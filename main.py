"""
Automated Code Review Agent - CLI Entry Point

A production-ready Multi-Agent System built with LangGraph for automated code review.
"""

import click
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from utils.logger import setup_logger
from graph.workflow import create_review_graph

logger = setup_logger(__name__)


@click.command()
@click.option(
    "--path",
    required=True,
    type=str,
    help="Local directory path or GitHub repository URL to review",
)
@click.option(
    "--output",
    default="./code_reviews",
    type=str,
    help="Output directory for review reports",
)
@click.option(
    "--model",
    default=None,
    type=str,
    help="Gemini model to use (overrides .env)",
)
def main(path: str, output: str, model: str):
    """
    Automated Code Review Agent
    
    Reviews code from local directories or GitHub repositories using
    specialized AI agents for security, performance, and style analysis.
    """
    try:
        logger.info("=" * 80)
        logger.info("🚀 Starting Automated Code Review Agent")
        logger.info("=" * 80)
        
        # Validate API key if using Gemini
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        if provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raise ValueError(
                    "❌ GOOGLE_API_KEY not set. Please configure .env file with your API key."
                )
        elif provider == "ollama":
            logger.info("🤖 Using Ollama as LLM provider")
        else:
            raise ValueError(f"❌ Invalid LLM_PROVIDER: {provider}. Must be 'gemini' or 'ollama'")
        
        # Set model if provided
        if model:
            os.environ["GEMINI_MODEL"] = model
            logger.info(f"📝 Using model: {model}")
        
        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Output directory: {output_path.absolute()}")
        
        # Create and execute review graph
        logger.info(f"🔍 Analyzing: {path}")
        graph = create_review_graph()
        
        # Initial state
        initial_state = {
            "input_path": path,
            "output_dir": str(output_path.absolute()),
        }
        
        # Execute workflow
        final_state = graph.invoke(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            logger.error(f"❌ Review failed: {final_state['error']}")
            return
        
        # Success
        report_path = final_state.get("report_path")
        if report_path:
            logger.info("=" * 80)
            logger.info(f"✅ Review completed successfully!")
            logger.info(f"📋 Report generated: {report_path}")
            logger.info("=" * 80)
        else:
            logger.warning("⚠️ Review completed but no report path found")
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
