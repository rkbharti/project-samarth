#!/usr/bin/env python3
"""
Project Samarth Data Setup Script (robust)
- Builds knowledge base
- Attempts vectorstore build, but will not fail whole script if embeddings missing
"""

import sys
import os
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent.parent))

from backend.utils.enhanced_data_fetcher import Enhanced2025DataFetcher
from backend.services.enhanced_vector_store import EnhancedVectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Project Samarth data setup...")

    dfetch = Enhanced2025DataFetcher()

    logger.info("🌾 Fetching agriculture datasets...")
    agriculture_datasets = dfetch.fetch_2025_agriculture_data()
    logger.info(f"Fetched {len(agriculture_datasets)} agriculture datasets")

    logger.info("🌧️ Fetching rainfall datasets...")
    rainfall_datasets = dfetch.fetch_enhanced_imd_rainfall()
    logger.info(f"Fetched {len(rainfall_datasets)} rainfall datasets")

    all_datasets = agriculture_datasets + rainfall_datasets

    logger.info("🧠 Creating knowledge base...")
    chunks = dfetch.create_2025_knowledge_base(all_datasets)
    logger.info(f"Created {len(chunks)} knowledge chunks")

    # Try to build vectorstore but do not abort on embedding import errors
    try:
        logger.info("📊 Initializing vector store...")
        vstore = EnhancedVectorStore()
        vstore.create_optimized_index(chunks)
        out_path = "data/vectorstore_2025"
        vstore.save_optimized_index(out_path)
        logger.info("✅ Vector store built and saved")
    except ImportError as ie:
        if 'sentence_transformers' in str(ie):
            logger.warning("⚠️ sentence-transformers not available; skipping vectorstore build. You can re-run after installing.")
        else:
            raise
    except Exception as e:
        logger.warning(f"⚠️ Vectorstore build skipped due to: {e}")

    logger.info("✨ Data setup completed. You can start the API now.")
    return True

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
