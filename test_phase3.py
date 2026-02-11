"""
Test Script - Verify Phase 3 Implementation

This script tests the ingestion system and workflow graph.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from graph.workflow import create_review_graph
from graph.state import create_initial_state

# Setup logger
logger = setup_logger(__name__, log_level="INFO")


def test_workflow_graph():
    """Test workflow graph creation."""
    logger.info("=" * 80)
    logger.info("🧪 Testing Workflow Graph Creation")
    logger.info("=" * 80)
    
    try:
        graph = create_review_graph()
        logger.info("✅ Workflow graph created successfully")
        
        # Try to visualize
        logger.info("\n📊 Attempting to visualize graph...")
        from graph.workflow import visualize_graph
        mermaid = visualize_graph()
        if mermaid:
            logger.info("✅ Graph visualization:")
            print(mermaid)
        
        return True
    except Exception as e:
        logger.error(f"❌ Workflow graph creation failed: {str(e)}", exc_info=True)
        return False


def test_ingestion_local():
    """Test ingestion with current directory."""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Local Directory Ingestion")
    logger.info("=" * 80)
    
    try:
        graph = create_review_graph()
        
        # Test with current directory
        initial_state = create_initial_state(
            input_path=".",
            output_dir="./test_output"
        )
        
        logger.info(f"📍 Testing with path: {initial_state['input_path']}")
        
        # Run workflow
        final_state = graph.invoke(initial_state)
        
        # Check results
        if final_state.get('error'):
            logger.error(f"❌ Workflow failed: {final_state['error']}")
            return False
        
        logger.info("\n✅ Workflow completed successfully!")
        logger.info(f"📊 Files found: {final_state.get('total_files', 0)}")
        logger.info(f"📁 Working directory: {final_state.get('working_directory', 'N/A')}")
        logger.info(f"🔐 Security findings: {len(final_state.get('security_findings', []))}")
        logger.info(f"⚡ Performance findings: {len(final_state.get('performance_findings', []))}")
        logger.info(f"✨ Style findings: {len(final_state.get('style_findings', []))}")
        
        # Show placeholder report
        if final_state.get('final_report'):
            logger.info("\n📋 Generated Report:")
            print(final_state['final_report'])
        
        return True
    except Exception as e:
        logger.error(f"❌ Ingestion test failed: {str(e)}", exc_info=True)
        return False


def test_static_tools():
    """Test static analysis tools."""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Static Analysis Tools")
    logger.info("=" * 80)
    
    try:
        from tools.bandit_tool import BanditScanner
        from tools.radon_tool import RadonAnalyzer
        
        # Test Bandit
        logger.info("\n🔒 Testing Bandit...")
        bandit = BanditScanner()
        
        # Test Radon
        logger.info("\n📊 Testing Radon...")
        radon = RadonAnalyzer()
        
        logger.info("✅ Static analysis tools initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Static tools test failed: {str(e)}", exc_info=True)
        return False


def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("🚀 Phase 3 Implementation Tests")
    logger.info("=" * 80)
    
    results = {
        'Workflow Graph': test_workflow_graph(),
        'Static Tools': test_static_tools(),
        'Local Ingestion': test_ingestion_local(),
    }
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 Test Results Summary")
    logger.info("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n🎉 All tests passed! Phase 3 is working correctly.")
    else:
        logger.info("\n⚠️ Some tests failed. Please review the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
