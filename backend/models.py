"""
Minimal Data Transfer Objects (DTOs) for API responses.

These models strip out unnecessary data to reduce payload sizes by ~40%.
Full objects are still stored in the database; these are for frontend display only.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Stage1ResponseMinimal(BaseModel):
    """Minimal Stage1 response for frontend display.
    
    Drops: usage, timing, raw API response details.
    Frontend only needs model name and response text.
    """
    model: str
    response: str


class Stage2RankingMinimal(BaseModel):
    """Minimal ranking entry for display.
    
    Drops: raw scores, detailed metadata.
    Frontend only needs rank, model, and reasoning.
    """
    rank: int
    model: str
    reasoning: str


class Stage2ResponseMinimal(BaseModel):
    """Minimal Stage2 response for frontend display.
    
    Simplifies rankings and aggregate data.
    """
    model: str
    rankings: List[Stage2RankingMinimal]
    aggregate_rankings: Optional[Dict[str, float]] = None


class Stage3ResponseMinimal(BaseModel):
    """Minimal Stage3 response for frontend display.
    
    Drops: usage, timing.
    Frontend only needs final synthesized response.
    """
    model: str
    response: str


class MessageResponseMinimal(BaseModel):
    """Lightweight message response optimized for frontend.
    
    Consolidates all timing/usage data into metadata instead of
    duplicating it in each stage response.
    """
    stage1: List[Stage1ResponseMinimal]
    stage2: List[Stage2ResponseMinimal]
    stage3: Stage3ResponseMinimal
    metadata: Dict[str, Any]


# ============================================================================
# Transformation Functions: Full Objects -> Minimal DTOs
# ============================================================================

def transform_stage1_to_minimal(stage1_full: List[Dict[str, Any]]) -> List[Stage1ResponseMinimal]:
    """Transform full Stage1 responses to minimal DTOs.
    
    Args:
        stage1_full: List of full stage1 response dicts with usage/timing
        
    Returns:
        List of minimal Stage1ResponseMinimal objects
    """
    minimal_responses = []
    
    for response in stage1_full:
        minimal_responses.append(Stage1ResponseMinimal(
            model=response.get("model", "unknown"),
            response=response.get("response", "")
        ))
    
    return minimal_responses


def transform_stage2_to_minimal(stage2_full: List[Dict[str, Any]]) -> List[Stage2ResponseMinimal]:
    """Transform full Stage2 responses to minimal DTOs.
    
    Args:
        stage2_full: List of full stage2 response dicts with detailed rankings
        
    Returns:
        List of minimal Stage2ResponseMinimal objects
    """
    minimal_responses = []
    
    for response in stage2_full:
        # Transform rankings
        rankings_full = response.get("rankings", [])
        minimal_rankings = [
            Stage2RankingMinimal(
                rank=r.get("rank", 0),
                model=r.get("model", "unknown"),
                reasoning=r.get("reasoning", "")
            )
            for r in rankings_full
        ]
        
        minimal_responses.append(Stage2ResponseMinimal(
            model=response.get("model", "unknown"),
            rankings=minimal_rankings,
            aggregate_rankings=response.get("aggregate_rankings")
        ))
    
    return minimal_responses


def transform_stage3_to_minimal(stage3_full: Dict[str, Any]) -> Stage3ResponseMinimal:
    """Transform full Stage3 response to minimal DTO.
    
    Args:
        stage3_full: Full stage3 response dict with usage/timing
        
    Returns:
        Minimal Stage3ResponseMinimal object
    """
    return Stage3ResponseMinimal(
        model=stage3_full.get("model", "unknown"),
        response=stage3_full.get("response", "")
    )


def transform_message_to_minimal(
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage3: Dict[str, Any],
    metadata: Dict[str, Any]
) -> MessageResponseMinimal:
    """Transform full message response to minimal DTO.
    
    Consolidates timing and usage data into metadata field.
    
    Args:
        stage1: Full stage1 responses
        stage2: Full stage2 responses
        stage3: Full stage3 response
        metadata: Metadata dict (already consolidated)
        
    Returns:
        Minimal MessageResponseMinimal object
    """
    # Transform each stage
    minimal_stage1 = transform_stage1_to_minimal(stage1)
    minimal_stage2 = transform_stage2_to_minimal(stage2)
    minimal_stage3 = transform_stage3_to_minimal(stage3)
    
    # Optionally enhance metadata with per-model timing if not already present
    # This moves individual model metrics out of responses into consolidated metadata
    if "model_timings" not in metadata and stage1:
        metadata["model_timings"] = {}
        for resp in stage1:
            if "timing" in resp:
                model_name = resp.get("model", "unknown")
                metadata["model_timings"][model_name] = resp["timing"]
    
    return MessageResponseMinimal(
        stage1=minimal_stage1,
        stage2=minimal_stage2,
        stage3=minimal_stage3,
        metadata=metadata
    )


def transform_conversation_messages_to_minimal(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform all messages in a conversation to use minimal DTOs.
    
    Used when fetching full conversation history.
    
    Args:
        messages: List of message dicts (user and assistant messages)
        
    Returns:
        List of messages with assistant messages using minimal DTOs
    """
    minimal_messages = []
    
    for msg in messages:
        # User messages stay as-is (already minimal)
        if msg.get("role") == "user":
            minimal_messages.append(msg)
            continue
        
        # Transform assistant messages
        if msg.get("role") == "assistant":
            # Check if stages exist
            if "stage1" in msg and "stage2" in msg and "stage3" in msg:
                transformed = {
                    "role": "assistant",
                    "stage1": [s.model_dump() for s in transform_stage1_to_minimal(msg["stage1"])],
                    "stage2": [s.model_dump() for s in transform_stage2_to_minimal(msg["stage2"])],
                    "stage3": transform_stage3_to_minimal(msg["stage3"]).model_dump(),
                    "metadata": msg.get("metadata", {})
                }
                minimal_messages.append(transformed)
            else:
                # Fallback for messages without stages
                minimal_messages.append(msg)
    
    return minimal_messages
