import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-item">
          School Testing
        </Link>
      </div>
      <div className="navbar-menu">
        <Link to="/tests" className="navbar-item">Тесты</Link>
        <Link to="/results" className="navbar-item">Результаты</Link>
      </div>
    </nav>
  );
};

export default Navbar;
