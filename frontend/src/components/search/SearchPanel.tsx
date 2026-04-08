import React, { useState } from 'react';
import { useSearch } from '../../hooks/useSearch';

const SearchPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const { results, loading, activeSource, setActiveSource, search, clearResults } = useSearch();

  const handleSearch = () => {
    if (query.trim()) {
      search(query);
    }
  };

  return (
    <div className="search-panel">
      <div className="search-header">
        <h3>🔍 Search Knowledge Sources</h3>
        <div className="source-toggle">
          <button
            className={activeSource === 'wikipedia' ? 'active' : ''}
            onClick={() => setActiveSource('wikipedia')}
          >
            📖 Wikipedia
          </button>
          <button
            className={activeSource === 'arxiv' ? 'active' : ''}
            onClick={() => setActiveSource('arxiv')}
          >
            🔬 arXiv
          </button>
        </div>
      </div>

      <div className="search-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Search ${activeSource === 'wikipedia' ? 'Wikipedia' : 'arXiv'}...`}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? '...' : 'Search'}
        </button>
        {results.length > 0 && (
          <button onClick={clearResults} className="clear-btn">Clear</button>
        )}
      </div>

      {loading && <div className="search-loading">Searching...</div>}

      {results.length > 0 && (
        <div className="search-results">
          {results.map((result, idx) => (
            <div key={idx} className="search-result">
              <div className="result-header">
                <h4>{result.title}</h4>
                <span className="relevance">{Math.round(result.relevance * 100)}%</span>
              </div>
              <p>{result.summary.substring(0, 200)}...</p>
              <a href={result.url} target="_blank" rel="noopener noreferrer">
                Read more →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchPanel;