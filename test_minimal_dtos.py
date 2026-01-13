"""
Quick validation script for minimal DTOs.
Tests transformation functions and size reduction.
"""

import sys
import json
from backend.models import (
    transform_stage1_to_minimal,
    transform_stage2_to_minimal,
    transform_stage3_to_minimal,
    transform_message_to_minimal
)


def test_transformations():
    """Test the transformation functions work correctly."""
    
    # Sample full stage1 response
    stage1_full = [
        {
            "model": "anthropic/claude-3.5-sonnet",
            "response": "This is a test response from Claude.",
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "timing": 1.2
        },
        {
            "model": "openai/gpt-4",
            "response": "This is a test response from GPT-4.",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
            "timing": 1.8
        }
    ]
    
    # Sample full stage2 response
    stage2_full = [
        {
            "model": "anthropic/claude-3.5-sonnet",
            "rankings": [
                {"rank": 1, "model": "openai/gpt-4", "reasoning": "Most comprehensive"},
                {"rank": 2, "model": "anthropic/claude-3.5-sonnet", "reasoning": "Good detail"}
            ],
            "aggregate_rankings": {"gpt-4": 1.5, "claude": 2.0}
        }
    ]
    
    # Sample full stage3 response
    stage3_full = {
        "model": "anthropic/claude-3.5-sonnet",
        "response": "Final synthesized response combining all inputs.",
        "usage": {"input_tokens": 500, "output_tokens": 100},
        "timing": 2.1
    }
    
    # Sample metadata
    metadata = {
        "total_time": 5.1,
        "stage_times": {"stage1": 2.0, "stage2": 1.5, "stage3": 1.6}
    }
    
    print("="*60)
    print(" Testing Minimal DTO Transformations")
    print("="*60)
    
    # Test Stage1 transformation
    print("\n1. Testing Stage1 transformation...")
    minimal_stage1 = transform_stage1_to_minimal(stage1_full)
    print(f"   ✓ Transformed {len(stage1_full)} stage1 responses")
    print(f"   Original size: {len(json.dumps(stage1_full))} bytes")
    minimal_stage1_dict = [s.dict() for s in minimal_stage1]
    print(f"   Minimal size:  {len(json.dumps(minimal_stage1_dict))} bytes")
    reduction_stage1 = (1 - len(json.dumps(minimal_stage1_dict)) / len(json.dumps(stage1_full))) * 100
    print(f"   Reduction:     {reduction_stage1:.1f}%")
    
    # Verify data integrity
    assert minimal_stage1[0].model == "anthropic/claude-3.5-sonnet"
    assert "test response" in minimal_stage1[0].response
    assert not hasattr(minimal_stage1[0], 'usage')
    print("   ✓ Data integrity verified")
    
    # Test Stage2 transformation
    print("\n2. Testing Stage2 transformation...")
    minimal_stage2 = transform_stage2_to_minimal(stage2_full)
    print(f"   ✓ Transformed {len(stage2_full)} stage2 responses")
    print(f"   Original size: {len(json.dumps(stage2_full))} bytes")
    minimal_stage2_dict = [s.dict() for s in minimal_stage2]
    print(f"   Minimal size:  {len(json.dumps(minimal_stage2_dict))} bytes")
    reduction_stage2 = (1 - len(json.dumps(minimal_stage2_dict)) / len(json.dumps(stage2_full))) * 100
    print(f"   Reduction:     {reduction_stage2:.1f}%")
    
    assert minimal_stage2[0].rankings[0].rank == 1
    assert minimal_stage2[0].rankings[0].model == "openai/gpt-4"
    print("   ✓ Data integrity verified")
    
    # Test Stage3 transformation
    print("\n3. Testing Stage3 transformation...")
    minimal_stage3 = transform_stage3_to_minimal(stage3_full)
    print(f"   Original size: {len(json.dumps(stage3_full))} bytes")
    minimal_stage3_dict = minimal_stage3.dict()
    print(f"   Minimal size:  {len(json.dumps(minimal_stage3_dict))} bytes")
    reduction_stage3 = (1 - len(json.dumps(minimal_stage3_dict)) / len(json.dumps(stage3_full))) * 100
    print(f"   Reduction:     {reduction_stage3:.1f}%")
    
    assert minimal_stage3.model == "anthropic/claude-3.5-sonnet"
    assert "Final synthesized" in minimal_stage3.response
    print("   ✓ Data integrity verified")
    
    # Test full message transformation
    print("\n4. Testing full message transformation...")
    minimal_message = transform_message_to_minimal(
        stage1_full, stage2_full, stage3_full, metadata
    )
    
    full_response = {
        "stage1": stage1_full,
        "stage2": stage2_full,
        "stage3": stage3_full,
        "metadata": metadata
    }
    
    full_size = len(json.dumps(full_response))
    minimal_size = len(json.dumps(minimal_message.dict()))
    
    print(f"   Full response size:    {full_size:,} bytes")
    print(f"   Minimal response size: {minimal_size:,} bytes")
    print(f"   Size reduction:        {full_size - minimal_size:,} bytes")
    print(f"   Percentage reduction:  {((1 - minimal_size/full_size) * 100):.1f}%")
    
    # Verify metadata enhancement
    assert "model_timings" in minimal_message.metadata
    print("   ✓ Metadata consolidated with model timings")
    
    print("\n" + "="*60)
    print(" ✅ All tests passed!")
    print("="*60)
    print(f"\n📊 Overall size reduction: {((1 - minimal_size/full_size) * 100):.1f}%")
    print("🎯 Target was 40% reduction\n")
    
    return True


if __name__ == "__main__":
    try:
        test_transformations()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
