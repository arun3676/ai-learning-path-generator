"""
Learning path generation logic for the AI Learning Path Generator.
This module handles the creation and management of personalized learning paths.
"""
import datetime
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError, validator

from src.data.document_store import DocumentStore
from src.ml.model_orchestrator import ModelOrchestrator
from src.ml.job_market import get_job_market_stats
from src.utils.config import (
    DEFAULT_REGION,
    EXPERTISE_LEVELS,
    LEARNING_STYLES,
    PERPLEXITY_API_KEY,
    TIME_COMMITMENTS,
)
from src.utils.helpers import (
    calculate_study_schedule,
    difficulty_to_score,
    match_resources_to_learning_style,
)


class ResourceItem(BaseModel):
    """A single learning resource."""

    type: str = Field(description="Type of the resource (e.g., article, video, book)")
    url: str = Field(description="URL of the resource")
    description: str = Field(description="Brief description of the resource")


class JobMarketData(BaseModel):
    """Job market data for a skill or role."""

    open_positions: Optional[str] = Field(
        description="Estimated number of open positions for this role/skill.",
        default="N/A",
    )
    trending_employers: Optional[List[str]] = Field(
        description="List of companies currently hiring for this role/skill.",
        default_factory=list,
    )
    average_salary: Optional[str] = Field(
        description="Estimated average salary range for this role/skill.", default="N/A"
    )
    related_roles: Optional[List[str]] = Field(
        description="Related job titles or roles for this skill/role.",
        default_factory=list,
    )
    demand_score: Optional[int] = Field(
        description="Demand score (0-100) for how hot this skill is right now", default=0
    )
    region: Optional[str] = Field(
        description="Region for which these stats apply", default=None
    )
    error: Optional[str] = Field(
        description="Error message if data could not be fetched.", default=None
    )


class Milestone(BaseModel):
    """A milestone in a learning path."""

    title: str = Field(description="Short title for the milestone")
    description: str = Field(description="Detailed description of what will be learned")
    estimated_hours: int = Field(
        description="Estimated hours to complete this milestone"
    )
    resources: List[ResourceItem] = Field(description="Recommended learning resources")
    skills_gained: List[str] = Field(
        description="Skills gained after completing this milestone"
    )
    job_market_data: JobMarketData = Field(
        description="Job market data for the skills gained",
        default_factory=JobMarketData,
    )

    @validator("resources", pre=True, always=True)
    def check_resources_not_empty(cls, v):
        if not v:
            # Instead of raising an error, provide a default resource
            return [
                ResourceItem(
                    type="article",
                    url="https://example.com/default-resource",
                    description="Default resource - Please explore additional materials for this milestone",
                )
            ]
        return v


class LearningPath(BaseModel):
    """Model representation of a learning path."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(description="Title of the learning path")
    description: str = Field(description="Detailed description of the learning path")
    topic: str = Field(description="Main topic of study")
    expertise_level: str = Field(description="Starting expertise level")
    learning_style: str = Field(description="Preferred learning style")
    time_commitment: str = Field(description="Weekly time commitment")
    duration_weeks: Optional[int] = Field(
        description="Total duration in weeks", default=0
    )
    goals: List[str] = Field(description="Learning goals and objectives")
    milestones: List["Milestone"] = Field(description="Weekly or modular breakdown")
    schedule: Optional[Dict[str, Any]] = Field(
        default=None, description="The calculated study schedule"
    )
    prerequisites: List[str] = Field(description="Prerequisites for this path")
    total_hours: int = Field(description="Total estimated hours")
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

    @validator("goals", pre=True, always=True)
    def check_goals_not_empty(cls, v):
        if not v:
            raise ValueError("Learning path goals list cannot be empty")
        # Ensure all goals are non-empty strings
        if not all(isinstance(goal, str) and goal.strip() for goal in v):
            raise ValueError("All goals must be non-empty strings")
        return v

    @validator("milestones", pre=True, always=True)
    def check_milestones_not_empty(cls, v):
        if not v:
            raise ValueError("Learning path milestones list cannot be empty")
        return v


class LearningPathGenerator:
    """
    Core class responsible for generating personalized learning paths.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the learning path generator.

        Args:
            api_key: Optional OpenAI API key (if not provided in environment)
        """
        self.model_orchestrator = ModelOrchestrator(api_key)
        self.document_store = DocumentStore()
        self.output_parser = PydanticOutputParser(pydantic_object=LearningPath)

    def fetch_job_market_data(
        self,
        skill_or_role: str,
        region: Optional[str] = None,
    ) -> JobMarketData:
        """
        Fetch job market data for a given skill or role using an LLM.

        Args:
            skill_or_role: The skill or role to query job market data for.
            region: The region to query job market data for (default is DEFAULT_REGION).

        Returns:
            A JobMarketData object containing job market statistics.
        """
        try:
            stats = get_job_market_stats(skill_or_role)
            return JobMarketData(**stats, region=region or DEFAULT_REGION)
        except Exception as e:
            # Fallback to default snapshot packaged in helper
            fallback = get_job_market_stats("__fallback__")  # returns default
            return JobMarketData(**fallback, region=region or DEFAULT_REGION, error=str(e))

    def fetch_related_roles(
        self, skills: List[str], ai_provider: Optional[str] = None, ai_model: Optional[str] = None
    ) -> List[str]:
        """
        Fetch related job roles for a given list of skills using an LLM.

        Args:
            skills: The list of skills to find related job roles for.
            ai_provider: The AI provider to use (e.g., 'openai', 'perplexity').
            ai_model: The specific AI model to use.

        Returns:
            A list of related job role titles.
        """
        if not skills:
            return []

        skills_str = ", ".join(skills)
        prompt = f"""
        Based on the following skills: {skills_str}, what are some relevant job titles or roles that utilize these skills?
        Please provide a list of job titles. Return the answer as a JSON array of strings.
        For example: ["Data Scientist", "Machine Learning Engineer", "Business Analyst"]
        """

        try:
            # Use the main model orchestrator to get the response
            response_str = self.model_orchestrator.get_response(
                prompt, provider=ai_provider, model=ai_model
            )

            # The response is expected to be a JSON string of a list
            roles = json.loads(response_str)
            if isinstance(roles, list):
                return roles
            return []
        except json.JSONDecodeError:
            # Fallback if the response is not valid JSON
            # Attempt to parse a plain list from the string
            if "[" in response_str and "]" in response_str:
                try:
                    # Extract content between brackets and split by comma
                    roles_str = response_str[response_str.find('[')+1:response_str.rfind(']')]
                    return [role.strip().strip('"\'') for role in roles_str.split(',')]
                except Exception:
                    return ["Could not parse roles"]
            return ["Could not determine roles"]
        except Exception as e:
            print(f"An unexpected error occurred while fetching related roles: {e}")
            return []

    def generate_path(
        self,
        topic: str,
        expertise_level: str,
        learning_style: str,
        time_commitment: str = "moderate",
        goals: List[str] = None,
        additional_info: Optional[str] = None,
        context: List[str] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
    ) -> LearningPath:
        """
        Generate a personalized learning path based on user preferences.

        Args:
            topic: The main topic of study
            expertise_level: Starting level of expertise
            learning_style: Preferred learning style
            time_commitment: Weekly time commitment
            goals: List of learning goals
            additional_info: Any additional information or constraints

        Returns:
            A complete learning path object
        """
        if goals is None:
            goals = [f"Master {topic}", f"Build practical skills in {topic}"]

        if expertise_level not in EXPERTISE_LEVELS:
            raise ValueError(
                f"Invalid expertise level. Choose from: {', '.join(EXPERTISE_LEVELS.keys())}"
            )

        if learning_style not in LEARNING_STYLES:
            raise ValueError(
                f"Invalid learning style. Choose from: {', '.join(LEARNING_STYLES.keys())}"
            )

        if time_commitment not in TIME_COMMITMENTS:
            raise ValueError(
                f"Invalid time commitment. Choose from: {', '.join(TIME_COMMITMENTS.keys())}"
            )

        relevant_docs = self.document_store.search_documents(
            query=topic, filters={"expertise_level": expertise_level}, top_k=10
        )

        hours_map = {"minimal": 2, "moderate": 5, "substantial": 8, "intensive": 15}
        hours_per_week = hours_map.get(time_commitment, 5)

        base_duration = 8
        intensity_factor = {
            "minimal": 2.0,
            "moderate": 1.5,
            "substantial": 1.0,
            "intensive": 0.75,
        }
        complexity_factor = {
            "beginner": 1.0,
            "intermediate": 1.2,
            "advanced": 1.5,
            "expert": 2.0,
        }

        adjusted_duration = int(
            base_duration
            * intensity_factor.get(time_commitment, 1.0)
            * complexity_factor.get(expertise_level, 1.0)
        )

        prompt_content = f"""
        Generate a detailed personalized learning path for the following:

        Topic: {topic}
        Expertise Level: {expertise_level} - {EXPERTISE_LEVELS[expertise_level]}
        Learning Style: {learning_style} - {LEARNING_STYLES[learning_style]}
        Time Commitment: {time_commitment} - {TIME_COMMITMENTS[time_commitment]}
        Learning Goals: {', '.join(goals)}
        Additional Information: {additional_info or 'None provided'}

        The learning path should include:
        1. A comprehensive description of the path
        2. 3-7 learning milestones that represent major stages of progress
        3. For each milestone, provide specific resources tailored to the {learning_style} learning style
        4. Each milestone should include estimated hours and skills gained
        5. List any prerequisites for starting this learning path

        Response should match the LearningPath schema.
        """

        prompt_with_context = prompt_content
        if context:
            context_text = "\n\nAdditional Context:\n" + "\n".join(context)
            prompt_with_context += context_text

        orchestrator_to_use = self.model_orchestrator
        if ai_provider:
            custom_orchestrator = ModelOrchestrator(provider=ai_provider)
            custom_orchestrator.init_language_model(model_name=ai_model)
            orchestrator_to_use = custom_orchestrator

        # Attempt up to 3 times to get a valid LearningPath JSON
        parsed_successfully = False
        last_error: Optional[Exception] = None
        for attempt in range(3):
            if attempt > 0:
                print(f"Retrying learning path generation (attempt {attempt+1}) due to previous validation failure…")
            response = orchestrator_to_use.generate_structured_response(
                prompt=prompt_with_context,
                output_schema=self.output_parser.get_format_instructions(),
                relevant_documents=(
                    [doc.page_content for doc in relevant_docs] if relevant_docs else None
                ),
                temperature=0.6 + 0.1 * attempt,  # vary temperature slightly on retries
            )
            try:
                learning_path: LearningPath = self.output_parser.parse(response)
                parsed_successfully = True
                break
            except ValidationError as ve:
                print("Validation failed when parsing AI response as LearningPath:", ve)
                print("Offending response:\n", response)
                last_error = ve
                # Slightly tweak the prompt for the next attempt
                prompt_with_context += (
                    "\n\nIMPORTANT: Your last response did NOT match the schema and was therefore rejected. "
                    "You MUST return a COMPLETE JSON object that follows the exact LearningPath schema with ALL required fields."
                )
            except Exception as e:
                print("Unexpected error while parsing AI response:", e)
                print("Offending response:\n", response)
                last_error = e
                break  # Unexpected errors – don't retry further

        if not parsed_successfully:
            raise RuntimeError("LearningPath generation failed after 3 attempts") from last_error

        for milestone in learning_path.milestones:
            if milestone.skills_gained:
                skill_or_role_raw = milestone.skills_gained
                if isinstance(skill_or_role_raw, list) and skill_or_role_raw:
                    skill_or_role = str(skill_or_role_raw[0])
                elif isinstance(skill_or_role_raw, str):
                    skill_or_role = skill_or_role_raw
                else:
                    skill_or_role = "general skill"

                milestone.job_market_data = self.fetch_job_market_data(skill_or_role)
                related_roles = self.fetch_related_roles(
                    milestone.skills_gained, ai_provider=ai_provider, ai_model=ai_model
                )
                milestone.job_market_data.related_roles = related_roles

        topic_weights = {
            milestone.title: milestone.estimated_hours
            for milestone in learning_path.milestones
        }

        schedule = calculate_study_schedule(
            weeks=adjusted_duration,
            hours_per_week=hours_per_week,
            topic_weights=topic_weights,
        )
        learning_path.schedule = schedule

        for milestone in learning_path.milestones:
            milestone.resources = match_resources_to_learning_style(
                resources=milestone.resources, learning_style=learning_style
            )

        learning_path.total_hours = sum(
            m.estimated_hours for m in learning_path.milestones if m.estimated_hours
        )
        learning_path.duration_weeks = adjusted_duration
        learning_path.id = str(uuid.uuid4())

        return learning_path

    def save_path(
        self, learning_path: LearningPath, output_dir: str = "learning_paths"
    ) -> str:
        """
        Save a learning path to file.

        Args:
            learning_path (LearningPath): The learning path to save.
            output_dir (str, optional): Directory to save the path. Defaults to "learning_paths".

        Returns:
            str: Path to the saved file.
        """
        path_dir = Path(output_dir)
        path_dir.mkdir(exist_ok=True, parents=True)

        safe_topic = learning_path.topic.lower().replace(" ", "_")[:30]
        filename = f"{safe_topic}_{learning_path.id[:8]}.json"
        file_path = path_dir / filename

        with open(file_path, "w") as f:
            f.write(json.dumps(learning_path.dict(), indent=2))

        return str(file_path)

    def load_path(
        self, path_id: str, input_dir: str = "learning_paths"
    ) -> Optional[LearningPath]:
        """
        Load a learning path from file by ID.

        Args:
            path_id (str): ID of the learning path to load.
            input_dir (str, optional): Directory to search for the path. Defaults to "learning_paths".

        Returns:
            Optional[LearningPath]: The loaded learning path or None if not found.
        """
        path_dir = Path(input_dir)
        if not path_dir.exists():
            return None

        for file_path in path_dir.glob(f"*_{path_id[:8]}.json"):
            try:
                with open(file_path, "r") as f:
                    path_data = json.load(f)
                    if path_data.get("id", "").startswith(path_id):
                        return LearningPath(**path_data)
            except Exception:
                continue

        return None
