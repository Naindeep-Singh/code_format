import React from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FormatPage from "./formatPage";
import AstPage from "./astPage";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/format" element={<FormatPage />} />
        <Route path="/ast" element={<AstPage />} />
      </Routes>
    </Router>
  );
};

export default App;
