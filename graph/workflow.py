"""
LangGraph Workflow - Orchestration of Code Review Agents
"""

from typing import Dict
from langgraph.graph import StateGraph, END

from graph.state import ReviewState
from agents.ingestor import create_ingestor_node
from agents.security import create_security_agent_node
from agents.performance import create_performance_agent_node
from agents.style import create_style_agent_node
from agents.aggregator import create_aggregator_agent_node
from utils.logger import get_logger

logger = get_logger(__name__)


# Use real agent implementations
create_security_node = create_security_agent_node
create_performance_node = create_performance_agent_node
create_style_node = create_style_agent_node
create_aggregator_node = create_aggregator_agent_node


def should_continue_to_agents(state: Dict) -> str:
    """
    Conditional edge: Determine if we should continue to analysis agents.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name or END
    """
    # Check if ingestion failed
    if state.get('error'):
        logger.error(f"❌ Workflow stopping due to error: {state['error']}")
        return END
    
    # Check if we have files to analyze
    total_files = state.get('total_files', 0)
    if total_files == 0:
        logger.warning("⚠️ No files found to analyze")
        state['error'] = 'No files found to analyze'
        return END
    
    # Continue to parallel agent execution
    logger.info(f"✅ Proceeding to analysis with {total_files} files")
    return "continue"


def create_review_graph() -> StateGraph:
    """
    Create the LangGraph workflow for code review.
    
    Workflow structure:
    1. Ingestor (sequential) - ingest code from URL or local path
    2. Conditional check - proceed only if ingestion successful
    3. Security, Performance, Style agents (parallel) - analyze code
    4. Aggregator (sequential) - compile final report
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("🔧 Creating code review workflow graph")
    
    # Create state graph with ReviewState
    workflow = StateGraph(ReviewState)
    
    # Create node functions
    ingestor_node = create_ingestor_node()
    security_node = create_security_node()
    performance_node = create_performance_node()
    style_node = create_style_node()
    aggregator_node = create_aggregator_node()
    
    # Add nodes to graph
    workflow.add_node("ingestor", ingestor_node)
    workflow.add_node("security", security_node)
    workflow.add_node("performance", performance_node)
    workflow.add_node("style", style_node)
    workflow.add_node("aggregator", aggregator_node)
    
    # Set entry point
    workflow.set_entry_point("ingestor")
    
    # Add conditional edge after ingestor
    workflow.add_conditional_edges(
        "ingestor",
        should_continue_to_agents,
        {
            "continue": "security",  # Go to security (which triggers all parallel nodes)
            END: END
        }
    )
    
    # Parallel execution: All three agents start after ingestor
    # Since we route to "security" above, we need to also trigger the others
    # In LangGraph, we achieve parallelism by having multiple edges from the same source
    
    # From ingestor, we also trigger performance and style
    workflow.add_edge("ingestor", "performance")
    workflow.add_edge("ingestor", "style")
    
    # All three agents converge to aggregator
    workflow.add_edge("security", "aggregator")
    workflow.add_edge("performance", "aggregator")
    workflow.add_edge("style", "aggregator")
    
    # End after aggregator
    workflow.add_edge("aggregator", END)
    
    # Compile the graph
    logger.info("✅ Workflow graph created successfully")
    logger.info("   📍 Entry point: ingestor")
    logger.info("   🔀 Parallel nodes: security, performance, style")
    logger.info("   📊 Aggregator: final report compilation")
    
    return workflow.compile()


def visualize_graph():
    """
    Visualize the workflow graph (for debugging/documentation).
    
    Returns:
        Graph visualization (if available)
    """
    try:
        graph = create_review_graph()
        
        # Try to get mermaid representation
        if hasattr(graph, 'get_graph'):
            return graph.get_graph().draw_mermaid()
        else:
            logger.warning("⚠️ Graph visualization not available")
            return None
    except Exception as e:
        logger.error(f"❌ Failed to visualize graph: {str(e)}")
        return None
