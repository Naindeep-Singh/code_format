import React, { useState } from "react";
import "./App.css";
import axios from "axios";

function FormatPage() {
  const [code, setCode] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("C");

  const handleChange = (event) => {
    setCode(event.target.value);
  };

  const formatCode = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/formatCode", {
        source_code: code,
      });
      setCode(response.data.formatted_code);
    } catch (error) {
      console.error("Error formatting code:", error);
    }
  };

  const clearCode = () => {
    setCode("");
  };

  const handleLanguageChange = (event) => {
    setSelectedLanguage(event.target.value);
  };

  return (
    <>
      <div className="App">
        <h1>Code Formatter</h1>
        <div className="container">
          <div>
            <button onClick={formatCode}>Format</button>
            <button onClick={clearCode}>Clear</button>
          </div>

          <div className="langSelect">
            <p>Choose language:</p>
            <select
              value={selectedLanguage}
              onChange={handleLanguageChange}
              className="styled-select"
            >
              <option value="C">C</option>
              <option value="C++">C++</option>
            </select>
          </div>
        </div>

        <textarea
          value={code}
          onChange={handleChange}
          placeholder="Enter your code here..."
        ></textarea>
      </div>
    </>
  );
}

export default FormatPage;
