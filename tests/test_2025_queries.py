#!/usr/bin/env python3
"""
Specific tests for 2025 enhanced queries and features

Run with: python -m pytest tests/test_2025_queries.py -v
"""

import pytest
import requests
import json
from typing import List, Dict

API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class Test2025EnhancedQueries:
    """Test suite for 2025-specific features and queries"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Verify API is running
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API is not running")
        except requests.RequestException:
            pytest.skip("API is not accessible")
    
    def test_2025_policy_queries(self):
        """Test 2025 government policy and scheme queries"""
        policy_questions = [
            "What is the budget allocation for PM Dhan-Dhaanya Krishi Yojana?",
            "How many farmers are registered on e-NAM platform in 2025?",
            "What are the key features of BHARATI Initiative?",
            "What is the agriculture budget for 2025-26?",
            "Tell me about Paramparagat Krishi Vikas Yojana"
        ]
        
        for question in policy_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={
                    "question": question,
                    "include_policy_context": True
                },
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have meaningful answer
            assert len(data["answer"].strip()) > 50
            
            # Should include policy context for policy queries  
            assert "policy_context" in data
            
            # Should have citations
            assert len(data["citations"]) > 0
            
            # Check for 2025-specific keywords in answer
            answer_lower = data["answer"].lower()
            policy_keywords = [
                "2025", "scheme", "budget", "crore", "farmers", 
                "government", "ministry", "agriculture"
            ]
            
            # At least some policy keywords should be present
            keyword_found = any(keyword in answer_lower for keyword in policy_keywords)
            assert keyword_found, f"No policy keywords found in answer for: {question}"
    
    def test_2025_production_data_queries(self):
        """Test queries about 2025 production data and statistics"""
        production_questions = [
            "What is the total food grain production for 2024-25?",
            "Compare rice production between Punjab and West Bengal in 2024",
            "What is the year-over-year growth in food grain production?",
            "Which state has the highest wheat production?",
            "Show me rice production statistics for 2024-25"
        ]
        
        for question in production_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have substantial answer
            assert len(data["answer"].strip()) > 30
            
            # Should have citations for production queries
            assert len(data["citations"]) > 0
            
            # Check for production-related keywords
            answer_lower = data["answer"].lower()
            production_keywords = [
                "production", "tonnes", "million", "yield", "crop", 
                "rice", "wheat", "state", "2024", "2025"
            ]
            
            keyword_found = any(keyword in answer_lower for keyword in production_keywords)
            assert keyword_found, f"No production keywords found for: {question}"
    
    def test_2025_climate_integration_queries(self):
        """Test climate data integration with agricultural context"""
        climate_questions = [
            "How did monsoon 2024 affect crop production?",
            "Correlate rainfall patterns with rice yield in West Bengal",
            "What was the impact of rainfall on wheat production in 2024?",
            "Compare rainfall and agricultural productivity across regions"
        ]
        
        for question in climate_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should provide analysis
            assert len(data["answer"].strip()) > 40
            
            # Check for climate and agriculture keywords
            answer_lower = data["answer"].lower()
            climate_keywords = [
                "rainfall", "monsoon", "climate", "weather", 
                "production", "yield", "crop", "impact"
            ]
            
            keyword_found = any(keyword in answer_lower for keyword in climate_keywords)
            assert keyword_found, f"No climate keywords found for: {question}"
    
    def test_2025_market_data_queries(self):
        """Test e-NAM and market data queries"""
        market_questions = [
            "How many traders are registered on e-NAM platform?",
            "What is the total trade value on e-NAM?",
            "How many mandis are connected to e-NAM?",
            "What crops are traded on e-NAM platform?"
        ]
        
        for question in market_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have informative answer
            assert len(data["answer"].strip()) > 20
            
            # Check for market-related keywords
            answer_lower = data["answer"].lower()
            market_keywords = [
                "e-nam", "market", "trade", "mandi", "farmer",
                "platform", "registered", "crore", "lakh"
            ]
            
            keyword_found = any(keyword in answer_lower for keyword in market_keywords)
            assert keyword_found, f"No market keywords found for: {question}"
    
    def test_query_intent_recognition(self):
        """Test that the system correctly recognizes different query intents"""
        intent_test_cases = [
            {
                "question": "Compare rice production in Punjab and Tamil Nadu",
                "expected_type": "comparison",
                "keywords": ["compare", "punjab", "tamil nadu", "rice"]
            },
            {
                "question": "What is the trend in wheat production over last 5 years?",
                "expected_type": "trend",
                "keywords": ["trend", "wheat", "years"]
            },
            {
                "question": "How does rainfall correlate with crop yield?",
                "expected_type": "correlation",
                "keywords": ["correlate", "rainfall", "yield"]
            },
            {
                "question": "What is PM Dhan-Dhaanya Krishi Yojana budget?",
                "expected_type": "policy",
                "keywords": ["pm", "dhan", "budget", "yojana"]
            }
        ]
        
        for test_case in intent_test_cases:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": test_case["question"]},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should provide relevant answer based on intent
            answer_lower = data["answer"].lower()
            
            # Check that expected keywords appear in the answer
            for keyword in test_case["keywords"]:
                assert keyword.lower() in answer_lower, \
                    f"Expected keyword '{keyword}' not found in answer for {test_case['question']}"
    
    def test_citation_quality_2025(self):
        """Test that citations include 2025-specific metadata"""
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": "What is the food grain production for 2024-25?"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have citations
        assert len(data["citations"]) > 0
        
        # Check citation structure
        for citation in data["citations"]:
            # Required fields
            required_fields = ["id", "source", "reliability"]
            for field in required_fields:
                assert field in citation, f"Missing citation field: {field}"
            
            # Reliability should be meaningful
            assert citation["reliability"] in ["High", "Verified", "Government"]
            
            # Source should be identifiable
            assert len(citation["source"]) > 0
    
    def test_data_vintage_2025(self):
        """Test that responses include correct data vintage information"""
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": "Tell me about current agriculture statistics"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have data vintage
        assert "data_vintage" in data
        assert "2025" in data["data_vintage"]
    
    def test_complex_multi_domain_queries(self):
        """Test complex queries that span multiple domains"""
        complex_questions = [
            "How do government schemes like e-NAM impact rice production statistics?",
            "What is the relationship between rainfall data and food grain production targets for 2025?",
            "Compare the effectiveness of BHARATI Initiative with traditional agricultural policies",
            "How does the PM Dhan-Dhaanya Krishi Yojana budget allocation support climate-resilient farming?"
        ]
        
        for question in complex_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Complex queries should have comprehensive answers
            assert len(data["answer"].strip()) > 100
            
            # Should have multiple citations for complex queries
            assert len(data["citations"]) >= 2
            
            # Should have good confidence for well-formed questions
            assert data["confidence_score"] > 0.3
    
    def test_performance_with_2025_features(self):
        """Test that 2025 enhancements don't significantly impact performance"""
        import time
        
        test_questions = [
            "What is the agriculture budget for 2025-26?",
            "How many farmers are on e-NAM platform?",
            "What is rice production in Punjab?"
        ]
        
        for question in test_questions:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            end_time = time.time()
            
            assert response.status_code == 200
            
            # Should respond within reasonable time
            response_time = end_time - start_time
            assert response_time < 8, f"Query took too long: {response_time:.2f}s"
            
            # Processing time should be efficient
            data = response.json()
            assert data["processing_time"] < 5, f"Processing time too high: {data['processing_time']:.2f}s"


if __name__ == "__main__":
    pytest.main(["-v", __file__])