import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Tests: React.FC = () => {
  const [tests, setTests] = useState([]);

  useEffect(() => {
    fetchTests();
  }, []);

  const fetchTests = async () => {
    try {
      const response = await axios.get('/api/tests');
      setTests(response.data);
    } catch (error) {
      console.error('Error fetching tests:', error);
    }
  };

  return (
    <div className="tests-page">
      <h1>Список тестов</h1>
      <div className="tests-list">
        {tests.map((test) => (
          <div key={test.id} className="test-item">
            <h3>{test.name}</h3>
            <p>{test.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tests;
