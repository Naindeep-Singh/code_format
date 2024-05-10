import React from "react";
import { Link } from "react-router-dom"; // Import Link from react-router-dom
import "./landingPage.css";

function LandingPage() {
  return (
    <>
      <div className="LApp">
        <h1 className="heading">C Code Formatter and AST Visualizer</h1>
        <div className="button-container">
          <Link to="/ast">
            <button>Generate AST</button>
          </Link>
          <Link to="/format">
            <button>Format Code</button>
          </Link>
        </div>
      </div>
    </>
  );
}

export default LandingPage;
