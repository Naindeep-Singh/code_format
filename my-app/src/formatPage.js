import React, { useState } from "react";
import "./App.css";
import axios from "axios";

function FormatPage() {
  const [code, setCode] = useState("");

  const handleChange = (event) => {
    setCode(event.target.value);

    // // Automatically adjust the height of the textarea
    // event.target.style.height = "auto";
    // event.target.style.height = event.target.scrollHeight + "px";
  };

  const formatCode = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/formatCode", {
        source_code: code,
      });
      setCode(response.data.formatted_code);

      // Adjusting height automatically, not working
      // response.data.style.height = "auto";
      // response.data.style.height = response.data.scrollHeight + "px";
    } catch (error) {
      console.error("Error formatting code:", error);
    }
  };

  const clearCode = () => {
    setCode("");
  };

  return (
    <>
      <div className="App">
        <h1>Code Formatter</h1>
        <div className="container">
          <button onClick={formatCode}>Format</button>
          <button onClick={clearCode}>Clear</button>
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
