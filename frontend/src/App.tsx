import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Tests from './pages/Tests';
import Results from './pages/Results';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tests" element={<Tests />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
