import React, { useState, useRef } from "react";
import "./App.css"; // Assuming you have a separate App.css file
import axios from "axios";

const AstPage = () => {
  const [code, setCode] = useState("");
  const [txt,setTxt] = useState("")
  const [imageSrc, setImageSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const codeRef = useRef();

  const handleChange = (event) => {
    setCode(event.target.value);
  };

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/generateAST",
        {
          code: codeRef.current.value,
        },
        { responseType: "arraybuffer" }
      );
      const base64 = btoa(
        new Uint8Array(response.data).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ""
        )
      );
      const src = `data:image/png;base64,${base64}`;
      setImageSrc(src);
    } catch (error) {
      console.error("Error fetching AST data:", error);
    } finally {
      setIsLoading(false);
      astText();
    }
  };

  const astText = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/generateasttext",
        {
          code: codeRef.current.value,
        }
      );
      setCode(response.data.ast_code);
      setTxt("Simplified AST")
    } catch (error) {
      console.error("Error generating ast text:", error);
    }
  };

  return (
    <div className="ast-page">
      <h1>AST Generator</h1> {/* New class for AstPage styles */}
      <div className="acontainer">
        {" "}
        {/* Assuming you have a container class */}
        <textarea ref={codeRef} placeholder="Enter your code here..." />
      </div>
      <button onClick={fetchData} disabled={isLoading}>
        {isLoading ? "Loading..." : "Generate AST"}
      </button>
      <h3>{txt}</h3>
      <div className="img">{imageSrc && <img src={imageSrc} alt="AST" />}</div>
      <h3>AST</h3>
      <div className="acontainer">
        {" "}
        {/* Assuming you have a container class */}
        <textarea value={code} onChange={handleChange} readOnly placeholder="The AST will appear here"/>
      </div>
    </div>
  );
};

export default AstPage;
