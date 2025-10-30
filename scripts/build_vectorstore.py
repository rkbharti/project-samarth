#!/usr/bin/env python3
"""
Project Samarth Vector Store Builder

This script specifically handles vector store creation and optimization.
Use this if you need to rebuild just the vector store.
"""

import sys
import os
from pathlib import Path
import logging
import json

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from services.enhanced_vector_store import EnhancedVectorStore
from utils.enhanced_data_fetcher import Enhanced2025DataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_processed_data():
    """Load processed data from files if available"""
    processed_dir = Path("data/processed")
    
    if not processed_dir.exists():
        logger.warning("No processed data directory found")
        return None
    
    chunks_file = processed_dir / "knowledge_chunks.json"
    if chunks_file.exists():
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            logger.info(f"Loaded {len(chunks)} chunks from processed data")
            return chunks
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
    
    return None

def save_processed_data(chunks):
    """Save processed chunks for future use"""
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    chunks_file = processed_dir / "knowledge_chunks.json"
    try:
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(chunks)} chunks to processed data")
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")

def main():
    """Main vector store building function"""
    logger.info("🔨 Building Project Samarth vector store...")
    
    try:
        # Try to load existing processed data first
        chunks = load_processed_data()
        
        if not chunks:
            # If no processed data, fetch and process new data
            logger.info("📥 No processed data found. Fetching fresh data...")
            
            data_fetcher = Enhanced2025DataFetcher()
            
            # Fetch all datasets
            agriculture_datasets = data_fetcher.fetch_2025_agriculture_data()
            rainfall_datasets = data_fetcher.fetch_enhanced_imd_rainfall()
            
            all_datasets = agriculture_datasets + rainfall_datasets
            
            if not all_datasets:
                logger.warning("No datasets fetched. Using sample data...")
                all_datasets = create_sample_datasets()
            
            # Create knowledge chunks
            chunks = data_fetcher.create_2025_knowledge_base(all_datasets)
            
            if chunks:
                save_processed_data(chunks)
        
        if not chunks:
            logger.error("❌ No chunks available for vector store creation")
            return False
        
        logger.info(f"🧠 Processing {len(chunks)} knowledge chunks...")
        
        # Initialize vector store
        vector_store = EnhancedVectorStore(
            embedding_model='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # Create optimized index
        logger.info("🔨 Creating optimized FAISS index...")
        vector_store.create_optimized_index(chunks)
        
        # Save the index
        vectorstore_path = "data/vectorstore_2025"
        logger.info(f"💾 Saving vector store to {vectorstore_path}...")
        vector_store.save_optimized_index(vectorstore_path)
        
        # Verify the saved index
        logger.info("🔍 Verifying saved vector store...")
        test_vector_store = EnhancedVectorStore()
        test_vector_store.load_local(vectorstore_path)
        
        # Test search
        test_results = test_vector_store.similarity_search_with_government_context(
            "rice production in Punjab", k=3
        )
        
        logger.info(f"✅ Vector store verification successful!")
        logger.info(f"Test search returned {len(test_results)} results")
        
        # Display stats
        stats = vector_store.get_stats()
        logger.info(f"Final stats: {stats}")
        
        logger.info("✨ Vector store building completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Vector store building failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_datasets():
    """Create sample datasets if real data is not available"""
    return [
        {
            'data': {
                'total_production_2024_25': 353.96,
                'rice_production': 130.29,
                'wheat_production': 114.92,
                'states': {
                    'Punjab': {'rice': 11.8, 'wheat': 18.6},
                    'Uttar Pradesh': {'rice': 12.5, 'wheat': 30.2},
                    'West Bengal': {'rice': 15.2, 'wheat': 0.9}
                }
            },
            'metadata': {
                'name': 'Food Grain Production 2024-25',
                'source': 'ministry_agriculture',
                'description': 'Latest production statistics',
                'year': 2025,
                'category': 'agriculture_production'
            }
        }
    ]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)