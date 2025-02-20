# src/agent.py
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from typing import List, Dict
from src.retriever import DocumentRetriever

class ResearchAgent:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required!")
            
        self.retriever = DocumentRetriever()
        self.llm = ChatOpenAI(
            temperature=0,
            api_key=api_key,
            model="gpt-3.5-turbo"
        )
        
        self.tools = [
            Tool(
                name="Search_Documents",
                func=self.search_docs,
                description="Searches through documents to find relevant information"
            )
        ]
        
        # Updated prompt with specific format instructions
        prompt = PromptTemplate(
            template="""Answer the following question using the provided tools.

Available tools:
{tools}

Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Previous conversation:
{agent_scratchpad}

Question: {input}

Thought: Let me approach this step by step.""",
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Added handle_parsing_errors=True
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def search_docs(self, query: str) -> str:
        """Search documents for relevant information"""
        results = self.retriever.retrieve_relevant_docs(query)
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            return "\n".join(docs)
        return "No relevant documents found."

    def answer_question(self, question: str) -> str:
        """Answer questions using the agent"""
        try:
            response = self.agent_executor.invoke({"input": question})
            return response["output"]
        except Exception as e:
            return f"Error processing question: {str(e)}"