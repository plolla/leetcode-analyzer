"""
Test script for hint generation endpoint
"""
import asyncio
from services.ai.ai_service_factory import ai_service

async def test_hints():
    problem_description = "Two Sum: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."
    
    code = """
def twoSum(nums, target):
    # I'm stuck, need help
    for i in range(len(nums)):
        pass
"""
    
    language = "python"
    
    print("Testing hint generation...")
    print(f"Problem: {problem_description[:50]}...")
    print(f"Code length: {len(code)} characters")
    print(f"Language: {language}")
    print("\nGenerating hints...\n")
    
    try:
        result = await ai_service.generate_hints(
            problem_description=problem_description,
            code=code,
            language=language
        )
        
        print("✓ Hint generation successful!")
        print(f"\nProgressive: {result.progressive}")
        print(f"\nHints ({len(result.hints)}):")
        for i, hint in enumerate(result.hints, 1):
            print(f"  {i}. {hint}")
        
        print(f"\nNext Steps ({len(result.next_steps)}):")
        for i, step in enumerate(result.next_steps, 1):
            print(f"  {i}. {step}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hints())
