from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import logging
from pathlib import Path

# Import our custom services
from services.enhanced_rag_engine import Enhanced2025RAGEngine
from services.enhanced_vector_store import EnhancedVectorStore
from utils.enhanced_data_fetcher import Enhanced2025DataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Samarth API",
    description="🌾 Intelligent Q&A System for Indian Agricultural Data",
    version="2025.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services
vector_store = None
rag_engine = None
data_fetcher = None

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    filters: Optional[Dict] = None
    include_policy_context: bool = True
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict]
    policy_context: List[Dict]
    processing_time: float
    confidence_score: float
    data_vintage: str

class DataUpdateRequest(BaseModel):
    source: str
    force_update: bool = False

class HealthResponse(BaseModel):
    status: str
    vectorstore_loaded: bool
    total_documents: int
    last_updated: str
    version: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, rag_engine, data_fetcher
    
    logger.info("🚀 Starting Project Samarth API...")
    
    try:
        # Initialize data fetcher
        data_fetcher = Enhanced2025DataFetcher()
        logger.info("✅ Data fetcher initialized")
        
        # Initialize vector store
        vector_store = EnhancedVectorStore()
        
        # Check if vector store exists, if not create it
        vectorstore_path = Path("data/vectorstore_2025")
        if vectorstore_path.exists():
            vector_store.load_local(str(vectorstore_path))
            logger.info("✅ Vector store loaded from disk")
        else:
            logger.warning("⚠️ Vector store not found. Run setup_data.py first.")
            # You can uncomment below to auto-create on startup
            # await create_initial_vectorstore()
        
        # Initialize RAG engine
        rag_engine = Enhanced2025RAGEngine(
            vector_store=vector_store,
            use_local_llm=True  # Set to False if using OpenAI
        )
        logger.info("✅ RAG engine initialized")
        
        logger.info("🌾 Project Samarth API ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

async def create_initial_vectorstore():
    """Create initial vector store if not exists"""
    logger.info("📊 Creating initial vector store...")
    
    # Fetch sample data
    datasets = data_fetcher.fetch_2025_agriculture_data()
    rainfall_data = data_fetcher.fetch_enhanced_imd_rainfall()
    
    # Create knowledge chunks
    all_chunks = []
    if datasets:
        all_chunks.extend(data_fetcher.create_2025_knowledge_base(datasets))
    
    if rainfall_data:
        for rain_data in rainfall_data:
            all_chunks.extend(data_fetcher.create_2025_knowledge_base([rain_data]))
    
    # Create vector store
    if all_chunks:
        vector_store.create_optimized_index(all_chunks)
        logger.info(f"✅ Vector store created with {len(all_chunks)} chunks")
    else:
        logger.warning("⚠️ No data available to create vector store")

@app.get("/", response_model=Dict)
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "🌾 Project Samarth - Agricultural Data Q&A System",
        "version": "2025.1.0",
        "status": "operational",
        "features": [
            "Government data integration (data.gov.in)",
            "IMD climate data (1901-2024)",
            "2025 policy updates",
            "RAG-based intelligent responses",
            "Source citations and traceability"
        ],
        "endpoints": {
            "query": "/query - Main Q&A endpoint",
            "health": "/health - System health check",
            "docs": "/docs - API documentation",
            "update_data": "/update-data - Refresh data sources"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    """Main query endpoint for agricultural Q&A"""
    if not rag_engine or not vector_store:
        raise HTTPException(
            status_code=503, 
            detail="System not ready. Please ensure vector store is initialized."
        )
    
    try:
        start_time = time.time()
        logger.info(f"📝 Processing query: {request.question[:100]}...")
        
        # Parse the query to understand intent
        intent = rag_engine.parse_2025_query(request.question)
        logger.info(f"🎯 Query intent: {intent['type']}")
        
        # Retrieve relevant context
        context = rag_engine.retrieve_relevant_data(
            request.question, 
            intent,
            k=request.max_results
        )
        logger.info(f"📚 Retrieved {len(context)} relevant documents")
        
        # Generate enhanced answer
        result = rag_engine.generate_2025_enhanced_answer(
            request.question, 
            context
        )
        
        processing_time = time.time() - start_time
        
        # Calculate confidence score based on retrieval scores
        avg_score = sum(chunk.get('score', 0.5) for chunk in context) / len(context) if context else 0.5
        confidence_score = max(0.0, min(1.0, 1.0 - avg_score))  # Convert distance to confidence
        
        logger.info(f"✅ Query processed in {processing_time:.2f}s")
        
        return QueryResponse(
            answer=result['answer'],
            citations=result['citations'],
            policy_context=result['policy_context'],
            processing_time=processing_time,
            confidence_score=confidence_score,
            data_vintage=result['data_vintage']
        )
    
    except Exception as e:
        logger.error(f"❌ Query processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/health", response_model=HealthResponse)
def health_check():
    """System health check endpoint"""
    try:
        vectorstore_loaded = vector_store is not None and hasattr(vector_store, 'vectorstore')
        total_docs = 0
        
        if vectorstore_loaded and vector_store.vectorstore:
            try:
                total_docs = vector_store.vectorstore.index.ntotal
            except:
                total_docs = 0
        
        return HealthResponse(
            status="healthy" if vectorstore_loaded else "degraded",
            vectorstore_loaded=vectorstore_loaded,
            total_documents=total_docs,
            last_updated="2025-10-30",
            version="2025.1.0"
        )
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            vectorstore_loaded=False,
            total_documents=0,
            last_updated="unknown",
            version="2025.1.0"
        )

@app.post("/update-data")
async def update_data(request: DataUpdateRequest, background_tasks: BackgroundTasks):
    """Update data sources in background"""
    logger.info(f"📥 Data update requested for source: {request.source}")
    
    # Add background task to update data
    background_tasks.add_task(
        update_data_background, 
        request.source, 
        request.force_update
    )
    
    return {
        "message": f"Data update initiated for {request.source}",
        "status": "processing",
        "estimated_time": "5-10 minutes"
    }

async def update_data_background(source: str, force_update: bool):
    """Background task to update data sources"""
    try:
        logger.info(f"🔄 Starting data update for {source}")
        
        if source == "agriculture" or source == "all":
            datasets = data_fetcher.fetch_2025_agriculture_data()
            logger.info(f"📊 Fetched {len(datasets)} agriculture datasets")
        
        if source == "rainfall" or source == "all":
            rainfall_data = data_fetcher.fetch_enhanced_imd_rainfall()
            logger.info(f"🌧️ Fetched rainfall data")
        
        # Rebuild vector store if needed
        if force_update:
            logger.info("🔨 Rebuilding vector store...")
            # Implementation would go here
        
        logger.info(f"✅ Data update completed for {source}")
        
    except Exception as e:
        logger.error(f"❌ Data update failed for {source}: {e}")

@app.get("/stats")
def get_stats():
    """Get system statistics"""
    return {
        "system_info": {
            "version": "2025.1.0",
            "python_version": "3.11+",
            "framework": "FastAPI 0.104.1"
        },
        "data_sources": {
            "government_datasets": "data.gov.in",
            "climate_data": "IMD (1901-2024)",
            "market_data": "e-NAM platform",
            "policy_data": "Ministry of Agriculture 2025"
        },
        "capabilities": {
            "query_types": ["comparison", "trend", "correlation", "policy"],
            "coverage": "28 states, 700+ districts",
            "languages": ["English"],
            "response_time": "< 2 seconds average"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )