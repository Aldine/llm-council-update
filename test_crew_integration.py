"""Test script for CrewAI council integration."""

import asyncio
from backend.crew_council import run_crew_council_deliberation


async def test_crew_council():
    """Test the CrewAI-powered council deliberation."""
    print("🤖 Testing CrewAI Council Integration\n")
    print("=" * 60)
    
    test_query = "What is the best approach to learning a new programming language?"
    
    print(f"\n📝 Query: {test_query}\n")
    print("Starting 3-stage CrewAI deliberation...\n")
    
    try:
        result = await run_crew_council_deliberation(test_query)
        
        print("✅ Stage 1 - Individual Responses:")
        print("-" * 60)
        for i, response in enumerate(result["stage1"], 1):
            print(f"\n{i}. {response['role']} ({response['model']})")
            print(f"   Response: {response['response'][:200]}...")
        
        print("\n\n✅ Stage 2 - Peer Rankings:")
        print("-" * 60)
        for i, ranking in enumerate(result["stage2"], 1):
            print(f"\n{i}. {ranking['role']} ({ranking['model']})")
            print(f"   Ranking: {ranking['ranking'][:200]}...")
        
        print("\n\n✅ Stage 3 - Final Synthesis:")
        print("-" * 60)
        print(f"\n{result['stage3']['role']} ({result['stage3']['model']})")
        print(f"\n{result['stage3']['response']}")
        
        print("\n\n" + "=" * 60)
        print("✅ CrewAI Integration Test Completed Successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_crew_council())
