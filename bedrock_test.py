import boto3
import json

client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
)

prompt = """Generate one Class 7 mathematics multiple-choice question about fractions.

Return:
Question:
Option A:
Option B:
Option C:
Option D:
Correct Answer:
"""

response = client.invoke_model(
    modelId="us.amazon.nova-2-lite-v1:0",
    body=json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 300,
            "temperature": 0.2
        }
    }),
    contentType="application/json",
    accept="application/json",
)

result = json.loads(response["body"].read())

print(json.dumps(result, indent=2, ensure_ascii=False))
