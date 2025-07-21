#!/usr/bin/env python3
"""
Trip Demo - Main demonstration script for Indra MVP

Shows the complete agent orchestration workflow with a travel planning example.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import indra
sys.path.insert(0, str(Path(__file__).parent.parent))

from indra.cli import run_workflow


def main():
    """Run the trip planning demo."""
    print("🌟 Indra MVP - Trip Planning Demo")
    print("=" * 50)
    
    # Demo prompt
    prompt = "Plan a 5-day trip to Paris with a budget of $3000"
    
    print(f"Demo Prompt: {prompt}")
    print()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Run the workflow
    success = run_workflow(
        prompt=prompt,
        output_dir="demo_results",
        timeout=30,
        api_key=api_key,
        verbose=True,
        keep_files=True
    )
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("Check the 'demo_results' directory for output files.")
    else:
        print("\n❌ Demo failed. Check the logs for details.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)