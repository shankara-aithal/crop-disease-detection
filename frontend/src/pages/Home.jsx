// src/pages/Home.jsx
import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { predictionAPI } from '../api/client'
import toast from 'react-hot-toast'
import './Home.css'

export default function Home() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      const f = acceptedFiles[0]
      setFile(f)
      const reader = new FileReader()
      reader.onload = e => setPreview(e.target.result)
      reader.readAsDataURL(f)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxSize: 16 * 1024 * 1024,
  })

  const handlePredict = async e => {
    e.preventDefault()
    if (!file) {
      toast.error('Please select an image')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('leaf_image', file)
      const res = await predictionAPI.predict(formData)
      toast.success('Prediction complete!')
      navigate(`/result/${res.data.id}`)
    } catch (err) {
      toast.error(err.response?.data?.error || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const clearFile = () => {
    setFile(null)
    setPreview(null)
  }

  return (
    <main className="home">
      <div className="container">
        <div className="hero">
          <div className="hero-left">
            <h1>Detect Crop Disease Instantly</h1>
            <p>Upload a leaf image and our AI will identify the disease, give you a confidence score, and suggest treatment in seconds.</p>
            <div className="pills">
              <span className="pill">📸 54,000+ Training Images</span>
              <span className="pill">🔬 38 Disease Classes</span>
              <span className="pill">📊 ~93% Accuracy</span>
            </div>
          </div>

          <div className="upload-box">
            <form onSubmit={handlePredict}>
              <div {...getRootProps()} className={`drop-zone ${isDragActive ? 'active' : ''} ${preview ? 'has-file' : ''}`}>
                <input {...getInputProps()} />
                {!preview ? (
                  <>
                    <div className="drop-icon">☁️</div>
                    <p>Drag & drop your leaf image here</p>
                    <small>or click to browse · JPG, PNG, WEBP</small>
                  </>
                ) : (
                  <>
                    <img src={preview} alt="preview" className="preview" />
                    <button type="button" onClick={clearFile} className="clear-btn">✕ Remove</button>
                  </>
                )}
              </div>

              <div className="tips">
                💡 <strong>Tips:</strong> Clear close-up photo · Good lighting · Affected leaf visible
              </div>

              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? '🔄 Analysing...' : '🔍 Analyse Leaf'}
              </button>
            </form>
          </div>
        </div>

        <section className="crops-section">
          <h2>Supported Crops</h2>
          <div className="crop-grid">
            {['🍅 Tomato', '🥔 Potato', '🌽 Corn', '🌶️ Pepper', '🍎 Apple', '🍇 Grape', '🍑 Peach', '🍒 Cherry', '🫐 Blueberry', '🍓 Strawberry', '🫘 Soybean', '🟡 Squash'].map(crop => (
              <span key={crop} className="crop-chip">{crop}</span>
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}
