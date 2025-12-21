"""CrewAI-powered multi-agent council deliberation system."""

from typing import List, Dict, Any, Tuple
from crewai import Agent, Task, Crew, Process
from crewai import LLM
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL, OPENROUTER_API_KEY, OPENROUTER_API_URL
import os


def create_openrouter_llm(model: str) -> LLM:
    """
    Create a CrewAI LLM instance configured for OpenRouter.
    
    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        
    Returns:
        LLM instance configured for OpenRouter
    """
    # Set environment variable for LiteLLM to use OpenRouter
    os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY
    
    # LiteLLM format: openrouter/provider/model
    # OpenRouter model format: provider/model
    return LLM(
        model=f"openrouter/{model}",
        temperature=0.7,
    )


def create_council_agents() -> List[Agent]:
    """
    Create specialized agents for each council member.
    
    Returns:
        List of CrewAI Agent objects
    """
    agents = []
    
    roles = [
        {
            "role": "Technical Analyst",
            "goal": "Provide technically accurate and detailed responses",
            "backstory": "You are an expert at breaking down complex technical concepts and providing precise, well-researched answers.",
        },
        {
            "role": "Critical Evaluator", 
            "goal": "Identify strengths and weaknesses in reasoning",
            "backstory": "You excel at logical analysis, spotting flaws in arguments, and evaluating the quality of explanations.",
        },
        {
            "role": "Practical Advisor",
            "goal": "Focus on actionable insights and real-world applications",
            "backstory": "You prioritize practical solutions and ensure answers are useful in real-world scenarios.",
        },
        {
            "role": "Comprehensive Synthesizer",
            "goal": "Combine multiple perspectives into cohesive answers",
            "backstory": "You are skilled at integrating diverse viewpoints and creating balanced, comprehensive responses.",
        },
    ]
    
    for i, config in enumerate(roles[:len(COUNCIL_MODELS)]):
        # Use OpenRouter LLM for each agent
        llm = create_openrouter_llm(COUNCIL_MODELS[i])
        
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
        agents.append(agent)
    
    return agents


def create_chairman_agent() -> Agent:
    """
    Create the chairman agent who synthesizes the final response.
    
    Returns:
        CrewAI Agent object for the chairman
    """
    llm = create_openrouter_llm(CHAIRMAN_MODEL)
    
    return Agent(
        role="Council Chairman",
        goal="Synthesize collective wisdom into a definitive answer",
        backstory="""You are the Chairman of an elite AI council. Your role is to:
        1. Consider all perspectives from council members
        2. Identify areas of consensus and disagreement
        3. Synthesize a comprehensive, balanced final answer
        4. Ensure the response is clear, accurate, and actionable""",
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )


async def crew_stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Use CrewAI agents to collect individual responses.
    
    Args:
        user_query: The user's question
        
    Returns:
        List of dicts with 'model', 'role', and 'response' keys
    """
    agents = create_council_agents()
    tasks = []
    
    # Create a task for each agent to respond to the query
    for i, agent in enumerate(agents):
        task = Task(
            description=f"""Answer the following question from your unique perspective as {agent.role}:

Question: {user_query}

Provide a thorough, well-reasoned response that reflects your specialized expertise.""",
            agent=agent,
            expected_output="A comprehensive answer to the user's question",
        )
        tasks.append(task)
    
    # Create crew with parallel execution
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,  # Each agent works independently
        verbose=True,
    )
    
    # Execute the crew
    result = crew.kickoff()
    
    # Format results
    stage1_results = []
    for i, agent in enumerate(agents):
        stage1_results.append({
            "model": COUNCIL_MODELS[i],
            "role": agent.role,
            "response": tasks[i].output.raw_output if hasattr(tasks[i], 'output') else str(result),
        })
    
    return stage1_results


async def crew_stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Use CrewAI agents to rank anonymized responses.
    
    Args:
        user_query: The original user query
        stage1_results: Results from Stage 1
        
    Returns:
        Tuple of (rankings list, label_to_model mapping)
    """
    agents = create_council_agents()
    
    # Create anonymized labels
    labels = [chr(65 + i) for i in range(len(stage1_results))]
    label_to_model = {
        f"Response {label}": result['model']
        for label, result in zip(labels, stage1_results)
    }
    
    # Build ranking prompt
    responses_text = "\n\n".join([
        f"Response {label} (by {result['role']}):\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])
    
    ranking_prompt = f"""Evaluate and rank the following responses to this question:

Question: {user_query}

Responses:
{responses_text}

Your task:
1. Evaluate each response's strengths and weaknesses
2. Provide a final ranking from best to worst

Format your final ranking as:
FINAL RANKING:
1. Response X
2. Response Y
3. Response Z"""
    
    tasks = []
    for agent in agents:
        task = Task(
            description=ranking_prompt,
            agent=agent,
            expected_output="Evaluation and ranking of all responses",
        )
        tasks.append(task)
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew.kickoff()
    
    # Format results
    stage2_results = []
    for i, agent in enumerate(agents):
        full_text = tasks[i].output.raw_output if hasattr(tasks[i], 'output') else str(result)
        stage2_results.append({
            "model": COUNCIL_MODELS[i],
            "role": agent.role,
            "ranking": full_text,
        })
    
    return stage2_results, label_to_model


async def crew_stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response using CrewAI.
    
    Args:
        user_query: The original user query
        stage1_results: Individual responses from Stage 1
        stage2_results: Rankings from Stage 2
        
    Returns:
        Dict with 'model', 'role', and 'response' keys
    """
    chairman = create_chairman_agent()
    
    # Build comprehensive context
    stage1_text = "\n\n".join([
        f"Model: {result['model']} ({result['role']})\nResponse: {result['response']}"
        for result in stage1_results
    ])
    
    stage2_text = "\n\n".join([
        f"Model: {result['model']} ({result['role']})\nRanking: {result['ranking']}"
        for result in stage2_results
    ])
    
    synthesis_task = Task(
        description=f"""As Council Chairman, synthesize the final answer to this question:

Question: {user_query}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task:
1. Analyze all responses and rankings
2. Identify consensus and key insights
3. Resolve any contradictions
4. Provide a comprehensive, authoritative final answer that represents the council's collective wisdom

The final answer should be clear, well-structured, and actionable.""",
        agent=chairman,
        expected_output="A synthesized final answer incorporating all council perspectives",
    )
    
    crew = Crew(
        agents=[chairman],
        tasks=[synthesis_task],
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew.kickoff()
    
    return {
        "model": CHAIRMAN_MODEL,
        "role": "Council Chairman",
        "response": synthesis_task.output.raw_output if hasattr(synthesis_task, 'output') else str(result),
    }


async def run_crew_council_deliberation(user_query: str) -> Dict[str, Any]:
    """
    Run the complete CrewAI-powered 3-stage council deliberation.
    
    Args:
        user_query: The user's question
        
    Returns:
        Dict containing all three stages of results
    """
    # Stage 1: Collect individual responses
    stage1_results = await crew_stage1_collect_responses(user_query)
    
    # Stage 2: Collect rankings
    stage2_results, label_to_model = await crew_stage2_collect_rankings(
        user_query, stage1_results
    )
    
    # Stage 3: Synthesize final response
    stage3_result = await crew_stage3_synthesize_final(
        user_query, stage1_results, stage2_results
    )
    
    return {
        "stage1": stage1_results,
        "stage2": stage2_results,
        "stage3": stage3_result,
        "metadata": {
            "labelToModel": label_to_model,
            "framework": "crewai",
        }
    }
