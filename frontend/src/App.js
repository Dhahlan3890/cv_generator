import React from 'react';
import Uploader from './FileUpload/uploader';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Visualizer from './FileUpload/visualizer';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Uploader />} />
        <Route path="/visualizer" element={<Visualizer />} />
      </Routes>
    </Router>
  );
}

export default App;