import React from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FormatPage from "./formatPage";
import AstPage from "./astPage";
import LandingPage from "./landingPage";

const App = () => {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<LandingPage />} />
        <Route path="/format" element={<FormatPage />} />
        <Route path="/ast" element={<AstPage />} />
      </Routes>
    </Router>
  );
};

export default App;
