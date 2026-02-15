import { useState, useRef } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000/api/v1/transcription";

export default function App() {
  const [view, setView] = useState("home");
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const uploadInputRef = useRef(null);

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

  function stopRecording() {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
      setRecording(false);
    }
  }

  function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setResult(null);
    sendAudio(file, file.name);
    e.target.value = "";
  }

  function startOver() {
    setResult(null);
    setError(null);
  }

  if (view === "analytics") {
    return (
      <div className="page">
        <h1 className="title">Analytics</h1>
        <div className="newRecording">
          <button type="button" onClick={() => setView("home")}>Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1 className="title">SpeakClear</h1>
      <p className="tagline">tool to improve speaking</p>
      <p className="subtitle">Record or upload audio to get a transcription.</p>

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

      {recording && (
        <div className="recording">
          <p className="recordingStatus">Recording… “Stop recording” when finished.</p>
          <button type="button" className="stopBtn" onClick={stopRecording}>
            Stop recording
          </button>
        </div>
      )}

      {processing && (
        <div className="processing">
          <p>Processing…</p>
        </div>
      )}

      {error && (
        <div className="error">
          <p>{error}</p>
          <div className="newRecording">
            <button type="button" onClick={startOver}>Try again</button>
          </div>
        </div>
      )}

      {result && (
        <div className="result">
          <h2 className="resultTitle">Transcription</h2>
          <p className="resultText">{result.text || "(no speech detected)"}</p>
          <div className="newRecording">
            <button type="button" onClick={startOver}>New recording or upload</button>
            <button type="button" onClick={() => setView("analytics")}>Go to analytics</button>
          </div>
        </div>
      )}
    </div>
  );
}
