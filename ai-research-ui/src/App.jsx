import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const MODES = [
  {
    id: "research",
    label: "Research Paper",
    placeholder: "Enter a research topic...",
  },
  {
    id: "script",
    label: "YouTube Script",
    placeholder: "Enter your video topic...",
  },
  {
    id: "literature",
    label: "Literature Review",
    placeholder: "Enter your research topic...",
  },
  {
    id: "explainer",
    label: "Explain Paper",
    placeholder: "Optional: describe what you want to understand...",
  },
];

const SCRIPT_STYLES = [
  "educational",
  "entertainment",
  "documentary",
  "tutorial",
];

const LOADING_MESSAGES = {
  research: [
    "Searching sources...",
    "Reading articles...",
    "Analysing research...",
    "Writing report...",
    "Almost done...",
  ],
  script: [
    "Finding research...",
    "Crafting your hook...",
    "Writing main points...",
    "Adding examples...",
    "Finalising script...",
  ],
  literature: [
    "Reading your papers...",
    "Summarising each paper...",
    "Finding themes...",
    "Identifying gaps...",
    "Writing review...",
  ],
  explainer: [
    "Reading your paper...",
    "Understanding the research...",
    "Writing simple explanation...",
    "Analysing limitations...",
    "Almost done...",
  ],
};

function loadSessions() {
  try {
    return JSON.parse(localStorage.getItem("synthex_sessions") || "[]");
  } catch {
    return [];
  }
}

function saveSessions(sessions) {
  try {
    localStorage.setItem("synthex_sessions", JSON.stringify(sessions));
  } catch {
    console.error("Could not save to localStorage");
  }
}

function formatTime(ts) {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return "Yesterday";
  return `${days}d ago`;
}

function getPreview(chat) {
  const userMsg = chat.find((m) => m.role === "user");
  return userMsg?.text?.slice(0, 40) || "New chat";
}

