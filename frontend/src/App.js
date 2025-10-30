import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Search, 
  Send, 
  Loader, 
  CheckCircle, 
  AlertCircle, 
  BarChart3,
  ExternalLink,
  Clock,
  Database,
  Sparkles,
  Wheat,
  CloudRain,
  TrendingUp
} from 'lucide-react';
import './App.css';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [stats, setStats] = useState(null);
  
  // Sample questions categorized by type
  const sampleQuestions = {
    policy: [
      "What is the budget allocation for PM Dhan-Dhaanya Krishi Yojana?",
      "How many farmers are registered on e-NAM platform in 2025?",
      "What are the key features of BHARATI Initiative for agri-tech startups?"
    ],
    production: [
      "Compare rice production in Punjab and West Bengal for 2024",
      "What is the total food grain production in India for 2024-25?",
      "Which state has the highest wheat production in India?"
    ],
    climate: [
      "Correlate rainfall patterns with crop yield in Maharashtra", 
      "What was the monsoon performance in 2024 across different regions?",
      "How does rainfall affect rice production in West Bengal?"
    ],
    trends: [
      "Analyze rice production trend in West Bengal over last decade",
      "What is the year-over-year growth in food grain production?",
      "Show irrigation coverage trends across major agricultural states"
    ]
  };

  // Fetch system health on component mount
  useEffect(() => {
    fetchSystemHealth();
    fetchSystemStats();
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const result = await axios.get(`${API_BASE_URL}/health`);
      setSystemHealth(result.data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const fetchSystemStats = async () => {
    try {
      const result = await axios.get(`${API_BASE_URL}/stats`);
      setStats(result.data);
    } catch (error) {
      console.error('Stats fetch failed:', error);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      const result = await axios.post(`${API_BASE_URL}/query`, {
        question: question.trim(),
        include_policy_context: true,
        max_results: 5
      });
      
      setResponse(result.data);
    } catch (error) {
      console.error('Query error:', error);
      setError(
        error.response?.data?.detail || 
        'Failed to process your question. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuestion = (sampleQ) => {
    setQuestion(sampleQ);
    setError(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <Wheat size={32} className="text-primary" />
            </div>
            <div>
              <h1 className="app-title">🌾 Project Samarth</h1>
              <p className="app-subtitle">
                Intelligent Q&A System for Indian Agricultural Data
              </p>
            </div>
          </div>
          
          {/* System Status */}
          <div className="system-status">
            {systemHealth && (
              <div className={`status-badge ${systemHealth.status}`}>
                {systemHealth.status === 'healthy' ? (
                  <CheckCircle size={16} />
                ) : (
                  <AlertCircle size={16} />
                )}
                <span>{systemHealth.status.toUpperCase()}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container">
        {/* Stats Cards */}
        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <Database size={20} className="stat-icon" />
              <div>
                <div className="stat-value">353.96M</div>
                <div className="stat-label">Tonnes Food Grain (2024-25)</div>
              </div>
            </div>
            <div className="stat-card">
              <TrendingUp size={20} className="stat-icon" />
              <div>
                <div className="stat-value">₹1.38L Cr</div>
                <div className="stat-label">Agriculture Budget 2025-26</div>
              </div>
            </div>
            <div className="stat-card">
              <BarChart3 size={20} className="stat-icon" />
              <div>
                <div className="stat-value">1.79 Cr</div>
                <div className="stat-label">e-NAM Registered Farmers</div>
              </div>
            </div>
            <div className="stat-card">
              <CloudRain size={20} className="stat-icon" />
              <div>
                <div className="stat-value">1901-2024</div>
                <div className="stat-label">IMD Climate Data Range</div>
              </div>
            </div>
          </div>
        )}

        {/* Query Section */}
        <div className="query-section">
          <div className="query-header">
            <Search size={24} className="query-icon" />
            <h2>Ask About Indian Agriculture</h2>
          </div>
          
          <div className="query-input-container">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., Compare rice production in Punjab and Tamil Nadu for 2024, or ask about government schemes like PM Dhan-Dhaanya Krishi Yojana..."
              rows={4}
              className="query-input"
              disabled={loading}
            />
            <button 
              onClick={handleQuery} 
              disabled={loading || !question.trim()}
              className="query-button"
            >
              {loading ? (
                <><Loader className="spinner" size={16} /> Processing...</>
              ) : (
                <><Send size={16} /> Get Answer</>
              )}
            </button>
          </div>
        </div>

        {/* Sample Questions */}
        <div className="samples-section">
          <h3>Sample Questions by Category:</h3>
          
          {Object.entries(sampleQuestions).map(([category, questions]) => (
            <div key={category} className="sample-category">
              <h4 className="category-title">
                {category === 'policy' && <Sparkles size={16} />}
                {category === 'production' && <Wheat size={16} />}
                {category === 'climate' && <CloudRain size={16} />}
                {category === 'trends' && <TrendingUp size={16} />}
                {category.charAt(0).toUpperCase() + category.slice(1)} Questions
              </h4>
              <div className="sample-questions">
                {questions.map((q, idx) => (
                  <div 
                    key={idx} 
                    className="sample-question" 
                    onClick={() => handleSampleQuestion(q)}
                  >
                    {q}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-section">
            <AlertCircle size={20} />
            <div>
              <h4>Error Processing Query</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Response Section */}
        {response && (
          <div className="response-section">
            <div className="response-header">
              <CheckCircle size={20} className="text-success" />
              <h3>Answer</h3>
              <div className="response-meta">
                <Clock size={14} />
                <span>{response.processing_time?.toFixed(2)}s</span>
                <span className="confidence-score">
                  Confidence: {(response.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            
            <div className="answer-content">
              {response.answer}
            </div>
            
            {/* Policy Context */}
            {response.policy_context && response.policy_context.length > 0 && (
              <div className="policy-context">
                <h4><Sparkles size={16} /> Government Policy Context</h4>
                <div className="policy-grid">
                  {response.policy_context.map((policy, idx) => (
                    <div key={idx} className="policy-card">
                      <h5>{policy.scheme}</h5>
                      <p><strong>Budget:</strong> {policy.budget}</p>
                      <p><strong>Year:</strong> {policy.year}</p>
                      <p><strong>Category:</strong> {policy.category}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Citations */}
            {response.citations && response.citations.length > 0 && (
              <div className="citations-section">
                <h4><Database size={16} /> Data Sources & Citations</h4>
                <div className="citations-grid">
                  {response.citations.map((cite, idx) => (
                    <div key={idx} className="citation-card">
                      <div className="citation-header">
                        <span className="citation-id">[Source {cite.id}]</span>
                        <span className={`reliability-badge ${cite.reliability?.toLowerCase()}`}>
                          {cite.reliability}
                        </span>
                      </div>
                      <div className="citation-details">
                        <p><strong>Source:</strong> {cite.source}</p>
                        {cite.state !== 'N/A' && (
                          <p><strong>State:</strong> {cite.state}</p>
                        )}
                        {cite.year !== 'N/A' && (
                          <p><strong>Year:</strong> {cite.year}</p>
                        )}
                        <p><strong>Category:</strong> {cite.category}</p>
                        {cite.url !== 'N/A' && (
                          <a 
                            href={cite.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="citation-link"
                          >
                            <ExternalLink size={14} />
                            View Source
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="data-vintage">
              <span className="vintage-badge">
                Data Vintage: {response.data_vintage}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>🌾 Built for Indian Agriculture</h4>
            <p>Empowering farmers and policymakers with data-driven insights</p>
          </div>
          
          <div className="footer-section">
            <h4>🔒 Data Sovereignty</h4>
            <p>All government data processed locally for security</p>
          </div>
          
          <div className="footer-section">
            <h4>🇮🇳 Made in India</h4>
            <p>Supporting Atmanirbhar Bharat initiative</p>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>© 2025 Project Samarth by Ravi Kumar Bharti • 
            <a href="https://github.com/rkbharti/project-samarth" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={14} /> GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;