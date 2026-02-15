import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000/api/v1/transcription";

// Loading spinner
function LoadingCircle() {
  return (
    <div className="loadingCircleWrap" aria-hidden="true">
      <div className="loadingCircle" />
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const uploadInputRef = useRef(null);

  // POST audio to backend, set result or error
  async function sendAudio(blob, filename = "recording.webm") {
    setError(null);
    setResult(null);
    setProcessing(true);
    try {
      const form = new FormData();
      form.append("file", blob, filename);
      const res = await fetch(`${API_BASE}/transcribe`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText || "Request failed");
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message || "Something went wrong");
    } finally {
      setProcessing(false);
    }
  }

  // Request mic, start MediaRecorder, on stop send blob
  async function startRecording() {
    setError(null);
    setResult(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        if (chunks.length) {
          const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
          sendAudio(blob, "recording.webm");
        }
      };
      recorder.start(200);
      mediaRecorderRef.current = recorder;
      setRecording(true);
    } catch (e) {
      setError(e.message || "Could not access microphone");
    }
  }

  // Stop recorder and release mic
  function stopRecording() {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
      setRecording(false);
    }
  }

  // User picked a file, send it
  function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setResult(null);
    sendAudio(file, file.name);
    e.target.value = "";
  }

  // Clear result and error
  function startOver() {
    setResult(null);
    setError(null);
  }

  // Analytics loading: show spinner then content after delay
  useEffect(() => {
    if (view === "analytics" && analyticsLoading) {
      const t = setTimeout(() => setAnalyticsLoading(false), 600);
      return () => clearTimeout(t);
    }
  }, [view, analyticsLoading]);

  // Analytics view
if (view === "analytics") {

  const fillerRanking =
    Object.entries(result?.fillers || {})
      .sort((a,b)=>b[1]-a[1]);

  const overallWPM =
    result?.sections?.length
      ? Math.round(
          result.sections.reduce((s,x)=>s+(x.wpm||0),0)
          / result.sections.length
        )
      : null;

  return (
    <div className="page">

      <h1 className="title">Analytics</h1>

      {analyticsLoading ? (

        <div className="processing">
          <LoadingCircle />
          <p>Loading analytics…</p>
        </div>

      ) : (

        <div className="dashboard">

          {/* LEFT */}
          <div className="panel">
            <h2>Transcription</h2>
            <p>{result?.text || "(no speech detected)"}</p>
          </div>

          {/* MIDDLE */}
          <div className="panel">
            <h2>Top filler words</h2>

            {fillerRanking.length ? (
              <ol>
                {fillerRanking.map(([w,c])=>(
                  <li key={w}>{w} — {c}</li>
                ))}
              </ol>
            ) : <p>No filler words 🎉</p>}
          </div>

          {/* RIGHT */}
          <div className="panel">
            <h2>Speaking Speed</h2>
            <div className="wpmNumber">
              {overallWPM ?? "--"}
            </div>
            <p>words per minute</p>
            <p className="wpmHint">Ideal: 120–160</p>
          </div>

        </div>
      )}

      <div className="newRecording">
        <button onClick={()=>setView("home")}>Home</button>
      </div>

    </div>
  );
}
  // Home view
  return (
    <div className="page">
      <h1 className="title">SpeakClear</h1>
      <p className="tagline">tool to improve speaking</p>
      <p className="subtitle">Record or upload audio to get a transcription.</p>

      {/* Record or upload options */}
      {!result && !processing && (
        <div className="options">
          <button
            type="button"
            className="option"
            onClick={recording ? stopRecording : startRecording}
            disabled={processing}
          >
            <span className="optionLabel">
              {recording ? "Stop recording" : "Record from microphone"}
            </span>
            <span className="optionHint">
              {recording
                ? "Click again when you’re done speaking."
                : "Use your browser microphone"}
            </span>
          </button>

          <label className="option">
            <input
              ref={uploadInputRef}
              type="file"
              className="uploadInput"
              accept="audio/*,.wav,.mp3,.webm,.m4a,.ogg"
              onChange={handleUpload}
              disabled={processing || recording}
            />
            <span className="optionLabel">Upload audio file</span>
            <span className="optionHint">WAV, MP3, WebM, just try one and hopefully it's supported.</span>
          </label>
        </div>
      )}

      {/* Recording in progress */}
      {recording && (
        <div className="recording">
          <p className="recordingStatus">Recording… “Stop recording” when finished.</p>
          <button type="button" className="stopBtn" onClick={stopRecording}>
            Stop recording
          </button>
        </div>
      )}

      {/* Transcription loading */}
      {processing && (
        <div className="processing">
          <LoadingCircle />
          <p>Processing…</p>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="error">
          <p>{error}</p>
          <div className="newRecording">
            <button type="button" onClick={startOver}>Try again</button>
          </div>
        </div>
      )}

      {/* Transcription result */}
      {result && (
        <div className="result">
          <h2 className="resultTitle">Transcription</h2>
          <p className="resultText">{result.text || "(no speech detected)"}</p>
          <div className="newRecording">
            <button type="button" onClick={startOver}>New recording or upload</button>
            <button type="button" onClick={() => { setView("analytics"); setAnalyticsLoading(true); }}>Go to analytics</button>
          </div>
        </div>
      )}
    </div>
  );
}
