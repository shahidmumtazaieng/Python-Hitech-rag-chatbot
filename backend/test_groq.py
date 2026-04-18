#!/usr/bin/env python3
"""Test Groq API with Llama 3.1"""

from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq

print("=" * 60)
print("Testing Groq API - Llama 3.1 8B")
print("=" * 60)

api_key = os.getenv("GROQ_API_KEY")
print(f"\n📋 API Key: {api_key[:10]}... (hidden)")

client = Groq(api_key=api_key)

print("\n📡 Sending test query...")
print("   Question: What steel products does Hitech offer?\n")

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "What steel products does Hitech offer? Give a brief answer."
        }
    ],
    temperature=0.3,
    max_tokens=1024,
)

print("✅ Response received:")
print("-" * 60)
print(completion.choices[0].message.content)
print("-" * 60)
print("\n✅ Groq API is working correctly!")
