"""Quick test to demonstrate JSON parsing in Bedrock responses."""
import json

from app.services.bedrock_service import BedrockService

# Test the JSON parsing method
def test_json_parsing():
    """Test various JSON parsing scenarios."""
    
    # Test 1: Valid JSON
    valid_json = '{"version": "1.0", "insights": ["insight1", "insight2"], "summary": "test"}'
    result = BedrockService._parse_json_response(valid_json)
    print("Test 1 - Valid JSON:")
    print(f"Type: {type(result)}")
    print(f"Content: {json.dumps(result, indent=2)}")
    print()
    
    # Test 2: JSON with extra text before/after
    json_with_extra = 'Some text before\n{"status": "success", "data": [1, 2, 3]}\nSome text after'
    result = BedrockService._parse_json_response(json_with_extra)
    print("Test 2 - JSON with surrounding text:")
    print(f"Type: {type(result)}")
    print(f"Content: {json.dumps(result, indent=2)}")
    print()
    
    # Test 3: Nested JSON
    nested_json = '''
    {
      "context": {
        "dataset": "sales",
        "rows": 15
      },
      "insights": [
        {
          "title": "Sales Trend",
          "data": {"mean": 1758.33, "std": 684.32}
        }
      ]
    }
    '''
    result = BedrockService._parse_json_response(nested_json)
    print("Test 3 - Nested JSON:")
    print(f"Type: {type(result)}")
    print(f"Content: {json.dumps(result, indent=2)}")
    print()
    
    # Test 4: Invalid JSON (should return as string)
    invalid_json = "This is just plain text, not JSON"
    result = BedrockService._parse_json_response(invalid_json)
    print("Test 4 - Invalid JSON (returns as string):")
    print(f"Type: {type(result)}")
    print(f"Content: {result}")
    print()
    
    print("✅ All parsing scenarios tested successfully!")

if __name__ == "__main__":
    test_json_parsing()
