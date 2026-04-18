#!/usr/bin/env python3
"""Test Pinecone connection and index status."""

import os
from dotenv import load_dotenv

load_dotenv()

def test_pinecone():
    print("=" * 60)
    print("Pinecone Connection Test")
    print("=" * 60)
    
    # Get environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    host = os.getenv("PINECONE_HOST")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    dimension = os.getenv("PINECONE_DIMENSION")
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {api_key[:20]}... (hidden)")
    print(f"   Host: {host}")
    print(f"   Index Name: {index_name}")
    print(f"   Dimension: {dimension}")
    
    try:
        from pinecone import Pinecone
        
        print(f"\n🔌 Initializing Pinecone client...")
        pc = Pinecone(
            api_key=api_key,
            host=host if host else None
        )
        print("✅ Pinecone client initialized")
        
        print(f"\n📊 Listing existing indexes...")
        indexes = [idx.name for idx in pc.list_indexes()]
        print(f"   Found indexes: {indexes}")
        
        if index_name in indexes:
            print(f"\n✅ Index '{index_name}' exists!")
            
            print(f"\n🔗 Connecting to index...")
            index = pc.Index(index_name)
            print(f"✅ Connected to index '{index_name}'")
            
            print(f"\n📈 Getting index stats...")
            stats = index.describe_index_stats()
            print(f"   Total vectors: {stats.total_vector_count}")
            print(f"   Dimension: {stats.dimension}")
            print(f"   Index fullness: {stats.index_fullness:.1%}")
            
            print("\n" + "=" * 60)
            print("✅ Pinecone connection test PASSED!")
            print("=" * 60)
            return True
            
        else:
            print(f"\n⚠️ Index '{index_name}' does NOT exist!")
            print(f"\n📝 To create it:")
            print(f"   Option 1: Run the app - it will auto-create the index")
            print(f"   Option 2: Create via Pinecone console at https://app.pinecone.io")
            
            create_now = input("\n❓ Create index now? (y/n): ").strip().lower()
            if create_now == 'y':
                from pinecone import ServerlessSpec
                print(f"\n🔨 Creating index '{index_name}'...")
                pc.create_index(
                    name=index_name,
                    dimension=int(dimension),
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"✅ Index created successfully!")
                print("⏳ Waiting 10 seconds for index to be ready...")
                import time
                time.sleep(10)
                print("✅ Index is ready!")
                return True
            else:
                return False
                
    except Exception as e:
        print(f"\n❌ Pinecone connection FAILED!")
        print(f"   Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your PINECONE_API_KEY is correct")
        print("   2. Verify PINECONE_HOST URL is valid")
        print("   3. Check your internet connection")
        print("   4. Visit https://app.pinecone.io to verify your account")
        return False


if __name__ == "__main__":
    test_pinecone()
