import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastReport, setLastReport] = useState(null);
  const [customFormat, setCustomFormat] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  
  useEffect(() => {
    console.log("CHAT STATE:", chat);
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
        console.log("FOLLOWUP RESPONSE:", data);

        setChat((prev) => [
          ...prev,
          { role: "ai", text: data.answer || "No answer returned." },
        ]);
      } else {
        
        res = await fetch("http://127.0.0.1:8000/generate-report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: input }),
          custom_format: customFormat || null,
        });

        data = await res.json();
        console.log("REPORT RESPONSE:", data);

        
        if (data.error) {
          setChat((prev) => [
            ...prev,
            { role: "ai", text: " Error: " + data.error },
          ]);
          return;
        }

        
        if (!data.sections || Object.keys(data.sections).length === 0) {
          setChat((prev) => [
            ...prev,
            {
              role: "ai",
              text: " No content generated. Try another topic.",
            },
          ]);
          return;
        }

        setLastReport(data);

        setChat((prev) => [...prev, { role: "ai", data: data }]);
      }
    } catch (err) {
      console.error(err);
      setChat((prev) => [
        ...prev,
        { role: "ai", text: " Backend connection failed." },
      ]);
    }

    setInput("");
    setLoading(false);
  };

  
  const handleNewChat = () => {
    setChat([]);
    setLastReport(null);
    setCustomFormat("");
  };

  
  const handleDownloadPDF = async () => {
    if (!lastReport) return;

    try {
      const res = await fetch("http://127.0.0.1:8000/download-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(lastReport),
      });

      
      if (!res.ok) {
        const err = await res.json();
        alert("PDF Error: " + err.error);
        return;
      }

      const blob = await res.blob();

      
      if (blob.type !== "application/pdf") {
        alert("Invalid PDF received");
        return;
      }

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "research_report.pdf";
      a.click();

      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Failed to download PDF");
    }
  };
  return (
    <div className="bg-[#0b0f19] text-gray-200 min-h-screen flex flex-col">
      
      <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center text-sm text-gray-400">
        <div className="flex gap-4 items-center">
          <span>AI Research Assistant</span>

          {lastReport && (
            <button
              onClick={handleDownloadPDF}
              className="text-xs bg-gray-700 px-2 py-1 rounded hover:bg-gray-600"
            >
              Download PDF
            </button>
          )}
        </div>

        <button onClick={handleNewChat} className="text-xs hover:text-white">
          New Chat
        </button>
      </div>

      
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
              
              <div className="text-right">
                <button
                  onClick={() =>
                    navigator.clipboard.writeText(
                      msg.text || JSON.stringify(msg.data),
                    )
                  }
                  className="text-xs text-gray-500 hover:text-white"
                >
                  Copy
                </button>
              </div>

              
              {msg.text && (
                <div className="prose prose-invert">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.text}
                  </ReactMarkdown>
                </div>
              )}

              
              {msg.data?.sections &&
                Object.entries(msg.data.sections).map(([key, value]) => (
                  <div key={key}>
                    <h2 className="text-lg font-semibold text-white mb-2">
                      {key}
                    </h2>
                    <div className="prose prose-invert text-gray-400">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {value || "No content"}
                      </ReactMarkdown>
                    </div>
                  </div>
                ))}

              
              {msg.data?.perspectives && (
                <div>
                  <h2 className="text-lg font-semibold text-white mb-2">
                    Perspectives
                  </h2>
                  <div className="prose prose-invert text-gray-400">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.data.perspectives}
                    </ReactMarkdown>
                  </div>
                </div>
              )}

              
              {msg.data?.critical_analysis && (
                <div>
                  <h2 className="text-lg font-semibold text-white mb-2">
                    Critical Analysis
                  </h2>
                  <div className="prose prose-invert text-gray-400">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.data.critical_analysis}
                    </ReactMarkdown>
                  </div>
                </div>
              )}

              
              {msg.data?.references?.length > 0 && (
                <div>
                  <h2 className="text-lg font-semibold text-white mb-2">
                    References
                  </h2>
                  <div className="space-y-1 text-sm text-gray-500">
                    {msg.data.references.map((ref) => (
                      <div key={ref.id}>
                        {ref.id}.{" "}
                        <a
                          href={ref.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-400 hover:underline"
                        >
                          {ref.title}
                        </a>{" "}
                        ({ref.source})
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ),
        )}

        
        {loading && (
          <div className="text-center text-gray-400 animate-pulse">
             Generating research...
          </div>
        )}

        <div ref={endRef} />
      </div>

      
      <div className="border-t border-gray-800 p-4 bg-[#0b0f19]">
        <div className="max-w-2xl mx-auto flex flex-col gap-2">
          <textarea
            value={customFormat}
            onChange={(e) => setCustomFormat(e.target.value)}
            placeholder="Paste research format (college format)"
            className="w-full bg-gray-800 px-4 py-2 rounded-xl text-white placeholder-gray-500 outline-none"
          />

          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
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
    </div>
  );
}

export default App;
