import { useState, useRef, useEffect } from "react";

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastReport, setLastReport] = useState(null);

  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const handleSend = async () => {
    if (!input) return;

    setChat((prev) => [...prev, { role: "user", text: input }]);
    setLoading(true);

    try {
      let res, data;

      if (lastReport) {
        res = await fetch("http://127.0.0.1:8000/ask-followup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: input,
            report: lastReport,
          }),
        });

        data = await res.json();

        setChat((prev) => [
          ...prev,
          { role: "ai", text: data.answer },
        ]);
      } else {
        res = await fetch("http://127.0.0.1:8000/generate-report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: input }),
        });

        data = await res.json();
        setLastReport(data);

        setChat((prev) => [
          ...prev,
          { role: "ai", data: data },
        ]);
      }
    } catch {
      alert("Backend error");
    }

    setInput("");
    setLoading(false);
  };

  return (
    <div className="bg-[#0b0f19] text-gray-200 min-h-screen flex flex-col">

      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 text-sm text-gray-400">
        AI Research Assistant
      </div>

      {/* Chat */}
      <div className="flex-1 overflow-y-auto max-w-2xl mx-auto w-full px-4 py-8 space-y-8">

        {chat.length === 0 && (
          <div className="text-center mt-32 text-gray-500 text-xl">
            Ask anything...
          </div>
        )}

        {chat.map((msg, i) =>
          msg.role === "user" ? (
            <div key={i} className="text-right">
              <div className="inline-block bg-gray-800 px-4 py-2 rounded-xl">
                {msg.text}
              </div>
            </div>
          ) : (
            <div key={i} className="space-y-6 leading-relaxed">

              {/* Follow-up */}
              {msg.text && (
                <p className="text-gray-300 whitespace-pre-wrap">
                  {msg.text}
                </p>
              )}

              {/* Sections */}
              {msg.data &&
                Object.entries(msg.data.sections || {}).map(
                  ([key, value]) => (
                    <div key={key}>
                      <h2 className="text-lg font-semibold text-white mb-2">
                        {key}
                      </h2>
                      <p className="text-gray-400 whitespace-pre-wrap">
                        {value}
                      </p>
                    </div>
                  )
                )}

              {/* Perspectives */}
              {msg.data && (
                <div>
                  <h2 className="text-lg font-semibold text-white mb-2">
                    Perspectives
                  </h2>
                  <p className="text-gray-400 whitespace-pre-wrap">
                    {msg.data.perspectives}
                  </p>
                </div>
              )}

              {/* Analysis */}
              {msg.data && (
                <div>
                  <h2 className="text-lg font-semibold text-white mb-2">
                    Critical Analysis
                  </h2>
                  <p className="text-gray-400 whitespace-pre-wrap">
                    {msg.data.critical_analysis}
                  </p>
                </div>
              )}
            </div>
          )
        )}

        {loading && <p className="text-center text-gray-500">Thinking...</p>}

        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-4 bg-[#0b0f19]">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 bg-gray-800 px-4 py-3 rounded-xl outline-none text-white placeholder-gray-500"
          />
          <button
            onClick={handleSend}
            className="bg-white text-black px-5 rounded-xl font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;