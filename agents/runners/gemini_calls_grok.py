import google.auth
import google.auth.transport.requests
import openai

# Get ADC credentials
credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(google.auth.transport.requests.Request())

print("✅ ADC Token acquired")

# Initialize OpenAI client pointing to Vertex AI Global endpoint
client = openai.OpenAI(
    base_url="https://aiplatform.googleapis.com/v1/projects/ctoteam/locations/global/endpoints/openapi",
    api_key=credentials.token
)

print("✅ Calling Grok 4.3...")

response = client.chat.completions.create(
    model="xai/grok-4.3",
    messages=[
        {"role": "user", "content": "Say hello from Grok 4.3 running on Vertex AI in ctoteam project!"}
    ],
    temperature=0.7,
    max_tokens=500
)

print("\n" + "="*60)
print(response.choices[0].message.content)
print("="*60)
print(f"Input tokens : {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")