function App() {
  const [mode, setMode] = useState("research");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastReport, setLastReport] = useState(null);
  const [customFormat, setCustomFormat] = useState("");
  const [showFormat, setShowFormat] = useState(false);
  const [scriptStyle, setScriptStyle] = useState("educational");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [explainerFile, setExplainerFile] = useState(null);
  const [loadingText, setLoadingText] = useState("Working...");
  const [sessions, setSessions] = useState(loadSessions);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const endRef = useRef(null);
  const fileInputRef = useRef(null);
  const explainerFileRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  useEffect(() => {
    if (!loading) return;
    const messages = LOADING_MESSAGES[mode] || ["Working..."];
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % messages.length;
      setLoadingText(messages[i]);
    }, 3000);
    return () => clearInterval(interval);
  }, [loading, mode]);

  useEffect(() => {
    if (chat.length === 0) return;
    setSessions((prev) => {
      const existing = prev.find((s) => s.id === activeSessionId);
      if (existing) {
        const updated = prev.map((s) =>
          s.id === activeSessionId
            ? { ...s, chat, lastReport, mode, updatedAt: Date.now() }
            : s,
        );
        saveSessions(updated);
        return updated;
      }
      return prev;
    });
  }, [chat, lastReport]);

  const startNewChat = () => {
    if (chat.length > 0 && activeSessionId) {
      setSessions((prev) => {
        const updated = prev.map((s) =>
          s.id === activeSessionId
            ? { ...s, chat, lastReport, mode, updatedAt: Date.now() }
            : s,
        );
        saveSessions(updated);
        return updated;
      });
    }
    const newId = Date.now().toString();
    const newSession = {
      id: newId,
      mode,
      chat: [],
      lastReport: null,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setSessions((prev) => {
      const updated = [newSession, ...prev];
      saveSessions(updated);
      return updated;
    });
    setActiveSessionId(newId);
    setChat([]);
    setLastReport(null);
    setInput("");
    setUploadedFiles([]);
    setExplainerFile(null);
    setCustomFormat("");
    setShowFormat(false);
  };

  const loadSession = (session) => {
    setActiveSessionId(session.id);
    setChat(session.chat || []);
    setLastReport(session.lastReport || null);
    setMode(session.mode || "research");
    setInput("");
    setUploadedFiles([]);
    setExplainerFile(null);
  };

  const deleteSession = (e, sessionId) => {
    e.stopPropagation();
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== sessionId);
      saveSessions(updated);
      return updated;
    });
    if (activeSessionId === sessionId) {
      setChat([]);
      setLastReport(null);
      setActiveSessionId(null);
    }
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setChat([]);
    setLastReport(null);
    setInput("");
    setUploadedFiles([]);
    setExplainerFile(null);
    setCustomFormat("");
    setShowFormat(false);
    setActiveSessionId(null);
  };

  const handleSend = async () => {
    if (mode === "literature" && uploadedFiles.length === 0) {
      alert("Please upload at least one PDF file");
      return;
    }
    if (mode === "explainer" && !explainerFile) {
      alert("Please upload a PDF to explain");
      return;
    }
    if (!input.trim() && mode !== "explainer") return;

    const userInput = input || explainerFile?.name || "Explain this paper";
    setInput("");
    setChat((prev) => [...prev, { role: "user", text: userInput }]);
    setLoading(true);
    setLoadingText(LOADING_MESSAGES[mode][0]);

    if (!activeSessionId) {
      const newId = Date.now().toString();
      const newSession = {
        id: newId,
        mode,
        chat: [],
        lastReport: null,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      setSessions((prev) => {
        const updated = [newSession, ...prev];
        saveSessions(updated);
        return updated;
      });
      setActiveSessionId(newId);
    }

    try {
      let res, data;

      if (lastReport && mode === "research") {
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
        return;
      }

      if (mode === "research") {
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
          setChat((prev) => [...prev, { role: "ai", data }]);
          return;
        }
        if (!data.sections || Object.keys(data.sections).length === 0) {
          setChat((prev) => [
            ...prev,
            { role: "ai", text: "No content generated. Try another topic." },
          ]);
          return;
        }
        setLastReport(data);
        setChat((prev) => [...prev, { role: "ai", data }]);
      } else if (mode === "script") {
        res = await fetch(`${API}/generate-script`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: userInput, style: scriptStyle }),
        });
        data = await res.json();
        setLastReport(data);
        setChat((prev) => [...prev, { role: "ai", data }]);
      } else if (mode === "literature") {
        const formData = new FormData();
        formData.append("topic", userInput);
        uploadedFiles.forEach((file) => formData.append("files", file));
        res = await fetch(`${API}/generate-literature-review`, {
          method: "POST",
          body: formData,
        });
        data = await res.json();
        setLastReport(data);
        setChat((prev) => [...prev, { role: "ai", data }]);
      } else if (mode === "explainer") {
        const formData = new FormData();
        formData.append("topic", userInput);
        formData.append("file", explainerFile);
        res = await fetch(`${API}/explain-paper`, {
          method: "POST",
          body: formData,
        });
        data = await res.json();
        setLastReport(data);
        setChat((prev) => [...prev, { role: "ai", data }]);
      }
    } catch (err) {
      console.error(err);
      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text: "Backend connection failed. Is the server running?",
        },
      ]);
    } finally {
      setLoading(false);
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
        if (ref && ref.url)
          return (
            <a
              key={i}
              href={ref.url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-400 hover:underline font-mono text-xs mx-0.5"
            >
              [{refId}]
            </a>
          );
        return (
          <span key={i} className="font-mono text-xs text-gray-500">
            [{refId}]
          </span>
        );
      }
      return part;
    });
  };

  const handleDownload = async (type) => {
    if (!lastReport) return;
    try {
      const res = await fetch(`${API}/download-${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: lastReport.topic || "Report",
          sections: lastReport.sections || {},
          references: lastReport.references || [],
          domain: lastReport.domain || "",
        }),
      });
      if (!res.ok) {
        alert("Download failed");
        return;
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report.${type === "pdf" ? "pdf" : "docx"}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert("Failed to download");
    }
  };

  const currentMode = MODES.find((m) => m.id === mode);

  const renderSections = (sections, references) =>
    Object.entries(sections || {}).map(([key, value]) => (
      <div key={key} className="space-y-3">
        <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
          {key}
        </h2>
        <div className="text-sm text-gray-300 leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p({ children }) {
                return (
                  <p className="mb-3 last:mb-0">
                    {renderWithCitations(children, references)}
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
                  <td className="border border-white/10 px-4 py-2 text-gray-300">
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
    ));

  const renderReferences = (references) =>
    references?.length > 0 && (
      <div className="space-y-3">
        <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
          References
        </h2>
        <div className="space-y-2">
          {references.map((ref) => (
            <div key={ref.id} className="flex gap-3 text-xs text-gray-500">
              <span className="font-mono shrink-0 text-gray-600">
                [{ref.id}]
              </span>
              <a
                href={ref.url}
                target="_blank"
                rel="noreferrer"
                className="text-gray-400 hover:text-white hover:underline transition-colors"
              >
                {ref.title}
              </a>
            </div>
          ))}
        </div>
      </div>
    );

  const ExplainerBlock = ({ label, content, accent = false }) => (
    <div className="space-y-3">
      <h2
        className={`text-xs font-semibold uppercase tracking-widest border-b pb-2 ${accent ? "text-blue-400 border-blue-400/20" : "text-white border-white/8"}`}
      >
        {label}
      </h2>
      <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </div>
  );

  const today = sessions.filter((s) => Date.now() - s.updatedAt < 86400000);
  const yesterday = sessions.filter(
    (s) =>
      Date.now() - s.updatedAt >= 86400000 &&
      Date.now() - s.updatedAt < 172800000,
  );
  const older = sessions.filter((s) => Date.now() - s.updatedAt >= 172800000);

  const SessionItem = ({ session }) => (
    <div
      onClick={() => loadSession(session)}
      className={`group flex items-start justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-all ${activeSessionId === session.id ? "bg-white/8 text-white" : "hover:bg-white/4 text-gray-500 hover:text-gray-300"}`}
    >
      <div className="flex-1 min-w-0">
        <p className="text-xs truncate">{getPreview(session.chat)}</p>
        <p className="text-xs text-gray-700 mt-0.5">
          {MODES.find((m) => m.id === session.mode)?.label} ·{" "}
          {formatTime(session.updatedAt)}
        </p>
      </div>
      <button
        onClick={(e) => deleteSession(e, session.id)}
        className="opacity-0 group-hover:opacity-100 text-gray-700 hover:text-red-400 transition-all ml-2 text-xs shrink-0"
      >
        ×
      </button>
    </div>
  );

  const SessionGroup = ({ label, items }) =>
    items.length > 0 && (
      <div className="space-y-0.5">
        <p className="text-xs text-gray-700 uppercase tracking-widest px-3 py-2">
          {label}
        </p>
        {items.map((s) => (
          <SessionItem key={s.id} session={s} />
        ))}
      </div>
    );

  return (
    <div
      className="bg-[#0f0f0f] text-gray-300 min-h-screen flex"
      style={{ fontFamily: "'Georgia', serif" }}
    >
      {/* SIDEBAR */}
      <aside
        className={`${sidebarOpen ? "w-64" : "w-0"} shrink-0 transition-all duration-300 overflow-hidden border-r border-white/8 flex flex-col`}
      >
        <div className="p-4 border-b border-white/8 flex items-center justify-between">
          <span className="text-white font-semibold text-sm tracking-widest uppercase">
            Synthex
          </span>
          <button
            onClick={startNewChat}
            className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/25 px-2 py-1 rounded transition-all"
          >
            + New
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-4">
          {sessions.length === 0 ? (
            <p className="text-xs text-gray-700 px-3 py-4 text-center">
              No chats yet. Start a new one.
            </p>
          ) : (
            <>
              <SessionGroup label="Today" items={today} />
              <SessionGroup label="Yesterday" items={yesterday} />
              <SessionGroup label="Older" items={older} />
            </>
          )}
        </div>
      </aside>

      {/* MAIN */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* HEADER */}
        <header className="border-b border-white/8 bg-[#0f0f0f] sticky top-0 z-10">
          <div className="px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-600 hover:text-white transition-colors text-sm"
              >
                ☰
              </button>
              <div className="flex gap-1">
                {MODES.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => handleModeChange(m.id)}
                    className={`text-xs px-3 py-1.5 rounded transition-all ${mode === m.id ? "bg-white text-black font-medium" : "text-gray-500 hover:text-white"}`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3">
              {lastReport && mode === "research" && (
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
              <button
                onClick={startNewChat}
                className="text-xs text-gray-500 hover:text-white border border-white/10 hover:border-white/20 px-3 py-1.5 rounded transition-all"
              >
                New Chat
              </button>
            </div>
          </div>
        </header>

        {/* CHAT */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-8 py-10 space-y-10">
            {chat.length === 0 && (
              <div className="mt-16 space-y-3">
                <h1 className="text-2xl text-white font-semibold">
                  {mode === "research" && "What would you like to research?"}
                  {mode === "script" && "What is your next video about?"}
                  {mode === "literature" &&
                    "Upload your papers for a literature review"}
                  {mode === "explainer" &&
                    "Upload a research paper to understand it"}
                </h1>
                <p className="text-gray-600 text-sm">
                  {mode === "research" &&
                    "Full academic research papers with citations, critical analysis and perspectives."}
                  {mode === "script" &&
                    "Fully researched YouTube script with hook, main points, examples and CTA."}
                  {mode === "literature" &&
                    "Upload research PDFs and get themes, gaps, research questions and hypotheses."}
                  {mode === "explainer" &&
                    "Upload any research paper and get simple explanations for beginners, students and professionals — plus what it actually proves."}
                </p>
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
                <div key={i} className="space-y-8">
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
                        }}
                      >
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* RESEARCH */}
                  {msg.data?.type === "research" && (
                    <div className="space-y-8">
                      <div className="flex gap-4 text-xs text-gray-600 border-b border-white/5 pb-4">
                        <span>
                          {Object.keys(msg.data.sections || {}).length} sections
                        </span>
                        {msg.data.domain && <span>{msg.data.domain}</span>}
                        {msg.data.source && <span>via {msg.data.source}</span>}
                        <button
                          onClick={() =>
                            navigator.clipboard.writeText(
                              JSON.stringify(msg.data),
                            )
                          }
                          className="ml-auto hover:text-gray-400 transition-colors"
                        >
                          Copy
                        </button>
                      </div>
                      {renderSections(msg.data.sections, msg.data.references)}
                      {msg.data?.perspectives && (
                        <div className="space-y-3">
                          <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
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
                          <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                            Critical Analysis
                          </h2>
                          <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.data.critical_analysis}
                            </ReactMarkdown>
                          </div>
                        </div>
                      )}
                      {renderReferences(msg.data.references)}
                    </div>
                  )}

                  {/* COMPARISON */}
                  {msg.data?.type === "comparison" && (
                    <div className="space-y-4">
                      <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                        Comparison — {msg.data.topic}
                      </h2>
                      <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.data.result}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}

                  {/* SCRIPT */}
                  {msg.data?.type === "script" && (
                    <div className="space-y-8">
                      <div className="flex gap-4 text-xs text-gray-600 border-b border-white/5 pb-4">
                        <span className="uppercase tracking-widest">
                          YouTube Script
                        </span>
                        <span>{msg.data.style}</span>
                        <button
                          onClick={() =>
                            navigator.clipboard.writeText(msg.data.script)
                          }
                          className="ml-auto hover:text-gray-400 transition-colors"
                        >
                          Copy Script
                        </button>
                      </div>
                      {msg.data.meta && (
                        <div className="space-y-3">
                          <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                            Title Ideas and Metadata
                          </h2>
                          <div className="text-sm text-gray-400 leading-relaxed whitespace-pre-wrap">
                            {msg.data.meta}
                          </div>
                        </div>
                      )}
                      {msg.data.script && (
                        <div className="space-y-3">
                          <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                            Full Script
                          </h2>
                          <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                p({ children }) {
                                  return (
                                    <p className="mb-4 last:mb-0">
                                      {renderWithCitations(
                                        children,
                                        msg.data?.references,
                                      )}
                                    </p>
                                  );
                                },
                              }}
                            >
                              {msg.data.script}
                            </ReactMarkdown>
                          </div>
                        </div>
                      )}
                      {renderReferences(msg.data.references)}
                    </div>
                  )}

                  {/* LITERATURE REVIEW */}
                  {msg.data?.type === "literature_review" && (
                    <div className="space-y-8">
                      <div className="flex gap-4 text-xs text-gray-600 border-b border-white/5 pb-4">
                        <span className="uppercase tracking-widest">
                          Literature Review
                        </span>
                        <span>{msg.data.paper_count} papers analysed</span>
                      </div>
                      {msg.data.summaries?.length > 0 && (
                        <div className="space-y-3">
                          <h2 className="text-white text-xs font-semibold uppercase tracking-widest border-b border-white/8 pb-2">
                            Paper Summaries
                          </h2>
                          <div className="space-y-4">
                            {msg.data.summaries.map((s) => (
                              <div
                                key={s.id}
                                className="border-l-2 border-white/10 pl-4"
                              >
                                <p className="text-xs text-gray-500 mb-1 font-mono">
                                  [{s.id}] {s.filename}
                                </p>
                                <p className="text-sm text-gray-300 leading-relaxed">
                                  {s.summary}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {msg.data.review && (
                        <ExplainerBlock
                          label="Literature Review"
                          content={msg.data.review}
                        />
                      )}
                      {msg.data.research_questions && (
                        <ExplainerBlock
                          label="Research Gaps and Questions"
                          content={msg.data.research_questions}
                        />
                      )}
                    </div>
                  )}

                  {/* PAPER EXPLAINER */}
                  {msg.data?.type === "paper_explainer" && (
                    <div className="space-y-8">
                      <div className="flex gap-4 text-xs text-gray-600 border-b border-white/5 pb-4">
                        <span className="uppercase tracking-widest">
                          Paper Explained
                        </span>
                        <button
                          onClick={() =>
                            navigator.clipboard.writeText(
                              `ELI5:\n${msg.data.eli5}\n\nStudent:\n${msg.data.student}\n\nProfessional:\n${msg.data.professional}`,
                            )
                          }
                          className="ml-auto hover:text-gray-400 transition-colors"
                        >
                          Copy All
                        </button>
                      </div>

                      {/* paper meta */}
                      {msg.data.meta && (
                        <div className="bg-white/3 border border-white/8 rounded-lg p-4">
                          <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">
                            Paper Details
                          </p>
                          <div className="text-sm text-gray-300 whitespace-pre-wrap">
                            {msg.data.meta}
                          </div>
                        </div>
                      )}

                      {/* key facts */}
                      {msg.data.key_facts && (
                        <ExplainerBlock
                          label="Key Facts and Numbers"
                          content={msg.data.key_facts}
                          accent={true}
                        />
                      )}

                      {/* 3 explanation levels */}
                      {msg.data.eli5 && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <h2 className="text-white text-xs font-semibold uppercase tracking-widest">
                              Explain Like I am 5
                            </h2>
                            <span className="text-xs text-gray-600 border border-white/8 px-2 py-0.5 rounded">
                              Beginner
                            </span>
                          </div>
                          <div className="border-l-2 border-white/15 pl-4 text-sm text-gray-300 leading-relaxed">
                            {msg.data.eli5}
                          </div>
                        </div>
                      )}

                      {msg.data.student && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <h2 className="text-white text-xs font-semibold uppercase tracking-widest">
                              Student Explanation
                            </h2>
                            <span className="text-xs text-gray-600 border border-white/8 px-2 py-0.5 rounded">
                              Undergraduate
                            </span>
                          </div>
                          <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.data.student}
                            </ReactMarkdown>
                          </div>
                        </div>
                      )}

                      {msg.data.professional && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <h2 className="text-white text-xs font-semibold uppercase tracking-widest">
                              Professional Summary
                            </h2>
                            <span className="text-xs text-gray-600 border border-white/8 px-2 py-0.5 rounded">
                              Executive
                            </span>
                          </div>
                          <div className="text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.data.professional}
                            </ReactMarkdown>
                          </div>
                        </div>
                      )}

                      {/* critical analysis */}
                      {msg.data.analysis && (
                        <ExplainerBlock
                          label="Critical Analysis"
                          content={msg.data.analysis}
                        />
                      )}
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

        {/* INPUT */}
        <footer className="border-t border-white/8 bg-[#0f0f0f] p-6">
          <div className="max-w-3xl mx-auto space-y-3">
            {mode === "research" && !lastReport && (
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

            {mode === "script" && (
              <div className="flex gap-2">
                {SCRIPT_STYLES.map((s) => (
                  <button
                    key={s}
                    onClick={() => setScriptStyle(s)}
                    className={`text-xs px-3 py-1 rounded border transition-all capitalize ${scriptStyle === s ? "bg-white text-black border-white" : "border-white/10 text-gray-500 hover:text-white"}`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {mode === "literature" && (
              <div>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".pdf"
                  multiple
                  className="hidden"
                  onChange={(e) => setUploadedFiles(Array.from(e.target.files))}
                />
                <button
                  onClick={() => fileInputRef.current.click()}
                  className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/25 px-4 py-2 rounded-lg transition-all"
                >
                  Upload PDFs ({uploadedFiles.length} selected)
                </button>
                {uploadedFiles.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {uploadedFiles.map((f, i) => (
                      <span
                        key={i}
                        className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded"
                      >
                        {f.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {mode === "explainer" && (
              <div>
                <input
                  type="file"
                  ref={explainerFileRef}
                  accept=".pdf"
                  className="hidden"
                  onChange={(e) => setExplainerFile(e.target.files[0] || null)}
                />
                <button
                  onClick={() => explainerFileRef.current.click()}
                  className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/25 px-4 py-2 rounded-lg transition-all"
                >
                  {explainerFile
                    ? `Selected: ${explainerFile.name}`
                    : "Upload PDF to explain"}
                </button>
              </div>
            )}

            <div className="flex gap-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
                placeholder={
                  lastReport && mode === "research"
                    ? "Ask a follow-up question..."
                    : mode === "explainer"
                      ? "Optional: what do you want to understand about this paper?"
                      : currentMode.placeholder
                }
                className="flex-1 bg-transparent border border-white/10 focus:border-white/25 px-4 py-3 rounded-lg outline-none text-white placeholder-gray-600 text-sm transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={loading}
                className={`px-6 py-3 rounded-lg text-sm font-medium transition-all ${loading ? "text-gray-600 border border-white/8 cursor-not-allowed" : "text-white bg-white/10 hover:bg-white/15 border border-white/15"}`}
              >
                {loading ? "Working..." : "Send"}
              </button>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
