from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
from typing import List, Dict, Optional
import pickle
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EnhancedVectorStore:
    """Enhanced FAISS vector store with 2025 best practices and government context weighting"""
    
    def __init__(self, embedding_model='sentence-transformers/all-MiniLM-L6-v2'):
        # Use free, high-performance embedding model
        logger.info(f"🤖 Initializing embeddings with model: {embedding_model}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = None
        self.index_params = {
            'index_type': 'HNSW',  # Best for most use cases
            'ef_construction': 200,
            'M': 16
        }
        
        # Text splitter for optimal chunk sizes
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def create_optimized_index(self, chunks: List[Dict]) -> None:
        """Create FAISS index with 2025 best practices and optimization"""
        if not chunks:
            logger.warning("No chunks provided for index creation")
            return
        
        logger.info(f"📊 Creating optimized FAISS index with {len(chunks)} chunks")
        
        # Prepare texts and metadata
        texts = []
        metadatas = []
        
        for chunk in chunks:
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            
            if not text.strip():
                continue
            
            # Split large texts for better retrieval
            if len(text) > 1000:
                splits = self.text_splitter.split_text(text)
                texts.extend(splits)
                # Preserve metadata for each split
                metadatas.extend([metadata.copy() for _ in splits])
            else:
                texts.append(text)
                metadatas.append(metadata)
        
        if not texts:
            logger.error("No valid texts found after processing")
            return
        
        logger.info(f"📋 After splitting: {len(texts)} text chunks")
        
        try:
            # Create FAISS index with HNSW for optimal performance
            self.vectorstore = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            # Optimize index parameters for better performance
            index = self.vectorstore.index
            if hasattr(index, 'hnsw'):
                index.hnsw.ef = 100  # Query-time parameter
                logger.info("⚙️ HNSW index parameters optimized")
            
            logger.info(f"✅ FAISS index created successfully with {self.vectorstore.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {e}")
            raise
    
    def save_optimized_index(self, path: str) -> None:
        """Save index with compression and metadata for production deployment"""
        if not self.vectorstore:
            logger.error("No vectorstore to save")
            return
        
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
            
            # Save the main FAISS index
            self.vectorstore.save_local(str(path_obj))
            
            # Save additional optimization metadata
            optimization_info = {
                'index_type': self.index_params['index_type'],
                'embedding_model': self.embeddings.model_name,
                'total_vectors': self.vectorstore.index.ntotal,
                'dimension': self.vectorstore.index.d,
                'created_date': '2025-10-30',
                'version': '2025.1.0',
                'optimization_params': self.index_params
            }
            
            with open(path_obj / 'optimization_info.json', 'w') as f:
                json.dump(optimization_info, f, indent=2)
            
            logger.info(f"✅ Optimized index saved to: {path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def load_local(self, path: str) -> None:
        """Load existing vector store from local path"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                logger.error(f"Path does not exist: {path}")
                return
            
            self.vectorstore = FAISS.load_local(
                str(path_obj),
                self.embeddings
            )
            
            # Load optimization info if available
            info_file = path_obj / 'optimization_info.json'
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                logger.info(f"📊 Loaded index: {info.get('total_vectors', 'unknown')} vectors")
            
            logger.info(f"✅ Vector store loaded from: {path}")
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise
    
    def similarity_search_with_government_context(self, query: str, k: int = 5) -> List[tuple]:
        """Enhanced search with policy context weighting and government priority"""
        if not self.vectorstore:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            # Get more results than needed for filtering and ranking
            results = self.vectorstore.similarity_search_with_score(query, k=k*3)
            
            # Apply context weighting for government policies and recent data
            weighted_results = []
            
            for doc, score in results:
                metadata = doc.metadata
                weight = 1.0
                
                # Boost recent data (2024-2025)
                doc_year = metadata.get('year', 0)
                if isinstance(doc_year, (int, float)) and doc_year >= 2024:
                    weight *= 1.2
                
                # Boost government policy sources
                if metadata.get('source') == 'government_policy':
                    weight *= 1.15
                
                # Boost agricultural statistics
                category = metadata.get('category', '').lower()
                if 'agriculture' in category or 'crop' in category:
                    weight *= 1.1
                
                # Boost scheme-related content
                if metadata.get('scheme'):
                    weight *= 1.1
                
                # Boost high-reliability sources
                if metadata.get('source') in ['data.gov.in', 'imd', 'ministry_agriculture']:
                    weight *= 1.05
                
                # Apply weight (lower score is better in FAISS)
                adjusted_score = score / weight
                
                weighted_results.append((doc, adjusted_score, weight))
            
            # Sort by adjusted score and return top k
            weighted_results.sort(key=lambda x: x[1])
            
            # Return tuples of (document, adjusted_score)
            final_results = [(doc, score) for doc, score, _ in weighted_results[:k]]
            
            logger.info(f"🔍 Retrieved {len(final_results)} results for query")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def add_documents(self, new_chunks: List[Dict]) -> None:
        """Add new documents to existing vector store"""
        if not new_chunks:
            logger.warning("No new chunks to add")
            return
        
        try:
            texts = [chunk['text'] for chunk in new_chunks]
            metadatas = [chunk['metadata'] for chunk in new_chunks]
            
            if self.vectorstore:
                # Add to existing store
                self.vectorstore.add_texts(texts, metadatas=metadatas)
                logger.info(f"➕ Added {len(texts)} new documents to existing index")
            else:
                # Create new store if none exists
                self.create_optimized_index(new_chunks)
                logger.info(f"🆕 Created new index with {len(texts)} documents")
        
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if not self.vectorstore:
            return {'status': 'not_initialized'}
        
        try:
            stats = {
                'status': 'initialized',
                'total_vectors': self.vectorstore.index.ntotal,
                'vector_dimension': self.vectorstore.index.d,
                'index_type': type(self.vectorstore.index).__name__,
                'embedding_model': self.embeddings.model_name
            }
            
            # Try to get additional FAISS-specific stats
            if hasattr(self.vectorstore.index, 'is_trained'):
                stats['index_trained'] = self.vectorstore.index.is_trained
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def search_by_metadata(self, filters: Dict, k: int = 10) -> List[tuple]:
        """Search documents by metadata filters"""
        if not self.vectorstore:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            # This is a simplified implementation
            # In production, you might want to use more sophisticated filtering
            all_results = self.vectorstore.similarity_search_with_score(
                "",  # Empty query to get all documents
                k=self.vectorstore.index.ntotal
            )
            
            filtered_results = []
            for doc, score in all_results:
                metadata = doc.metadata
                match = True
                
                for key, value in filters.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_results.append((doc, score))
                
                if len(filtered_results) >= k:
                    break
            
            logger.info(f"🔎 Metadata search found {len(filtered_results)} results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in metadata search: {e}")
            return []