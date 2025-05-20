import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Results: React.FC = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const response = await axios.get('/api/results');
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  return (
    <div className="results-page">
      <h1>Результаты тестов</h1>
      <div className="results-list">
        {results.map((result) => (
          <div key={result.id} className="result-item">
            <h3>{result.testName}</h3>
            <p>Оценка: {result.score}</p>
            <p>Дата: {new Date(result.date).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Results;
