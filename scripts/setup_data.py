#!/usr/bin/env python3
"""
Project Samarth Data Setup Script

This script initializes the data collection and processing pipeline.
Run this script first to set up the knowledge base.
"""

import sys
import os
from pathlib import Path
import logging

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from utils.enhanced_data_fetcher import Enhanced2025DataFetcher
from services.enhanced_vector_store import EnhancedVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main data setup function"""
    logger.info("🚀 Starting Project Samarth data setup...")
    
    try:
        # Initialize data fetcher
        logger.info("📥 Initializing data fetcher...")
        data_fetcher = Enhanced2025DataFetcher()
        
        # Fetch agriculture data
        logger.info("🌾 Fetching agriculture datasets...")
        agriculture_datasets = data_fetcher.fetch_2025_agriculture_data()
        logger.info(f"Fetched {len(agriculture_datasets)} agriculture datasets")
        
        # Fetch rainfall data
        logger.info("🌧️ Fetching rainfall datasets...")
        rainfall_datasets = data_fetcher.fetch_enhanced_imd_rainfall()
        logger.info(f"Fetched {len(rainfall_datasets)} rainfall datasets")
        
        # Combine all datasets
        all_datasets = agriculture_datasets + rainfall_datasets
        
        if not all_datasets:
            logger.warning("⚠️ No datasets were fetched. Creating sample data...")
            all_datasets = create_sample_datasets()
        
        # Create knowledge base
        logger.info("🧠 Creating knowledge base...")
        all_chunks = data_fetcher.create_2025_knowledge_base(all_datasets)
        logger.info(f"Created {len(all_chunks)} knowledge chunks")
        
        if not all_chunks:
            logger.error("❌ No knowledge chunks created. Cannot proceed.")
            return False
        
        # Initialize vector store
        logger.info("📊 Initializing vector store...")
        vector_store = EnhancedVectorStore()
        
        # Create and save vector index
        logger.info("🔨 Building FAISS vector index...")
        vector_store.create_optimized_index(all_chunks)
        
        # Save the index
        vectorstore_path = "data/vectorstore_2025"
        logger.info(f"💾 Saving vector store to {vectorstore_path}...")
        vector_store.save_optimized_index(vectorstore_path)
        
        # Get and display stats
        stats = vector_store.get_stats()
        logger.info(f"✅ Vector store created successfully!")
        logger.info(f"Stats: {stats}")
        
        logger.info("✨ Data setup completed successfully!")
        logger.info("🚀 You can now start the FastAPI backend with: uvicorn backend.main:app --reload")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_datasets() -> list:
    """Create sample datasets if real data fetching fails"""
    logger.info("📋 Creating sample datasets for demonstration...")
    
    sample_datasets = [
        {
            'data': {
                'total_production_2024_25': 353.96,
                'rice_production': 130.29,
                'wheat_production': 114.92,
                'states': {
                    'Uttar Pradesh': {'rice': 12.5, 'wheat': 30.2},
                    'Punjab': {'rice': 11.8, 'wheat': 18.6},
                    'West Bengal': {'rice': 15.2, 'wheat': 0.9}
                }
            },
            'metadata': {
                'name': 'Sample Food Grain Production 2024-25',
                'source': 'ministry_agriculture',
                'description': 'Sample production data for demonstration',
                'url': 'https://desagri.gov.in/',
                'year': 2025,
                'category': 'agriculture_production'
            },
            'last_updated': '2025-10-30T16:23:00'
        },
        {
            'data': {
                'registered_farmers': 1.79,
                'registered_traders': 2.2,
                'mandis_connected': 1361,
                'total_trade_value': 2.8
            },
            'metadata': {
                'name': 'Sample e-NAM Market Data',
                'source': 'enam_platform',
                'description': 'Sample market data for demonstration',
                'url': 'https://enam.gov.in/',
                'year': 2025,
                'category': 'market_data'
            },
            'last_updated': '2025-10-30T16:23:00'
        },
        {
            'data': {
                'latest_year_rainfall': {
                    'all_india_average': 868.6,
                    'monsoon_2024': 923.1
                },
                'regional_averages': {
                    'Northwest India': 650.2,
                    'Central India': 1012.3,
                    'South Peninsula': 975.4
                }
            },
            'metadata': {
                'name': 'Sample IMD Rainfall Data',
                'source': 'imd',
                'description': 'Sample rainfall data for demonstration',
                'url': 'https://mausam.imd.gov.in/',
                'year': 2024,
                'category': 'climate_data'
            },
            'last_updated': '2025-10-30T16:23:00'
        }
    ]
    
    return sample_datasets

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)