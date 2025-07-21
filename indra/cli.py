"""CLI Interface - Main orchestration."""

import sys
import argparse
from pathlib import Path
from openai import OpenAI
from .queen import Queen
from .router import Router
from .compiler import Compiler
from .utils import setup_logging, ensure_directories, get_api_key


def run_workflow(prompt: str, output_dir: str = "results") -> bool:
    """Execute the complete Indra workflow."""
    try:
        # Validate inputs
        if not prompt or not prompt.strip():
            print("❌ Error: Prompt cannot be empty")
            return False
        
        setup_logging()
        ensure_directories()
        Path(output_dir).mkdir(exist_ok=True)
        
        # Get API key
        api_key = get_api_key()
        if not api_key:
            print("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable")
            return False
        
        # Import workers to trigger registration
        from . import workers
        
        # Initialize components
        try:
            client = OpenAI(api_key=api_key)
            queen = Queen(client)
            router = Router()
            compiler = Compiler(results_dir=output_dir)
        except Exception as e:
            print(f"❌ Failed to initialize components: {e}")
            return False
        
        print(f"🤖 Processing: {prompt}")
        
        # Step 1: Generate tasks
        try:
            tasks = queen.generate_tasks(prompt)
            if not tasks:
                print("❌ No tasks generated from prompt")
                return False
            
            task_ids = [task.id for task in tasks]
            print(f"👑 Generated {len(tasks)} tasks")
        except Exception as e:
            print(f"❌ Task generation failed: {e}")
            return False
        
        # Step 2: Dispatch tasks
        try:
            router.dispatch_tasks(tasks)
            print(f"🚦 Dispatched tasks")
        except Exception as e:
            print(f"❌ Task dispatch failed: {e}")
            return False
        
        # Step 3: Wait for completion
        try:
            completed = router.wait_for_completion(task_ids)
            if not completed:
                print("⚠️  Some tasks timed out")
        except Exception as e:
            print(f"❌ Task execution failed: {e}")
            return False
        
        # Step 4: Compile results
        try:
            compiled_data = compiler.compile_results(task_ids)
            output_path = Path(output_dir) / "result.json"
            final_output = compiler.generate_final_output(compiled_data, prompt, str(output_path))
            
            print(f"✅ Results saved to {output_path}")
            print(f"📋 Completed {final_output['tasks_completed']} tasks")
        except Exception as e:
            print(f"❌ Result compilation failed: {e}")
            return False
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Indra MVP - AI Agent Orchestration")
    subparsers = parser.add_subparsers(dest="command")
    
    # Run command
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("prompt", help="User prompt to process")
    run_parser.add_argument("--out", default="results", help="Output directory")
    
    # Status command
    subparsers.add_parser("status")
    
    args = parser.parse_args()
    
    if args.command == "run":
        success = run_workflow(args.prompt, args.out)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        api_key = get_api_key()
        print("✅ API Key: Configured" if api_key else "❌ API Key: Missing")
        print("✅ System: Ready")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()