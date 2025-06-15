"""
Autonomous Learning Agents module
Contains specialized agents for different learning tasks
"""
from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .teaching_agent import TeachingAgent

__all__ = ['BaseAgent', 'ResearchAgent', 'TeachingAgent']
