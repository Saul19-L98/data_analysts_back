"""
Quick test script to verify JSON parsing strategies work correctly.
This simulates the truncated JSON response from Bedrock.
"""
import json
from app.services.bedrock_service import BedrockService

# Simulate a simpler truncated response (more typical case)
truncated_json1 = """{
  "version": "1.0",
  "context": {
    "type": "data_analysis"
  },
  "suggested_charts": [
    {
      "chart_type": "bar",
      "title": "Sales by Product",
      "data_source": {
        "columns": ["product", "sales"]
      }
    }
  ],
  "incomplete_field": "this value is cut off mid"""

print("=" * 60)
print("TEST 1: Truncated mid-string")
print("=" * 60)
print(f"Input length: {len(truncated_json1)} chars\n")

result1 = BedrockService._parse_json_response(truncated_json1)

print(f"\nResult type: {type(result1)}")
if isinstance(result1, dict):
    print("[OK] SUCCESS! Parsed as JSON object")
    print(f"Keys: {list(result1.keys())}")
    print(json.dumps(result1, indent=2))
else:
    print("[FAIL] Still returned as string")

# Test 2: The actual complex case
truncated_json2 = """{
  "version": "1.0",
  "context": {
    "type": "data_analysis",
    "file_info": {
      "filename": "paper_sales.csv",
      "columns": ["date", "paper_type", "quantity", "price", "total_sales"]
    }
  },
  "suggested_charts": [
    {
      "chart_type": "bar",
      "title": "Ventas por Tipo de Papel",
      "description": "Comparación de ventas totales por tipo de papel",
      "data_source": {
        "table": "paper_sales",
        "columns": ["paper_type", "total_sales"],
        "http_method": "POST","""

# What Strategy 4 should produce (cut at the `],` after "total_sales")
# This leaves us with:
# { ... "columns": ["paper_type", "total_sales"] ... } 
# But wait, data_source is still open! So we need to close data_source too
# The issue is we're inside data_source object which is incomplete

# Let me print the structure
print("\n" + "=" * 60)
print("TEST 2: Complex nested truncation - ANALYSIS")
print("=" * 60)
print(f"Input length: {len(truncated_json2)} chars")
print("\nLet's manually find where to cut...")
print("Looking for last CLOSED array (],) :")

import re
matches = list(re.finditer(r'\],', truncated_json2))
if matches:
    for i, m in enumerate(matches):
        print(f"  Match {i+1} at position {m.start()}: '{truncated_json2[max(0,m.start()-20):m.start()+5]}'")

# The issue: even after cutting at "],", we still have open "data_source": {
# So let's try cutting at the PREVIOUS "],

result2 = BedrockService._parse_json_response(truncated_json2)

print(f"\nResult type: {type(result2)}")
if isinstance(result2, dict):
    print("[OK] SUCCESS! Parsed as JSON object")
    print(f"Keys: {list(result2.keys())}")
    if 'suggested_charts' in result2:
        print(f"Number of charts: {len(result2['suggested_charts'])}")
    print(json.dumps(result2, indent=2))
else:
    print("[FAIL] Still returned as string")

