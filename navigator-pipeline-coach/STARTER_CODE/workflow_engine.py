#!/usr/bin/env python3
"""
Workflow Engine Example for Navigator-Pipeline
Demonstrates advanced workflow orchestration with parallel execution.
"""

import asyncio
import uuid
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    name: str
    agent: str
    inputs: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    outputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowStage:
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    parallel: bool = False

@dataclass 
class Pipeline:
    id: str
    name: str
    stages: List[WorkflowStage] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

class AgentSimulator:
    """Simulates agent calls for demonstration."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def call(self, action: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate an agent call with realistic delay."""
        print(f"📞 Calling {self.name}.{action}")
        await asyncio.sleep(0.3)  # Simulate processing time
        
        # Return mock results based on agent type
        if self.name == "ingest":
            return self._mock_ingest_results(action)
        elif self.name == "strategy":
            return self._mock_strategy_results(action)
        else:
            return {"status": "success", "result": f"Mock result from {self.name}"}
    
    def _mock_ingest_results(self, action: str) -> Dict[str, Any]:
        if action == "rss_discovery":
            return {"episodes": ["AI Weekly #142", "Tech Trends Today"]}
        elif action == "transcription":
            return {"transcripts": ["Transcript 1", "Transcript 2"]}
        return {"status": "success"}
    
    def _mock_strategy_results(self, action: str) -> Dict[str, Any]:
        if action == "goal_alignment":
            return {"aligned_content": [{"episode": "AI Weekly", "score": 9.2}]}
        elif action == "insight_extraction":
            return {"insights": [{"title": "AI Investment Surge", "score": 9.1}]}
        return {"status": "success"}

