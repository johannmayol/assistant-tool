import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [message, setMessage] = useState("Chargement...");

  useEffect(() => {
    axios.get(`${API_URL}/`)
    .then(response => setMessage(response.data.message))
    .catch(error => setMessage("Erreur de connexion au backend"));
  }, []);

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Assistant Intelligent</h1>
      <p>{message}</p>
    </div>
  );
}

async function searchWeb(query) {
  const response = await fetch(`${API_URL}/search_web/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  const data = await response.json();
  console.log("Résultats de la recherche :", data.results);
}


export default App;
