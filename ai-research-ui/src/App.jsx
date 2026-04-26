import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const SUGGESTED_TOPICS = [
  "Impact of AI on healthcare",
  "Climate change and renewable energy",
  "Transformer neural networks",
  "Mental health in teenagers",
];

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastReport, setLastReport] = useState(null);
  const [customFormat, setCustomFormat] = useState("");
  const [showFormat, setShowFormat] = useState(false);
  const [loadingText, setLoadingText] = useState("Searching sources...");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  useEffect(() => {
    if (!loading) return;
    const messages = [
      "Searching sources...",
      "Reading articles...",
      "Analysing research...",
      "Writing report...",
      "Almost done...",
    ];
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % messages.length;
      setLoadingText(messages[i]);
    }, 3000);
    return () => clearInterval(interval);
  }, [loading]);

  const handleSend = async (topicOverride = null) => {
    const userInput = topicOverride || input;
    if (!userInput.trim()) return;

    setInput("");
    setChat((prev) => [...prev, { role: "user", text: userInput }]);
    setLoading(true);

    try {
      let res, data;

      if (lastReport) {
        res = await fetch(`${API}/ask-followup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: userInput, report: lastReport }),
        });
        data = await res.json();
        setChat((prev) => [
          ...prev,
          { role: "ai", text: data.answer || "No answer returned." },
        ]);
      } else {
        res = await fetch(`${API}/generate-report`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            topic: userInput,
            custom_format: customFormat || "",
          }),
        });
        data = await res.json();

        if (data.type === "comparison") {
          setLastReport(data);
          setChat((prev) => [...prev, { role: "ai", data: data }]);
          return;
        }

        if (!data.sections || Object.keys(data.sections).length === 0) {
          setChat((prev) => [
            ...prev,
            {
              role: "ai",
              text: "No content generated. Please try another topic.",
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
        {
          role: "ai",
          text: "Could not connect to server. Please make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
      setLoadingText("Searching sources...");
    }
  };

  const renderWithCitations = (text, references) => {
    let str = "";
    if (typeof text === "string") str = text;
    else if (Array.isArray(text))
      str = text.map((i) => (typeof i === "string" ? i : "")).join("");
    else return text;

    const parts = str.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const refId = parseInt(match[1]);
        const ref = references?.find((r) => r.id === refId);
        if (ref) {
          return (
            <a
              key={i}
              href={ref.url}
              target="_blank"
              rel="noreferrer"
              title={ref.title}
              className="text-blue-400 hover:underline font-mono text-xs mx-0.5"
            >
              [{refId}]
            </a>
          );
        }
      }
      return part;
    });
  };

  const handleNewChat = () => {
    setChat([]);
    setLastReport(null);
    setCustomFormat("");
    setShowFormat(false);
  };

  const handleDownload = async (type) => {
    if (!lastReport) return;
    try {
      const res = await fetch(`${API}/download-${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: lastReport.topic,
          sections: lastReport.sections,
        }),
      });
      if (!res.ok) {
        alert(`${type.toUpperCase()} download failed`);
        return;
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `research_report.${type === "pdf" ? "pdf" : "docx"}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert(`Failed to download ${type.toUpperCase()}`);
    }
  };

  return (
    <div
      className="bg-[#0f0f0f] text-gray-300 min-h-screen flex flex-col"
      style={{ fontFamily: "'Georgia', serif" }}
    >
      <header className="border-b border-white/8 bg-[#0f0f0f] sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-8 py-5 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <span className="text-white font-semibold text-sm tracking-widest uppercase">
              Research Agent
            </span>
            {lastReport?.domain && (
              <span className="text-xs text-gray-500 border border-white/10 px-2 py-0.5 rounded">
                {lastReport.domain}
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            {lastReport && (
              <>
                <button
                  onClick={() => handleDownload("pdf")}
                  className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/25 px-3 py-1.5 rounded transition-all"
                >
                  Download PDF
                </button>
                <button
                  onClick={() => handleDownload("docx")}
                  className="text-xs text-white bg-white/10 hover:bg-white/15 border border-white/15 px-3 py-1.5 rounded transition-all"
                >
                  Download Word
                </button>
              </>
            )}
            {chat.length > 0 && (
              <button
                onClick={handleNewChat}
                className="text-xs text-gray-500 hover:text-white transition-colors"
              >
                New Chat
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-8 py-10 space-y-10">
          {chat.length === 0 && (
            <div className="mt-20 space-y-10">
              <div className="space-y-2">
                <h1 className="text-2xl text-white font-semibold">
                  What would you like to research?
                </h1>
                <p className="text-gray-500 text-sm">
                  Generate full academic research papers on any topic — medical,
                  technology, law, finance, history, and more.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {SUGGESTED_TOPICS.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => handleSend(topic)}
                    className="text-left text-sm text-gray-400 hover:text-white border border-white/8 hover:border-white/20 px-4 py-3 rounded-lg transition-all bg-white/2 hover:bg-white/5"
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {chat.map((msg, i) =>
            msg.role === "user" ? (
              <div key={i} className="flex justify-end">
                <div className="bg-white/6 border border-white/10 text-white px-5 py-3 rounded-lg max-w-lg text-sm leading-relaxed">
                  {msg.text}
                </div>
              </div>
            ) : (
              <div key={i} className="space-y-6">
                {msg.text && (
                  <div className="text-sm text-gray-300 leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p({ children }) {
                          return (
                            <p className="mb-3 last:mb-0">
                              {renderWithCitations(
                                children,
                                lastReport?.references,
                              )}
                            </p>
                          );
                        },
                        a({ href, children }) {
                          return (
                            <a
                              href={href}
                              target="_blank"
                              rel="noreferrer"
                              className="text-blue-400 underline"
                            >
                              {children}
                            </a>
                          );
                        },
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>
                )}

                {msg.data?.type === "comparison" && msg.data?.result && (
                  <div className="space-y-4">
                    <div className="border-b border-white/8 pb-3">
                      <p className="text-xs uppercase tracking-widest text-gray-500 mb-1">
                        Comparison
                      </p>
                      <h2 className="text-white text-lg font-semibold">
                        {msg.data.topic}
                      </h2>
                    </div>
                    <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.data.result}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {msg.data?.sections && (
                  <div className="flex gap-4 text-xs text-gray-600 border-b border-white/5 pb-4">
                    <span>
                      {Object.keys(msg.data.sections).length} sections
                    </span>
                    {msg.data.domain && <span>{msg.data.domain}</span>}
                    {msg.data.source && <span>via {msg.data.source}</span>}
                    <button
                      onClick={() =>
                        navigator.clipboard.writeText(JSON.stringify(msg.data))
                      }
                      className="ml-auto hover:text-gray-400 transition-colors"
                    >
                      Copy
                    </button>
                  </div>
                )}

                {msg.data?.sections &&
                  Object.entries(msg.data.sections).map(([key, value]) => (
                    <div key={key} className="space-y-3">
                      <h2 className="text-white text-sm font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                        {key}
                      </h2>
                      <div className="text-sm text-gray-300 leading-relaxed">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p({ children }) {
                              return (
                                <p className="mb-3 last:mb-0">
                                  {renderWithCitations(
                                    children,
                                    msg.data?.references,
                                  )}
                                </p>
                              );
                            },
                            table({ children }) {
                              return (
                                <div className="overflow-x-auto my-4">
                                  <table className="w-full text-xs border-collapse border border-white/10">
                                    {children}
                                  </table>
                                </div>
                              );
                            },
                            th({ children }) {
                              return (
                                <th className="border border-white/10 bg-white/5 px-4 py-2 text-left text-white font-medium">
                                  {children}
                                </th>
                              );
                            },
                            td({ children }) {
                              return (
                                <td className="border border-white/10 px-4 py-2">
                                  {children}
                                </td>
                              );
                            },
                          }}
                        >
                          {value || "No content"}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ))}

                {msg.data?.perspectives && (
                  <div className="space-y-3">
                    <h2 className="text-white text-sm font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                      Perspectives
                    </h2>
                    <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.data.perspectives}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {msg.data?.critical_analysis && (
                  <div className="space-y-3">
                    <h2 className="text-white text-sm font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                      Critical Analysis
                    </h2>
                    <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.data.critical_analysis}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {msg.data?.references?.length > 0 && (
                  <div className="space-y-3">
                    <h2 className="text-white text-sm font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                      References
                    </h2>
                    <div className="space-y-2">
                      {msg.data.references.map((ref) => (
                        <div
                          key={ref.id}
                          className="flex gap-3 text-xs text-gray-500"
                        >
                          <span className="font-mono shrink-0 text-gray-600">
                            [{ref.id}]
                          </span>
                          <div>
                            <a
                              href={ref.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-gray-400 hover:text-white hover:underline transition-colors"
                            >
                              {ref.title}
                            </a>
                            {ref.source && (
                              <span className="text-gray-700 ml-2">
                                {ref.source}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ),
          )}

          {loading && (
            <div className="text-sm text-gray-500 italic">{loadingText}</div>
          )}

          <div ref={endRef} />
        </div>
      </main>

      <footer className="border-t border-white/8 bg-[#0f0f0f] p-6">
        <div className="max-w-3xl mx-auto space-y-3">
          {!lastReport && (
            <div>
              <button
                onClick={() => setShowFormat(!showFormat)}
                className="text-xs text-gray-600 hover:text-gray-400 transition-colors mb-2"
              >
                {showFormat ? "Hide" : "Custom format (optional)"}
              </button>
              {showFormat && (
                <textarea
                  value={customFormat}
                  onChange={(e) => setCustomFormat(e.target.value)}
                  placeholder="Paste your college or custom research format here..."
                  className="w-full bg-transparent border border-white/10 px-4 py-3 rounded-lg text-white placeholder-gray-700 outline-none text-xs resize-none focus:border-white/20 transition-colors"
                  rows={3}
                />
              )}
            </div>
          )}

          <div className="flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
              placeholder={
                lastReport
                  ? "Ask a follow-up question..."
                  : "Enter a research topic..."
              }
              className="flex-1 bg-transparent border border-white/10 focus:border-white/25 px-4 py-3 rounded-lg outline-none text-white placeholder-gray-600 text-sm transition-colors"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading}
              className={`px-6 py-3 rounded-lg text-sm font-medium transition-all ${
                loading
                  ? "text-gray-600 border border-white/8 cursor-not-allowed"
                  : "text-white bg-white/10 hover:bg-white/15 border border-white/15"
              }`}
            >
              {loading ? "Working..." : "Send"}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
