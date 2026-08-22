import React, {
  useEffect,
  useRef,
  useState,
} from "react";
import ReactMarkdown from "react-markdown";

import {
  ChevronDown,
  FileText,
  Moon,
  Send,
  ShieldCheck,
  Sun,
  Upload,
  X,
  Zap,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] =
    useState(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [metrics, setMetrics] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  const [darkMode, setDarkMode] = useState(false);

  const fileInputRef = useRef(null);

  /*
  ============================================================
  THEME
  ============================================================
  */

  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      darkMode
    );
  }, [darkMode]);

  /*
  ============================================================
  BROWSER TAB / FAVICON
  ============================================================
  */

  useEffect(() => {
    document.title = "GyaanAI";

    document
      .querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]')
      .forEach((link) => link.remove());

    const favicon = document.createElement("link");
    favicon.rel = "icon";
    favicon.type = "image/x-icon";
    favicon.href = "/favicon.ico";
    document.head.appendChild(favicon);

    const shortcutIcon = document.createElement("link");
    shortcutIcon.rel = "shortcut icon";
    shortcutIcon.type = "image/x-icon";
    shortcutIcon.href = "/favicon.ico";
    document.head.appendChild(shortcutIcon);
  }, []);

  /*
  ============================================================
  LOAD DOCUMENTS FROM BACKEND
  ============================================================
  */

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      const response = await fetch(
        `${API_URL}/documents`
      );

      if (!response.ok) {
        throw new Error(
          `Failed to load documents: ${response.status}`
        );
      }

      const data = await response.json();

      const activeDocuments = Array.isArray(data)
        ? data
        : data.documents || [];

      setDocuments(activeDocuments);

      /*
       * If the selected document no longer exists,
       * clear it.
       */
      setSelectedDocument((current) => {
        if (!current) {
          return null;
        }

        const stillExists = activeDocuments.some(
          (document) =>
            document.document_id ===
            current.document_id
        );

        return stillExists ? current : null;
      });
    } catch (err) {
      console.error(
        "Failed to load documents:",
        err
      );

      setError(
        "Could not load active documents."
      );
    }
  }

  /*
  ============================================================
  REMOVE EXPIRED DOCUMENTS FROM UI
  ============================================================
  */

  useEffect(() => {
    const timer = setInterval(() => {
      setDocuments((current) =>
        current.filter((document) => {
          if (!document.expires_at) {
            return true;
          }

          return (
            new Date(
              document.expires_at
            ).getTime() > Date.now()
          );
        })
      );

      setSelectedDocument((current) => {
        if (!current) {
          return null;
        }

        if (!current.expires_at) {
          return current;
        }

        if (
          new Date(
            current.expires_at
          ).getTime() <= Date.now()
        ) {
          setQuestion("");
          setAnswer("");
          setSources([]);
          setMetrics(null);

          return null;
        }

        return current;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  /*
  ============================================================
  UPLOAD DOCUMENT
  ============================================================
  */

  async function handleUpload(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      setError(
        "Only PDF files are supported."
      );

      return;
    }

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();

      formData.append(
        "file",
        file
      );

      const response = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const data =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          data?.detail ||
            `Upload failed with status ${response.status}`
        );
      }

      const data =
        await response.json();

      const uploadedDocument = {
        document_id:
          data.document_id,

        filename:
          data.filename ||
          file.name,

        expires_at:
          data.expires_at,
      };

      /*
       * Reload documents from backend.
       * This makes backend metadata the source
       * of truth.
       */
      await loadDocuments();

      setSelectedDocument(
        uploadedDocument
      );

      setQuestion("");
      setAnswer("");
      setSources([]);
      setMetrics(null);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong while uploading."
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  /*
  ============================================================
  SELECT DOCUMENT
  ============================================================
  */

  function selectDocument(document) {
    setSelectedDocument(document);

    setQuestion("");
    setAnswer("");
    setSources([]);
    setMetrics(null);
    setError("");
  }

  /*
  ============================================================
  NEW DOCUMENT / DESELECT
  ============================================================
  */

  function handleNewDocument() {
    setSelectedDocument(null);

    setQuestion("");
    setAnswer("");
    setSources([]);
    setMetrics(null);
    setError("");
  }

  /*
  ============================================================
  ASK QUESTION
  ============================================================
  */

  async function handleAsk() {
    const trimmed =
      question.trim();

    if (!trimmed) {
      return;
    }

    if (!selectedDocument) {
      setError(
        "Upload and select a document first."
      );

      return;
    }

    setAsking(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/documents/${selectedDocument.document_id}/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            question: trimmed,
          }),
        }
      );

      if (!response.ok) {
        const data =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          data?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data =
        await response.json();

      setAnswer(
        data.answer || ""
      );

      setSources(
        data.sources || []
      );

      setMetrics(
        data.metrics || null
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Failed to generate an answer."
      );
    } finally {
      setAsking(false);
    }
  }

  /*
  ============================================================
  ENTER TO ASK
  ============================================================
  */

  function handleQuestionKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (!asking) {
        handleAsk();
      }
    }
  }

  /*
  ============================================================
  FORMAT EXPIRY
  ============================================================
  */

  function formatExpiry(expiresAt) {
    if (!expiresAt) {
      return "";
    }

    return new Date(
      expiresAt
    ).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  /*
  ============================================================
  FORMAT METRIC
  ============================================================
  */

  function formatMetric(value) {
    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    return `${Math.round(
      value * 100
    )}%`;
  }

  /*
  ============================================================
  RENDER
  ============================================================
  */

  return (
    <div className="app">

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside className="sidebar">

        <div className="sidebar-content">

          {/* BRAND */}

          <div className="brand">

            <div
              className="brand-mark"
              style={{
                width: "58px",
                height: "58px",
                borderRadius: "50%",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                background: "transparent",
              }}
            >
              <img
                src="/favicon.ico"
                alt="GyaanAI logo"
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                  display: "block",
                }}
              />
            </div>

            <div className="brand-copy">

              <div className="brand-name">
                GyaanAI
              </div>

              <div className="brand-subtitle">
                Ask. Understand. Discover.
              </div>

            </div>

          </div>


          {/* UPLOAD */}

          <button
            className="upload-button"
            onClick={() =>
              fileInputRef.current?.click()
            }
            disabled={uploading}
          >
            <Upload size={18} />

            <span>
              {uploading
                ? "Uploading..."
                : "Upload PDF"}
            </span>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleUpload}
            hidden
          />


          {/* DOCUMENTS */}

          <div className="sidebar-heading">
            CURRENT DOCUMENTS
          </div>

          <div className="document-list">

            {documents.length === 0 ? (

              <div className="empty-documents">

                <FileText size={28} />

                <strong>
                  No active documents.
                </strong>

                <span>
                  Upload a PDF to begin.
                </span>

              </div>

            ) : (

              documents.map((document) => (

                <button
                  key={
                    document.document_id
                  }
                  className={`document-item ${
                    selectedDocument?.document_id ===
                    document.document_id
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    selectDocument(
                      document
                    )
                  }
                >

                  <div className="document-icon">
                    <FileText size={20} />
                  </div>

                  <div className="document-details">

                    <strong>
                      {document.filename}
                    </strong>

                    <span>
                      Expires{" "}
                      {formatExpiry(
                        document.expires_at
                      )}
                    </span>

                  </div>

                  <ChevronDown
                    className="document-chevron"
                    size={17}
                  />

                </button>

              ))

            )}

          </div>

        </div>


        {/* SIDEBAR FOOTER */}

        <div className="sidebar-footer">

          <div className="security">

            <div className="security-icon">
              <ShieldCheck size={21} />
            </div>

            <div>

              <strong>
                Built with RAG + Gemini
              </strong>

              <span>
                Secure. Private. Intelligent.
              </span>

            </div>

          </div>

        </div>

      </aside>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="main">

        {/* HEADER */}

        <header className="header">

          <div>

            <div className="header-eyebrow">
              GYAANAI
            </div>

            <h1>
              Document Q&amp;A
            </h1>

          </div>


          {/* THEME */}

          <button
            className="theme-toggle"
            onClick={() =>
              setDarkMode(
                (current) => !current
              )
            }
          >

            {darkMode ? (
              <Sun size={17} />
            ) : (
              <Moon size={17} />
            )}

            <span>
              {darkMode
                ? "Light"
                : "Dark"}
            </span>

          </button>

        </header>


        {/* ERROR */}

        {error && (

          <div className="error-banner">

            <span>
              {error}
            </span>

            <button
              onClick={() =>
                setError("")
              }
            >
              <X size={16} />
            </button>

          </div>

        )}


        {/* =================================================
            NO DOCUMENT SELECTED
        ================================================= */}

        {!selectedDocument && (

          <section className="empty-state-section">

            <div className="empty-chat-state">

              <div className="empty-chat-icon">
                <Zap
                  size={28}
                  strokeWidth={2}
                />
              </div>

              <h2>
                Ask anything about your document.
              </h2>

              <p>
                GyaanAI will retrieve the relevant
                passages and generate a grounded answer.
              </p>

            </div>

          </section>

        )}


        {/* =================================================
            DOCUMENT SELECTED
        ================================================= */}

        {selectedDocument && (

          <>

            {/* SELECTED DOCUMENT */}

            <section className="selected-document-section">

              <div className="section-label">
                SELECTED DOCUMENT
              </div>

              <div className="selected-document-card">

                <div className="selected-file-icon">
                  <FileText size={27} />
                </div>

                <div className="selected-file-details">

                  <strong>
                    {selectedDocument.filename}
                  </strong>

                  <span>
                    {selectedDocument.document_id}
                  </span>

                </div>

                <div className="expiry-details">

                  <span>
                    EXPIRES AT
                  </span>

                  <strong>
                    {formatExpiry(
                      selectedDocument.expires_at
                    )}
                  </strong>

                </div>

              </div>

            </section>


            {/* QUESTION */}

            <section className="question-section">

              <h2>
                Ask a question about this document
              </h2>

              <div className="question-box">

                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value
                    )
                  }
                  onKeyDown={
                    handleQuestionKeyDown
                  }
                  placeholder="What would you like to know?"
                  disabled={asking}
                />

                <button
                  className="ask-button"
                  onClick={handleAsk}
                  disabled={
                    asking ||
                    !question.trim()
                  }
                >

                  <Send size={17} />

                  <span>
                    {asking
                      ? "Asking..."
                      : "Ask"}
                  </span>

                </button>

              </div>

              <div className="question-hint">
                Press Enter to ask · Shift + Enter for a new line
              </div>

            </section>


            {/* ANSWER */}

            {answer && (

              <section className="results">

                <div className="section-label">
                  ANSWER
                </div>

                <div className="answer-panel">

                  <div className="answer markdown-answer">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => (
                          <p style={{ margin: "0 0 1rem", lineHeight: 1.8 }}>
                            {children}
                          </p>
                        ),
                        ul: ({ children }) => (
                          <ul
                            style={{
                              margin: "0.75rem 0 1rem 1.5rem",
                              paddingLeft: "1rem",
                              lineHeight: 1.8,
                            }}
                          >
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol
                            style={{
                              margin: "0.75rem 0 1rem 1.5rem",
                              paddingLeft: "1rem",
                              lineHeight: 1.8,
                            }}
                          >
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => (
                          <li style={{ marginBottom: "0.5rem" }}>
                            {children}
                          </li>
                        ),
                        strong: ({ children }) => (
                          <strong style={{ fontWeight: 700 }}>
                            {children}
                          </strong>
                        ),
                        h1: ({ children }) => (
                          <h1 style={{ margin: "1.25rem 0 0.75rem" }}>
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 style={{ margin: "1.25rem 0 0.75rem" }}>
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 style={{ margin: "1.25rem 0 0.75rem" }}>
                            {children}
                          </h3>
                        ),
                      }}
                    >
                      {answer}
                    </ReactMarkdown>
                  </div>

                </div>


                {/* METRICS */}

                {metrics && (

                  <div className="metrics-panel">

                    <div className="section-label">
                      EVALUATION
                    </div>

                    <div className="metrics">

                      <div className="metric">

                        <div className="metric-value">
                          {formatMetric(
                            metrics.faithfulness
                          )}
                        </div>

                        <div className="metric-label">
                          Faithfulness
                        </div>

                      </div>


                      <div className="metric">

                        <div className="metric-value">
                          {formatMetric(
                            metrics.answer_relevancy
                          )}
                        </div>

                        <div className="metric-label">
                          Answer Relevancy
                        </div>

                      </div>


                      <div className="metric">

                        <div className="metric-value">
                          {formatMetric(
                            metrics.context_precision
                          )}
                        </div>

                        <div className="metric-label">
                          Context Precision
                        </div>

                      </div>

                    </div>

                  </div>

                )}


                {/* SOURCES */}

                {sources.length > 0 && (

                  <div className="sources-panel">

                    <div className="section-label">
                      SOURCES
                    </div>

                    {sources.map(
                      (source, index) => (

                        <div
                          className="source"
                          key={`${source.chunk_id}-${index}`}
                        >

                          <div className="source-number">
                            {String(
                              index + 1
                            ).padStart(2, "0")}
                          </div>

                          <div className="source-content">

                            <div className="source-meta">
                              Page {source.page}
                              {" · "}
                              Score{" "}
                              {Number(
                                source.score
                              ).toFixed(3)}
                            </div>

                            <div className="source-text">
                              {source.text}
                            </div>

                          </div>

                        </div>

                      )
                    )}

                  </div>

                )}

              </section>

            )}

          </>

        )}


        {/* FOOTER */}

        <footer className="footer">

          <span>
            GyaanAI · Grounded document intelligence
          </span>

          <span>
            Documents are temporary and expire automatically.
          </span>

          <span>
            © {new Date().getFullYear()} Tisya Ahuja · All rights reserved
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;