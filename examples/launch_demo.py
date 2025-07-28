#!/usr/bin/env python3
"""
Launch Demo - Alternative demonstration launcher for Indra MVP

Provides an interactive demo experience with multiple example prompts.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import indra
sys.path.insert(0, str(Path(__file__).parent.parent))

from indra.cli import run_workflow


def print_banner():
    """Print the demo banner."""
    print("🌟" * 25)
    print("🚀 INDRA MVP - AI AGENT ORCHESTRATION")
    print("🌟" * 25)
    print()
    print("Welcome to the Indra MVP demonstration!")
    print("This will show you how AI agents work together to solve complex tasks.")
    print()


def get_demo_prompts():
    """Get a list of demo prompts to choose from."""
    return [
        {
            "title": "🏖️  Weekend Trip Planning",
            "prompt": "Plan a 3-day weekend trip to San Francisco with a $1500 budget",
            "description": "Travel planning with budget analysis"
        },
        {
            "title": "🌍 Multi-City European Tour", 
            "prompt": "Plan a 10-day trip visiting Paris, Rome, and Barcelona with a $4000 budget",
            "description": "Complex multi-destination travel planning"
        },
        {
            "title": "💰 Budget Analysis",
            "prompt": "Calculate the cost breakdown for a family of 4 visiting Disney World for 5 days",
            "description": "Detailed financial planning and cost estimation"
        },
        {
            "title": "✈️  Business Travel",
            "prompt": "Find flights and hotels for a 2-day business trip to New York next week",
            "description": "Quick business travel arrangements"
        },
        {
            "title": "🎒 Backpacking Adventure",
            "prompt": "Plan a 2-week backpacking trip through Southeast Asia with a $2000 budget",
            "description": "Budget travel planning with multiple destinations"
        },
        {
            "title": "🏔️  Custom Prompt",
            "prompt": "",
            "description": "Enter your own travel planning prompt"
        }
    ]


def select_demo():
    """Let user select a demo to run."""
    prompts = get_demo_prompts()
    
    print("📋 Available Demonstrations:")
    print("-" * 50)
    
    for i, demo in enumerate(prompts, 1):
        print(f"{i}. {demo['title']}")
        print(f"   {demo['description']}")
        print()
    
    while True:
        try:
            choice = input("Select a demo (1-{}): ".format(len(prompts)))
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(prompts):
                selected = prompts[choice_num - 1]
                
                if selected['title'] == "🏔️  Custom Prompt":
                    custom_prompt = input("\nEnter your travel planning prompt: ").strip()
                    if custom_prompt:
                        selected['prompt'] = custom_prompt
                    else:
                        print("❌ Empty prompt. Please try again.")
                        continue
                
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(prompts)}")
                
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Demo cancelled by user")
            return None


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found!")
        print()
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("You can get an API key from: https://platform.openai.com/api-keys")
        return False
    
    print("✅ OpenAI API key found")
    
    # Check imports
    try:
        import indra
        print("✅ Indra package available")
    except ImportError as e:
        print(f"❌ Indra package not available: {e}")
        print("Please run: pip install -e .")
        return False
    
    print("✅ All prerequisites met!")
    print()
    return True


def run_demo(demo_config):
    """Run the selected demo."""
    print(f"🚀 Running Demo: {demo_config['title']}")
    print("-" * 60)
    print(f"Prompt: {demo_config['prompt']}")
    print()
    
    # Confirm execution
    confirm = input("Press Enter to start the demo (or 'q' to quit): ").strip().lower()
    if confirm == 'q':
        print("👋 Demo cancelled")
        return False
    
    print("\n🎬 Starting demonstration...")
    print("=" * 60)
    
    # Run the workflow
    success = run_workflow(
        prompt=demo_config['prompt'],
        output_dir="demo_results"
    )
    
    print("=" * 60)
    
    if success:
        print("🎉 Demo completed successfully!")
        print()
        print("📁 Results saved to: demo_results/")
        print("📊 Check the generated files for detailed output")
        print()
        
        # Show result files
        results_dir = Path("demo_results")
        if results_dir.exists():
            result_files = list(results_dir.glob("*.json"))
            readable_files = list(results_dir.glob("*_readable.txt"))
            
            if result_files:
                print("📄 Generated files:")
                for file in result_files:
                    print(f"   • {file.name}")
                for file in readable_files:
                    print(f"   • {file.name}")
    else:
        print("❌ Demo failed. Check the logs for details.")
        print("💡 Try running with a simpler prompt or check your API key.")
    
    return success


def show_next_steps():
    """Show what users can do next."""
    print("\n🎯 What's Next?")
    print("-" * 30)
    print("1. 🔧 Try the CLI directly:")
    print('   indra run "Your custom prompt here"')
    print()
    print("2. 📚 Read the documentation:")
    print("   Check README.md for detailed usage instructions")
    print()
    print("3. 🛠️  Extend the system:")
    print("   Add your own workers in indra/workers/")
    print()
    print("4. 🧪 Run tests:")
    print("   python test_framework.py")
    print()
    print("5. 📊 Check system status:")
    print("   indra status")


def main():
    """Main demo launcher."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    try:
        # Select demo
        demo_config = select_demo()
        if not demo_config:
            return False
        
        # Run demo
        success = run_demo(demo_config)
        
        # Show next steps
        show_next_steps()
        
        return success
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)