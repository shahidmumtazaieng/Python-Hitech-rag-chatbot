#!/usr/bin/env python3
"""Quick LangChain Gemini test."""

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

print("=" * 60)
print("Testing Gemini 2.5 Flash with LangChain")
print("=" * 60)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    max_output_tokens=2048
)

print("\n📡 Sending test query...")
print("   Question: What steel products does Hitech offer?\n")

# Test response
response = llm.invoke("What steel products does Hitech offer? Give a brief answer.")

print("✅ Response received:")
print("-" * 60)
print(response.content)
print("-" * 60)
print("\n✅ Gemini API is working correctly!")
