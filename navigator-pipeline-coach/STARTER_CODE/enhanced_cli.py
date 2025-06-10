#!/usr/bin/env python3
"""
Enhanced CLI Example for Navigator-Pipeline
Demonstrates smart command interface with validation, progress bars, and rich output.
"""

import click
import asyncio
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class AnalysisRequest:
    goal: str
    sources: List[str]
    format: str = "table"
    save_path: Optional[str] = None

class GoalValidator:
    """Validates and provides suggestions for strategic goals."""
    
    EXAMPLE_GOALS = [
        "Identify AI investment opportunities in Q4 2024",
        "Track blockchain regulation developments", 
        "Monitor cybersecurity threat trends",
        "Analyze fintech startup acquisition targets"
    ]
    
    @classmethod
    def validate(cls, goal: str) -> tuple[bool, str]:
        """Validate goal and return (is_valid, message)."""
        if len(goal) < 10:
            suggestion = cls.EXAMPLE_GOALS[0]
            return False, f"Goal too short. Try: '{suggestion}'"
        
        if not any(word in goal.lower() for word in ['identify', 'track', 'monitor', 'analyze']):
            return False, "Goal should include an action verb (identify, track, monitor, analyze)"
        
        return True, "Goal looks good!"

class WorkflowSimulator:
    """Simulates the workflow execution with progress indicators."""
    
    async def execute_analysis(self, request: AnalysisRequest) -> dict:
        """Execute analysis workflow with progress tracking."""
        
        # Simulate progress phases
        print("🔍 Discovering content...")
        await asyncio.sleep(0.3)
        
        print("🎤 Transcribing episodes...")
        await asyncio.sleep(0.5)
        
        print("🧠 Analyzing insights...")
        await asyncio.sleep(0.4)
        
        # Return mock results
        return {
            "goal": request.goal,
            "sources_analyzed": len(request.sources),
            "insights_found": 12,
            "relevance_score": 8.7,
            "processing_time": "1.2s",
            "insights": [
                {"title": "AI Investment Surge", "score": 9.2, "source": "TechCrunch AI"},
                {"title": "Regulatory Changes", "score": 8.5, "source": "WSJ Tech"},
                {"title": "Market Consolidation", "score": 8.1, "source": "Bloomberg Tech"}
            ]
        }

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """🚀 SpiceflowNavigator Pipeline CLI - Enhanced Edition"""
    pass

@cli.command()
@click.option('--goal', '-g', help='Strategic goal for analysis')
@click.option('--source', '-s', multiple=True, help='Content sources (RSS feeds, URLs)')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'table', 'summary']), 
              default='table',
              help='Output format')
@click.option('--save', '-o', help='Save results to file')
@click.option('--guided', is_flag=True, help='Interactive guided setup')
def analyze(goal: str, source: tuple, format: str, save: str, guided: bool):
    """Analyze content for strategic insights with guided setup."""
    
    if guided:
        goal, source = _interactive_setup()
    
    if not goal:
        print("❌ Goal is required. Use --goal or --guided")
        raise click.Abort()
    
    if not source:
        print("❌ At least one source is required. Use --source or --guided")
        raise click.Abort()
    
    # Validate goal
    is_valid, message = GoalValidator.validate(goal)
    if not is_valid:
        print(f"❌ {message}")
        raise click.Abort()
    
    print(f"✅ {message}")
    
    # Create request
    request = AnalysisRequest(
        goal=goal,
        sources=list(source),
        format=format,
        save_path=save
    )
    
    # Execute analysis
    results = asyncio.run(_execute_analysis_workflow(request))
    
    # Display results
    _display_results(results, format)
    
    if save:
        _save_results(results, save, format)
        print(f"📁 Results saved to {save}")

@cli.command()
def status():
    """Show system status and health."""
    
    print("🌐 SpiceflowNavigator System Status\\n")
    
    # Mock agent status data
    agents = [
        {"name": "Navigator-Ingest", "status": "UP", "latency": "245ms"},
        {"name": "Navigator-Strategy", "status": "UP", "latency": "180ms"},
        {"name": "Navigator-UI", "status": "SLOW", "latency": "2.1s"},
        {"name": "CommonUtils", "status": "UP", "latency": "50ms"}
    ]
    
    # Simple table display
    print(f"{'Agent':<20} {'Status':<10} {'Latency'}")
    print("-" * 40)
    
    for agent in agents:
        status_emoji = "✅" if agent["status"] == "UP" else "⚠️"
        print(f"{agent['name']:<20} {status_emoji} {agent['status']:<8} {agent['latency']}")
    
    print("\\n🔧 Active Jobs: 3 running, 12 completed, 0 failed")
    print("📈 Performance: avg 1.2s/analysis, 98.5% success rate")

def _interactive_setup() -> tuple[str, tuple]:
    """Interactive guided setup for new users."""
    print("🎯 Guided Analysis Setup")
    
    # Goal selection
    print("\\n📋 Choose your strategic goal:")
    for i, example in enumerate(GoalValidator.EXAMPLE_GOALS, 1):
        print(f"  {i}. {example}")
    print("  5. Enter custom goal")
    
    choice = click.prompt("Select option (1-5)", type=int, default=1)
    
    if choice <= 4:
        goal = GoalValidator.EXAMPLE_GOALS[choice - 1]
    else:
        goal = click.prompt("Enter your strategic goal")
    
    # Source selection  
    sources = ("rss://example.com/feed",)
    
    return goal, sources

async def _execute_analysis_workflow(request: AnalysisRequest) -> dict:
    """Execute the analysis workflow."""
    simulator = WorkflowSimulator()
    return await simulator.execute_analysis(request)

def _display_results(results: dict, format: str):
    """Display results in the specified format."""
    if format == "json":
        import json
        print(json.dumps(results, indent=2))
    
    elif format == "table":
        print(f"\\n🎯 Analysis Summary")
        print(f"Goal: {results['goal']}")
        print(f"Sources Analyzed: {results['sources_analyzed']}")
        print(f"Insights Found: {results['insights_found']}")
        print(f"Relevance Score: {results['relevance_score']}/10")
        print(f"Processing Time: {results['processing_time']}")
        
        print(f"\\n📈 Top Insights:")
        for insight in results["insights"]:
            print(f"- {insight['title']} ({insight['score']}/10) - {insight['source']}")
    
    elif format == "summary":
        print(f"\\n🎯 Analysis Complete for: {results['goal']}")
        print(f"📊 Found {results['insights_found']} insights")
        print(f"⭐ Overall relevance: {results['relevance_score']}/10")

def _save_results(results: dict, filepath: str, format: str):
    """Save results to file."""
    import json
    
    if format == "json":
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        with open(filepath, 'w') as f:
            f.write(f"SpiceflowNavigator Analysis Results\\n")
            f.write(f"Goal: {results['goal']}\\n")
            f.write(f"Insights Found: {results['insights_found']}\\n")

if __name__ == "__main__":
    cli() 