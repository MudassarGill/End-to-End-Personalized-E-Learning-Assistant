import React, { useState, useRef, useCallback } from "react";
import { uploadFile, uploadText } from "../api";

const SUPPORTED = [
    { ext: ".pdf", icon: "📄", label: "PDF" },
    { ext: ".docx", icon: "📝", label: "Word" },
    { ext: ".txt", icon: "📃", label: "Text" },
    { ext: ".pptx", icon: "📊", label: "PowerPoint" },
    { ext: ".xlsx", icon: "📗", label: "Excel" },
    { ext: ".csv", icon: "📋", label: "CSV" },
    { ext: ".md", icon: "📑", label: "Markdown" },
    { ext: ".png", icon: "🖼️", label: "Image" },
    { ext: ".jpg", icon: "🖼️", label: "Image" },
];

export default function UploadForm({ userId, onSuccess, onError, onLoading }) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [mode, setMode] = useState("file"); // "file" or "text"
    const [textInput, setTextInput] = useState("");
    const [uploading, setUploading] = useState(false);
    const fileRef = useRef(null);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
        else if (e.type === "dragleave") setDragActive(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setSelectedFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const getFileIcon = (filename) => {
        const ext = "." + filename.split(".").pop().toLowerCase();
        const found = SUPPORTED.find((s) => s.ext === ext);
        return found ? found.icon : "📁";
    };

    const handleUpload = async () => {
        if (mode === "text") {
            if (!textInput.trim() || textInput.trim().length < 50) {
                onError("Please enter at least 50 characters.");
                return;
            }
            setUploading(true);
            onLoading(true);
            try {
                const result = await uploadText(textInput, userId);
                if (result.success) {
                    onSuccess(result.data);
                } else {
                    onError(result.message || "Processing failed.");
                }
            } catch (err) {
                onError(err.message || "Connection error.");
            } finally {
                setUploading(false);
                onLoading(false);
            }
            return;
        }

        if (!selectedFile) {
            onError("Please select a file first.");
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            onError("File too large. Maximum 10MB allowed.");
            return;
        }

        setUploading(true);
        onLoading(true);
        try {
            const result = await uploadFile(selectedFile, userId);
            if (result.success) {
                onSuccess(result.data);
            } else {
                onError(result.message || "Upload failed.");
            }
        } catch (err) {
            onError(err.message || "Connection error. Is the backend running?");
        } finally {
            setUploading(false);
            onLoading(false);
        }
    };

    return (
        <div className="card upload-card">
            <h2>📤 Upload Document</h2>

            {/* Mode Toggle */}
            <div className="mode-toggle">
                <button
                    className={`toggle-btn ${mode === "file" ? "active" : ""}`}
                    onClick={() => setMode("file")}
                >
                    📁 Upload File
                </button>
                <button
                    className={`toggle-btn ${mode === "text" ? "active" : ""}`}
                    onClick={() => setMode("text")}
                >
                    ✏️ Paste Text
                </button>
            </div>

            {mode === "file" ? (
                <>
                    {/* Drop Zone */}
                    <div
                        className={`upload-area ${dragActive ? "drag-active" : ""}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => fileRef.current?.click()}
                    >
                        <input
                            type="file"
                            ref={fileRef}
                            onChange={handleFileSelect}
                            accept=".pdf,.docx,.txt,.pptx,.xlsx,.csv,.md,.png,.jpg,.jpeg"
                            hidden
                        />

                        {selectedFile ? (
                            <div className="selected-file">
                                <span className="file-icon">{getFileIcon(selectedFile.name)}</span>
                                <div>
                                    <p className="file-name">{selectedFile.name}</p>
                                    <p className="file-size">
                                        {(selectedFile.size / 1024).toFixed(1)} KB
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="drop-prompt">
                                <span className="drop-icon">📂</span>
                                <p>Drag & drop your file here</p>
                                <p className="drop-hint">or click to browse</p>
                            </div>
                        )}
                    </div>

                    {/* Supported Formats */}
                    <div className="format-list">
                        {SUPPORTED.map((fmt) => (
                            <span key={fmt.ext} className="format-badge">
                                {fmt.icon} {fmt.label}
                            </span>
                        ))}
                    </div>
                </>
            ) : (
                /* Text Input Mode */
                <textarea
                    className="text-input"
                    placeholder="Paste your text here (English or Urdu)... Minimum 50 characters."
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    rows={8}
                />
            )}

            {/* Upload Button */}
            <button
                className="upload-btn"
                onClick={handleUpload}
                disabled={uploading || (mode === "file" && !selectedFile)}
            >
                {uploading ? (
                    <>⏳ Processing...</>
                ) : (
                    <>🚀 {mode === "file" ? "Upload & Process" : "Process Text"}</>
                )}
            </button>
        </div>
    );
}