class WorkflowEngine:
    """Advanced workflow engine with parallel execution capabilities."""
    
    def __init__(self):
        self.agents = {
            "ingest": AgentSimulator("ingest"),
            "strategy": AgentSimulator("strategy"), 
            "ui": AgentSimulator("ui")
        }
        self.pipelines: Dict[str, Pipeline] = {}
    
    def create_pipeline(self, name: str) -> Pipeline:
        """Create a new pipeline."""
        pipeline_id = str(uuid.uuid4())
        pipeline = Pipeline(id=pipeline_id, name=name)
        self.pipelines[pipeline_id] = pipeline
        return pipeline
    
    def add_parallel_stage(self, pipeline: Pipeline, stage_name: str) -> WorkflowStage:
        """Add a parallel execution stage to the pipeline."""
        stage_id = str(uuid.uuid4())
        stage = WorkflowStage(id=stage_id, name=stage_name, parallel=True)
        pipeline.stages.append(stage)
        return stage
    
    def add_stage(self, pipeline: Pipeline, stage_name: str) -> WorkflowStage:
        """Add a sequential execution stage to the pipeline."""
        stage_id = str(uuid.uuid4())
        stage = WorkflowStage(id=stage_id, name=stage_name, parallel=False)
        pipeline.stages.append(stage)
        return stage
    
    def add_task(self, stage: WorkflowStage, task_name: str, agent: str, 
                 inputs: Dict[str, Any]) -> Task:
        """Add a task to a stage."""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, name=task_name, agent=agent, inputs=inputs)
        stage.tasks.append(task)
        return task
    
    async def execute(self, pipeline: Pipeline, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline with parallel and sequential stages."""
        print(f"🚀 Starting pipeline: {pipeline.name}")
        pipeline.status = TaskStatus.RUNNING
        
        stage_results = {}
        
        for stage in pipeline.stages:
            print(f"📋 Executing stage: {stage.name} ({'parallel' if stage.parallel else 'sequential'})")
            
            if stage.parallel:
                # Execute all tasks in parallel
                tasks = []
                for task in stage.tasks:
                    agent = self.agents[task.agent]
                    task_coroutine = agent.call(task.name, {**inputs, **task.inputs})
                    tasks.append(task_coroutine)
                
                results = await asyncio.gather(*tasks)
                stage_results[stage.name] = results
                print(f"✅ Parallel stage completed with {len(results)} results")
                
            else:
                # Execute tasks sequentially
                results = []
                for task in stage.tasks:
                    print(f"  🔄 Executing task: {task.name}")
                    agent = self.agents[task.agent]
                    result = await agent.call(task.name, {**inputs, **task.inputs})
                    results.append(result)
                    task.status = TaskStatus.COMPLETED
                    task.outputs = result
                
                stage_results[stage.name] = results
                print(f"✅ Sequential stage completed")
        
        pipeline.status = TaskStatus.COMPLETED
        print(f"🎉 Pipeline completed: {pipeline.name}")
        
        return {
            "pipeline_id": pipeline.id,
            "status": "success",
            "stage_results": stage_results,
            "total_stages": len(pipeline.stages)
        }

# Example usage and demonstration
async def demo_basic_workflow():
    """Demonstrate a basic workflow with parallel and sequential stages."""
    print("🎯 Basic Workflow Demo")
    print("=" * 30)
    
    engine = WorkflowEngine()
    pipeline = engine.create_pipeline("content_analysis")
    
    # Stage 1: Parallel content acquisition
    content_stage = engine.add_parallel_stage(pipeline, "content_acquisition")
    engine.add_task(content_stage, "rss_discovery", "ingest", {"feeds": ["feed1", "feed2"]})
    engine.add_task(content_stage, "transcription", "ingest", {"audio": ["url1", "url2"]})
    
    # Stage 2: Sequential analysis
    analysis_stage = engine.add_stage(pipeline, "strategic_analysis")
    engine.add_task(analysis_stage, "goal_alignment", "strategy", {"goal": "AI trends"})
    engine.add_task(analysis_stage, "insight_extraction", "strategy", {"depth": "deep"})
    
    # Execute pipeline
    inputs = {"user_goal": "Identify AI investment opportunities"}
    results = await engine.execute(pipeline, inputs)
    
    print(f"\\n📊 Results: {results['status']}")
    print(f"📈 Stages completed: {results['total_stages']}")

async def demo_advanced_workflow():
    """Demonstrate a more complex workflow with error handling."""
    print("\\n🎯 Advanced Workflow Demo")
    print("=" * 30)
    
    engine = WorkflowEngine()
    pipeline = engine.create_pipeline("full_analysis_pipeline")
    
    # Stage 1: Content Discovery (Parallel)
    discovery_stage = engine.add_parallel_stage(pipeline, "discovery")
    engine.add_task(discovery_stage, "rss_discovery", "ingest", {"sources": 5})
    engine.add_task(discovery_stage, "trend_monitoring", "strategy", {"timeframe": "7d"})
    
    # Stage 2: Content Processing (Sequential for dependencies)
    processing_stage = engine.add_stage(pipeline, "processing")
    engine.add_task(processing_stage, "transcription", "ingest", {"quality": "high"})
    engine.add_task(processing_stage, "content_filtering", "strategy", {"relevance_threshold": 0.8})
    
    # Stage 3: Analysis (Parallel analysis types)
    analysis_stage = engine.add_parallel_stage(pipeline, "analysis")
    engine.add_task(analysis_stage, "sentiment_analysis", "strategy", {"model": "advanced"})
    engine.add_task(analysis_stage, "topic_extraction", "strategy", {"max_topics": 10})
    engine.add_task(analysis_stage, "goal_alignment", "strategy", {"scoring": "detailed"})
    
    # Stage 4: Results (Sequential for final output)
    results_stage = engine.add_stage(pipeline, "results")
    engine.add_task(results_stage, "insight_ranking", "strategy", {"algorithm": "hybrid"})
    engine.add_task(results_stage, "dashboard_update", "ui", {"format": "interactive"})
    
    # Execute with comprehensive inputs
    inputs = {
        "user_goal": "Track AI investment opportunities and regulatory changes",
        "priority_sources": ["TechCrunch", "a16z", "WSJ"],
        "analysis_depth": "comprehensive",
        "output_format": "executive_summary"
    }
    
    try:
        results = await engine.execute(pipeline, inputs)
        
        print(f"\\n🎉 Advanced pipeline completed!")
        print(f"📊 Status: {results['status']}")
        print(f"📈 Total stages: {results['total_stages']}")
        print(f"🔬 Analysis complete for goal: {inputs['user_goal']}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

if __name__ == "__main__":
    async def main():
        await demo_basic_workflow()
        await demo_advanced_workflow()
    
    asyncio.run(main()) 