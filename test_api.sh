#!/bin/bash

echo "Testing hints API endpoint..."
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "problem_url": null,
    "code": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
    "language": "python",
    "analysis_type": "hints"
  }' | python3 -m json.tool
