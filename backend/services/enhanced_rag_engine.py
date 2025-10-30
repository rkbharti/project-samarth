from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import re
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Enhanced2025RAGEngine:
    """Enhanced RAG engine with 2025 agricultural context and policy integration"""
    
    def __init__(self, vector_store, use_local_llm=True):
        self.vector_store = vector_store
        self.use_local_llm = use_local_llm
        
        # Initialize LLM based on configuration
        if use_local_llm:
            logger.info("🤖 Initializing local LLM (HuggingFace)")
            try:
                # Using a lightweight model for cost efficiency
                self.llm = HuggingFacePipeline.from_model_id(
                    model_id="microsoft/DialoGPT-medium",
                    task="text-generation",
                    model_kwargs={
                        "temperature": 0.1, 
                        "max_length": 512,
                        "do_sample": True
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to load local LLM: {e}. Using fallback.")
                self.llm = None
        else:
            logger.info("🌐 Initializing OpenAI LLM")
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0
            )
    
    def parse_2025_query(self, question: str) -> Dict:
        """Enhanced query parsing with 2025 agricultural context"""
        intent = {
            'type': None,
            'states': [],
            'crops': [],
            'years': [],
            'metrics': [],
            'schemes': [],  # Government schemes
            'policies': []   # Policy queries
        }
        
        question_lower = question.lower()
        
        # 2025 Government Schemes Detection
        scheme_patterns = {
            'pm_dhan_dhaanya': ['pm.*dhan.*dhaanya', 'dhan.*dhaanya'],
            'bharati': ['bharati', 'bharti.*initiative'],
            'pkvy': ['pkvy', 'paramparagat.*krishi'],
            'enam': ['e-nam', 'enam', 'national.*agriculture.*market'],
            'soil_health': ['soil.*health.*card', 'shc'],
            'kisan_credit': ['kisan.*credit.*card', 'kcc']
        }
        
        for scheme_name, patterns in scheme_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    intent['schemes'].append(scheme_name)
                    intent['type'] = 'scheme_query'
                    break
        
        # Policy and Budget Queries
        policy_patterns = [
            'budget.*202[45]', 'allocation', 'government.*scheme',
            'ministry.*agriculture', 'atmanirbhar', 'self.*relian',
            'expenditure', 'funding'
        ]
        
        for pattern in policy_patterns:
            if re.search(pattern, question_lower):
                intent['policies'].append(pattern)
                if intent['type'] is None:
                    intent['type'] = 'policy_query'
        
        # Standard query type detection
        if intent['type'] is None:
            if 'compare' in question_lower or 'comparison' in question_lower:
                intent['type'] = 'comparison'
            elif any(word in question_lower for word in ['trend', 'over time', 'years', 'decade']):
                intent['type'] = 'trend'
            elif any(word in question_lower for word in ['correlate', 'relationship', 'impact', 'effect']):
                intent['type'] = 'correlation'
            elif any(word in question_lower for word in ['recommend', 'suggest', 'advice']):
                intent['type'] = 'recommendation'
            else:
                intent['type'] = 'general'
        
        # Extract entities (simplified - in production, use spaCy NER)
        # States
        indian_states = [
            'punjab', 'haryana', 'uttar pradesh', 'bihar', 'west bengal',
            'maharashtra', 'gujarat', 'rajasthan', 'madhya pradesh',
            'karnataka', 'tamil nadu', 'andhra pradesh', 'telangana',
            'kerala', 'odisha', 'jharkhand', 'chhattisgarh'
        ]
        
        for state in indian_states:
            if state in question_lower:
                intent['states'].append(state.title())
        
        # Crops
        major_crops = [
            'rice', 'wheat', 'cotton', 'sugarcane', 'pulses', 'oilseeds',
            'maize', 'bajra', 'jowar', 'barley', 'gram', 'tur', 'moong'
        ]
        
        for crop in major_crops:
            if crop in question_lower:
                intent['crops'].append(crop.title())
        
        # Years
        year_pattern = r'20[0-9]{2}'
        years = re.findall(year_pattern, question)
        intent['years'] = [int(year) for year in years]
        
        logger.info(f"Parsed intent: {intent}")
        return intent
    
    def retrieve_relevant_data(self, question: str, intent: Dict, k: int = 5) -> List[Dict]:
        """Get relevant chunks based on query intent with 2025 enhancements"""
        if not self.vector_store or not hasattr(self.vector_store, 'vectorstore'):
            logger.warning("Vector store not available")
            return []
        
        try:
            # Use enhanced similarity search with government context
            results = self.vector_store.similarity_search_with_government_context(
                question, k=k*2  # Get more results for filtering
            )
            
            # Filter and rank based on intent
            filtered_results = []
            for doc, score in results:
                metadata = doc.metadata
                content = doc.page_content
                
                # Apply intent-based filtering
                relevance_boost = 1.0
                
                # State filtering
                if intent.get('states'):
                    doc_states = [metadata.get('state', '').lower()]
                    if any(state.lower() in doc_states for state in intent['states']):
                        relevance_boost *= 1.3
                    else:
                        continue  # Skip if state doesn't match
                
                # Crop filtering
                if intent.get('crops'):
                    doc_crops = [metadata.get('crop', '').lower()]
                    if any(crop.lower() in doc_crops for crop in intent['crops']):
                        relevance_boost *= 1.2
                
                # Year filtering
                if intent.get('years'):
                    doc_year = metadata.get('year', 0)
                    if doc_year in intent['years']:
                        relevance_boost *= 1.4
                
                # Scheme/Policy boost
                if intent['type'] in ['scheme_query', 'policy_query']:
                    if metadata.get('source') == 'government_policy':
                        relevance_boost *= 1.5
                
                adjusted_score = score / relevance_boost  # Lower score = better
                
                filtered_results.append({
                    'content': content,
                    'metadata': metadata,
                    'score': adjusted_score,
                    'relevance_boost': relevance_boost
                })
            
            # Sort by adjusted score and return top k
            filtered_results.sort(key=lambda x: x['score'])
            return filtered_results[:k]
            
        except Exception as e:
            logger.error(f"Error in data retrieval: {e}")
            return []
    
    def generate_2025_enhanced_answer(self, question: str, context: List[Dict]) -> Dict:
        """Generate answers with 2025 agricultural context and policy integration"""
        
        # Build enhanced context with policy information
        context_str = self._build_enhanced_context(context)
        
        # Enhanced prompt with 2025 context
        prompt = f"""You are an expert agricultural data analyst for the Government of India, 
specializing in the latest 2025 agricultural policies and data.

## Current Agricultural Context (2025 Update):
- Food grain production: 353.96 million tonnes (2024-25)
- Agriculture budget: ₹1,37,756.55 crore (2025-26)  
- e-NAM registered farmers: 1.79 crore
- PM Dhan-Dhaanya Krishi Yojana: ₹24,000 crore annually (2025-31)
- BHARATI Initiative: Supporting 100 agri-tech startups

## Available Data Sources:
{context_str}

## User Question: 
{question}

## Instructions:
1. Provide accurate answers based on the latest 2025 data available
2. Cite specific sources using [Source X] format for every claim
3. Include relevant government scheme information when applicable
4. Mention budget allocations and policy context where relevant
5. If comparing data across years, use the most recent figures available
6. State any data limitations or gaps clearly
7. Use specific numbers and statistics from the provided sources
8. If the question involves government schemes, provide implementation details

## Response Format:
- Start with a direct answer to the question
- Provide supporting data with citations
- Include policy context if relevant
- End with data source information

Answer:"""

        try:
            # Generate response using selected LLM
            if self.llm:
                if self.use_local_llm:
                    # For local models, we need to handle the response differently
                    response = self._generate_with_local_llm(prompt)
                else:
                    response = self.llm.predict(prompt)
            else:
                # Fallback response if LLM is not available
                response = self._generate_fallback_response(question, context)
            
            # Extract and format citations
            citations = self._extract_enhanced_citations(response, context)
            
            # Extract policy context
            policy_context = self._extract_policy_context(context)
            
            return {
                'answer': response,
                'citations': citations,
                'context_used': context,
                'policy_context': policy_context,
                'data_vintage': '2025-edition'
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                'answer': f"I apologize, but I encountered an error processing your question about: {question}. Please try rephrasing your query.",
                'citations': [],
                'context_used': context,
                'policy_context': [],
                'data_vintage': '2025-edition'
            }
    
    def _generate_with_local_llm(self, prompt: str) -> str:
        """Generate response using local HuggingFace model"""
        try:
            # Truncate prompt if too long
            max_prompt_length = 1000
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "..."
            
            response = self.llm(prompt)
            
            # Extract the generated text from the response
            if isinstance(response, str):
                return response
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Local LLM generation error: {e}")
            return self._generate_fallback_response("extracted from prompt", [])
    
    def _generate_fallback_response(self, question: str, context: List[Dict]) -> str:
        """Generate a fallback response when LLM is not available"""
        if not context:
            return f"I don't have enough information to answer your question about: {question}. Please ensure the data sources are properly loaded."
        
        # Create a basic response from context
        response_parts = []
        response_parts.append(f"Based on available agricultural data sources:")
        
        for i, chunk in enumerate(context[:3]):  # Use top 3 chunks
            content = chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
            response_parts.append(f"\n[Source {i+1}]: {content}")
        
        response_parts.append("\nFor more detailed analysis, please ensure the AI models are properly configured.")
        
        return "".join(response_parts)
    
    def _build_enhanced_context(self, context: List[Dict]) -> str:
        """Build context string with enhanced 2025 information"""
        if not context:
            return "No relevant data sources found."
        
        context_parts = []
        
        for i, chunk in enumerate(context):
            content = chunk['content']
            metadata = chunk['metadata']
            
            # Add source credibility indicators
            credibility = "High" if metadata.get('source') == 'government_policy' else "Verified"
            year = metadata.get('year', 'Recent')
            source_type = metadata.get('source', 'Data Source')
            
            context_part = f"[Source {i+1}] ({credibility} - {year} - {source_type}):\n{content}\n"
            context_part += f"Metadata: State={metadata.get('state', 'N/A')}, "
            context_part += f"Crop={metadata.get('crop', 'N/A')}, "
            context_part += f"Category={metadata.get('category', 'N/A')}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _extract_enhanced_citations(self, answer: str, context: List[Dict]) -> List[Dict]:
        """Extract and format citations with enhanced metadata"""
        citations = []
        citation_pattern = r'\[Source (\d+)\]'
        matches = re.findall(citation_pattern, answer)
        
        for match in set(matches):
            idx = int(match) - 1
            if idx < len(context):
                chunk = context[idx]
                metadata = chunk['metadata']
                
                citations.append({
                    'id': match,
                    'source': metadata.get('source', 'Unknown'),
                    'url': metadata.get('url', 'N/A'),
                    'state': metadata.get('state', 'N/A'),
                    'year': metadata.get('year', 'N/A'),
                    'category': metadata.get('category', 'N/A'),
                    'scheme': metadata.get('scheme', 'N/A'),
                    'reliability': 'High' if metadata.get('source') == 'government_policy' else 'Verified'
                })
        
        return citations
    
    def _extract_policy_context(self, context: List[Dict]) -> List[Dict]:
        """Extract policy-specific context for enhanced responses"""
        policies = []
        for chunk in context:
            metadata = chunk['metadata']
            if metadata.get('source') == 'government_policy':
                policies.append({
                    'scheme': metadata.get('scheme', 'Unknown Scheme'),
                    'budget': metadata.get('budget', 'Not specified'),
                    'year': metadata.get('year', 2025),
                    'category': metadata.get('category', 'agricultural_policy'),
                    'focus_area': metadata.get('focus_area', 'General Agriculture')
                })
        return policies