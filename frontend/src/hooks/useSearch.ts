import { useState, useCallback } from 'react';
import { searchWikipedia, searchArxiv } from '../services/api';
import { SearchResult } from '../types';

export function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeSource, setActiveSource] = useState<'wikipedia' | 'arxiv'>('wikipedia');

  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      let data: SearchResult[];
      if (activeSource === 'wikipedia') {
        data = await searchWikipedia(query);
      } else {
        data = await searchArxiv(query);
      }
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [activeSource]);

  const clearResults = useCallback(() => setResults([]), []);

  return { results, loading, activeSource, setActiveSource, search, clearResults };
}