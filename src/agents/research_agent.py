"""
Research Agent for autonomous learning
Handles research tasks and knowledge acquisition
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Specialized agent for conducting research and acquiring knowledge
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.research_topics = []
        self.research_history = []
        self.current_research_focus = None
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a research task
        
        Args:
            task: Task description and parameters
            
        Returns:
            Research results
        """
        task_type = task.get("type", "research")
        
        if task_type == "research":
            return self.conduct_research(task)
        elif task_type == "update_knowledge":
            return self.update_knowledge(task)
        elif task_type == "analyze_trends":
            return self.analyze_trends(task)
        else:
            return {
                "success": False,
                "message": f"Unknown task type: {task_type}"
            }
    
    def conduct_research(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct research on a specific topic
        
        Args:
            task: Research task parameters
            
        Returns:
            Research findings
        """
        topic = task.get("topic")
        depth = task.get("depth", "medium")
        context = task.get("context", [])
        
        if not topic:
            return {
                "success": False,
                "message": "Topic is required for research"
            }
        
        # Create a more intelligent research prompt that can handle any type of query
        context_str = '\n'.join(context) if context else ''
        
        # Enhanced prompt with better instruction and flexibility for ANY topic
        prompt = f"""
        I want you to act as an expert AI educational assistant with comprehensive knowledge in all fields of study, technologies, skills, and courses. The user has requested information about: "{topic}"
        
        This could be a request for:
        1. A learning path on this topic or skill
        2. Specific research or information on this subject
        3. How to accomplish a task or learn a technique
        4. Explanations or definitions of concepts
        5. Course recommendations for a particular field
        6. Career advice related to skills or technologies
        7. Comparisons between different technologies, methods, or approaches
        
        YOUR GOAL: Provide the most helpful, accurate, and comprehensive information possible about ANY educational topic the user asks about. You should be able to address questions about programming languages, data science, machine learning, web development, mobile development, cloud computing, cybersecurity, design, business, humanities, sciences, mathematics, or any other educational subject.
        
        If it seems like they want a learning path:
        - Provide a step-by-step progression from basics to advanced
        - Include estimated time commitments for each stage
        - Recommend specific resources (books, courses, tutorials) for each step
        
        If it seems like they want specific information:
        - Provide detailed, technically accurate information
        - Include practical applications and examples
        - Balance theoretical knowledge with practical insights
        
        Your response should be thorough, accurate, helpful for any level of expertise, and include both theoretical understanding and practical application.
        
        Additional context:
        {context_str}
        
        Provide your findings in this JSON format:
        {{
            "summary": "A clear 2-3 paragraph summary answering the query directly, with specific details and actionable insights",
            "key_concepts": ["List of 4-6 key concepts relevant to the query, with brief explanations"],
            "learning_path": ["Detailed steps for learning this topic in a logical order, from beginner to advanced"],
            "resources": ["Specific recommended resources including books, courses, tutorials, documentation, and communities"],
            "code_examples": ["Relevant code examples or practical exercises that demonstrate key concepts"],
            "advanced_topics": ["More advanced topics to explore after mastering basics, with brief explanations of why they matter"],
            "career_applications": ["How these skills apply to real-world jobs and career paths"],
            "curiosity_trails": ["A list of 3-5 intriguing follow-up questions or related sub-topics to explore further, designed to spark curiosity and deeper learning."]
        }}
        
        For the "curiosity_trails", think about what someone who has just learned the main topic might wonder next, or what fascinating related areas they could branch into.
        
        Be extremely thorough, accurate, and helpful. Don't just provide general advice - give specific, actionable information that would genuinely help someone learn this topic or skill.  
        """
        
        # Generate research findings with error handling
        findings_json = self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "summary": "string",
                "key_concepts": ["string"],
                "learning_path": ["string"],
                "resources": ["string"],
                "code_examples": ["string"],
                "advanced_topics": ["string"],
                "career_applications": ["string"],
                "curiosity_trails": ["string"]
            }
            """
        )
        if not findings_json:
            return {
                "success": False,
                "message": "AI provider did not return a valid response. Please try again later."
            }
        try:
            findings = json.loads(findings_json)
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to parse AI response: {str(e)}",
                "raw_response": findings_json
            }
        
        # Store findings
        self.add_to_memory(f"Research findings on {topic}: {json.dumps(findings)}")
        self.research_history.append({
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "depth": depth,
            "findings": findings
        })
        
        return {
            "success": True,
            "findings": findings,
            "message": f"Successfully completed research on {topic}"
        }
    
    def update_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update knowledge based on new information
        
        Args:
            task: Update task parameters
            
        Returns:
            Update results
        """
        new_info = task.get("new_information")
        related_topics = task.get("related_topics", [])
        
        if not new_info:
            return {
                "success": False,
                "message": "New information is required for knowledge update"
            }
        
        # Analyze new information
        prompt = f"""
        Analyze this new information and update existing knowledge:
        {new_info}
        """
        
        # Include related topics
        related_topics = self._find_related_topics(new_info)
        if related_topics:
            related_topics_str = '\n'.join(related_topics)
            prompt += f"\n\nRelated topics to consider:\n{related_topics_str}"
        
        prompt += f"""
        Identify:
        1. What new knowledge should be added
        2. What existing knowledge should be updated
        3. What knowledge should be deprecated
        """
        
        analysis = json.loads(self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "new_knowledge": ["string"],
                "updated_knowledge": ["string"],
                "deprecated_knowledge": ["string"]
            }
            """
        ))
        
        # Update knowledge base
        self.add_to_memory(f"Knowledge update: {json.dumps(analysis)}")
        
        return {
            "success": True,
            "analysis": analysis,
            "message": "Knowledge base updated successfully"
        }
    
    def analyze_trends(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trends in a specific area
        
        Args:
            task: Trend analysis parameters
            
        Returns:
            Trend analysis results
        """
        area = task.get("area")
        timeframe = task.get("timeframe", "recent")
        context = task.get("context", [])
        
        if not area:
            return {
                "success": False,
                "message": "Area is required for trend analysis"
            }
        
        # Create analysis prompt
        prompt = f"""
        Analyze current trends in: {area}
        
        Timeframe: {timeframe}
        """
        
        # Add context if available
        if context:
            context_str = '\n'.join(context)
            prompt += f"\n\nContext:\n{context_str}"
        
        prompt += f"""
        Provide analysis in JSON format with:
        - Current trends
        - Emerging patterns
        - Predicted developments
        - Impact assessment
        """
        
        # Generate trend analysis
        analysis = json.loads(self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "current_trends": ["string"],
                "emerging_patterns": ["string"],
                "predicted_developments": ["string"],
                "impact": ["string"]
            }
            """
        ))
        
        # Store analysis
        self.add_to_memory(f"Trend analysis for {area}: {json.dumps(analysis)}")
        
        return {
            "success": True,
            "analysis": analysis,
            "message": f"Successfully analyzed trends in {area}"
        }
    
    def plan_next_research(self) -> Dict[str, Any]:
        """
        Plan next research task based on current knowledge
        
        Returns:
            Next research plan
        """
        # Get current knowledge gaps
        relevant_memories = self.get_relevant_memory("knowledge gaps")
        
        # Create planning prompt
        memory_summary = "\n".join(item["content"] for item in relevant_memories)
        prompt = f"""
        Based on current knowledge:
        {memory_summary}
        
        Identify:
        1. Most important knowledge gaps
        2. Areas requiring deeper research
        3. Emerging topics to explore
        
        Propose next research task with:
        - Topic
        - Research depth
        - Related topics
        """
        
        # Generate research plan
        plan = json.loads(self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "topic": "string",
                "depth": "string",
                "related_topics": ["string"],
                "reason": "string"
            }
            """
        ))
        
        # Store plan
        self.add_to_memory(f"Next research plan: {json.dumps(plan)}")
        
        return plan
