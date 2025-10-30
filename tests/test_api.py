#!/usr/bin/env python3
"""
API Tests for Project Samarth

Run with: python -m pytest tests/test_api.py -v
"""

import pytest
import requests
import time
from typing import Dict, Any

# Test Configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds

class TestProjectSamarthAPI:
    """Test suite for Project Samarth API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test"""
        # Verify API is running
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API is not running or unhealthy")
        except requests.RequestException:
            pytest.skip("API is not accessible")
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Project Samarth" in data["message"]
        assert "version" in data
        assert "features" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "vectorstore_loaded" in data
        assert "total_documents" in data
        assert "version" in data
        
        # Status should be healthy or degraded
        assert data["status"] in ["healthy", "degraded"]
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = requests.get(f"{API_BASE_URL}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_info" in data
        assert "data_sources" in data
        assert "capabilities" in data
        
        # Check system info
        system_info = data["system_info"]
        assert "version" in system_info
        assert "framework" in system_info
    
    def test_query_endpoint_basic(self):
        """Test basic query functionality"""
        test_question = "What is the total food grain production in India?"
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": test_question},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert "processing_time" in data
        assert "confidence_score" in data
        assert "data_vintage" in data
        
        # Answer should not be empty
        assert len(data["answer"].strip()) > 0
        
        # Processing time should be reasonable
        assert 0 < data["processing_time"] < 30
        
        # Confidence score should be between 0 and 1
        assert 0 <= data["confidence_score"] <= 1
    
    def test_query_with_policy_context(self):
        """Test query with policy context enabled"""
        test_question = "What is PM Dhan-Dhaanya Krishi Yojana?"
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={
                "question": test_question,
                "include_policy_context": True,
                "max_results": 3
            },
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "policy_context" in data
        
        # Should have policy context for policy-related questions
        if data["policy_context"]:
            policy = data["policy_context"][0]
            assert "scheme" in policy
            assert "budget" in policy
            assert "year" in policy
    
    def test_query_agriculture_production(self):
        """Test agriculture production related queries"""
        test_questions = [
            "Compare rice production in Punjab and West Bengal",
            "What is wheat production in Uttar Pradesh?",
            "Show food grain production statistics for 2024-25"
        ]
        
        for question in test_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["answer"].strip()) > 0
            
            # Should have citations for data-driven queries
            assert len(data["citations"]) > 0
    
    def test_query_climate_data(self):
        """Test climate and rainfall related queries"""
        test_questions = [
            "What was the monsoon performance in 2024?",
            "Compare rainfall in different regions of India",
            "How does rainfall affect crop production?"
        ]
        
        for question in test_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["answer"].strip()) > 0
    
    def test_query_government_schemes(self):
        """Test government schemes and policy queries"""
        test_questions = [
            "What is the budget for e-NAM platform?",
            "How many farmers are registered on e-NAM?",
            "What is BHARATI Initiative?"
        ]
        
        for question in test_questions:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["answer"].strip()) > 0
    
    def test_query_invalid_input(self):
        """Test query endpoint with invalid input"""
        # Empty question
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": ""},
            timeout=TEST_TIMEOUT
        )
        
        # Should either succeed with a helpful message or return 400
        assert response.status_code in [200, 400]
        
        # Missing question field
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_query_response_format(self):
        """Test that query responses have correct format"""
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": "Tell me about rice production"},
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "answer", "citations", "policy_context", 
            "processing_time", "confidence_score", "data_vintage"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["citations"], list)
        assert isinstance(data["policy_context"], list)
        assert isinstance(data["processing_time"], (int, float))
        assert isinstance(data["confidence_score"], (int, float))
        assert isinstance(data["data_vintage"], str)
        
        # Check citation format if citations exist
        if data["citations"]:
            citation = data["citations"][0]
            citation_fields = ["id", "source", "reliability"]
            for field in citation_fields:
                assert field in citation
    
    def test_concurrent_queries(self):
        """Test handling of concurrent queries"""
        import concurrent.futures
        import threading
        
        def make_query(question_id):
            question = f"What is agriculture production data? Query {question_id}"
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                timeout=TEST_TIMEOUT
            )
            return response.status_code == 200
        
        # Run 5 concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All queries should succeed
        assert all(results), "Some concurrent queries failed"
    
    def test_performance_benchmarks(self):
        """Test API performance benchmarks"""
        # Simple query performance
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": "What is rice production in India?"},
            timeout=TEST_TIMEOUT
        )
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond within reasonable time
        response_time = end_time - start_time
        assert response_time < 10, f"Query took too long: {response_time:.2f}s"
        
        # Check processing time reported by API
        data = response.json()
        assert data["processing_time"] < 5, f"Processing time too high: {data['processing_time']:.2f}s"


if __name__ == "__main__":
    # Run tests directly
    pytest.main(["-v", __file__])