import { useState } from "react";

function App() {
  const [task, setTask] = useState("génération de texte");
  const [inputData, setInputData] = useState("");
  const [output, setOutput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    const response = await fetch("http://localhost:8000/dispatch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task, input_data: inputData }),
    });

    const data = await response.json();
    setOutput(data.generated_text || data.summary || data.error);
    setHistory([{ task, inputData, output: data.generated_text || data.summary }, ...history]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-6">
      {/* Sélection de la tâche */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold">Assistant IA</h1>
        <select
          className="mt-2 p-2 border rounded"
          value={task}
          onChange={(e) => setTask(e.target.value)}
        >
          <option value="génération de texte">Génération de texte</option>
          <option value="résumé">Résumé</option>
          <option value="workflow n8n">Exécuter un workflow n8n</option>
        </select>
      </div>

      {/* Zone de saisie */}
      <textarea
        className="w-2/3 p-2 border rounded"
        rows="4"
        placeholder="Tape ta requête ici..."
        value={inputData}
        onChange={(e) => setInputData(e.target.value)}
      />

      <button
        className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "En cours..." : "Envoyer"}
      </button>

      {/* Affichage du résultat */}
      <div className="mt-6 w-2/3 bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold">Réponse IA :</h2>
        <p className="mt-2">{output || "Aucune réponse pour le moment."}</p>
      </div>

      {/* Historique des requêtes */}
      <div className="mt-6 w-2/3">
        <h2 className="text-lg font-semibold">Historique :</h2>
        <ul className="mt-2 space-y-2">
          {history.map((item, index) => (
            <li key={index} className="p-2 bg-gray-200 rounded">
              <strong>{item.task} :</strong> {item.inputData} → <em>{item.output}</em>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
export default App;
