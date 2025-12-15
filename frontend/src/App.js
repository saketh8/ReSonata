import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [composer, setComposer] = useState('Chopin');
  const [mood, setMood] = useState('melancholic');
  const [innovationLevel, setInnovationLevel] = useState(0.3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [styleProfile, setStyleProfile] = useState(null);
  const [midiData, setMidiData] = useState(null);
  const [midiUrl, setMidiUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [originalAudioUrl, setOriginalAudioUrl] = useState(null);
  const [isPlayingOriginal, setIsPlayingOriginal] = useState(false);
  const [isPlayingAI, setIsPlayingAI] = useState(false);
  const [audioRef, setAudioRef] = useState(null);
  const [originalAudioRef, setOriginalAudioRef] = useState(null);

  const fetchStyleProfile = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/style-profile`, {
        params: { composer }
      });
      setStyleProfile(response.data);
    } catch (error) {
      console.error('Error fetching style profile:', error);
    }
  }, [composer]);

  useEffect(() => {
    fetchStyleProfile();
  }, [fetchStyleProfile]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, {
        mood,
        innovationLevel
      });

      if (response.data.success) {
        // Download MIDI file
        const midiResponse = await axios.get(`${API_BASE_URL}/download`, {
          responseType: 'blob'
        });
        
        const blob = new Blob([midiResponse.data], { type: 'audio/midi' });
        const url = URL.createObjectURL(blob);
        setMidiData(url);
        setMidiUrl(url);
        
        // Try to get audio if available
        if (response.data.audioAvailable) {
          try {
            const audioResponse = await axios.get(`${API_BASE_URL}/audio`, {
              responseType: 'blob'
            });
            const audioBlob = new Blob([audioResponse.data], { type: 'audio/wav' });
            const audioUrlObj = URL.createObjectURL(audioBlob);
            setAudioUrl(audioUrlObj);
            
            // Create audio element
            const audio = new Audio(audioUrlObj);
            audio.onended = () => setIsPlayingAI(false);
            setAudioRef(audio);
          } catch (error) {
            console.log('Audio not available, using MIDI only');
          }
        }
        
        // Load original audio for comparison
        try {
          const originalResponse = await axios.get(`${API_BASE_URL}/original-audio`, {
            responseType: 'blob'
          });
          const originalBlob = new Blob([originalResponse.data], { type: 'audio/wav' });
          const originalUrlObj = URL.createObjectURL(originalBlob);
          setOriginalAudioUrl(originalUrlObj);
          
          const originalAudio = new Audio(originalUrlObj);
          originalAudio.onended = () => setIsPlayingOriginal(false);
          setOriginalAudioRef(originalAudio);
        } catch (error) {
          console.log('Original audio not available');
        }
        
        alert('Piece generated successfully! Use the comparison player to hear AI vs Original.');
      }
    } catch (error) {
      console.error('Error generating music:', error);
      alert('Error generating music. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlayAI = () => {
    if (audioRef) {
      if (isPlayingAI) {
        audioRef.pause();
        audioRef.currentTime = 0;
        setIsPlayingAI(false);
      } else {
        // Stop original if playing
        if (originalAudioRef && isPlayingOriginal) {
          originalAudioRef.pause();
          originalAudioRef.currentTime = 0;
          setIsPlayingOriginal(false);
        }
        audioRef.play();
        setIsPlayingAI(true);
      }
    } else if (midiUrl) {
      // Fallback to MIDI
      window.open(midiUrl, '_blank');
    } else {
      alert('Please generate a piece first!');
    }
  };

  const handlePlayOriginal = () => {
    if (originalAudioRef) {
      if (isPlayingOriginal) {
        originalAudioRef.pause();
        originalAudioRef.currentTime = 0;
        setIsPlayingOriginal(false);
      } else {
        // Stop AI if playing
        if (audioRef && isPlayingAI) {
          audioRef.pause();
          audioRef.currentTime = 0;
          setIsPlayingAI(false);
        }
        originalAudioRef.play();
        setIsPlayingOriginal(true);
      }
    } else {
      alert('Original audio not available');
    }
  };

  const handleDownload = () => {
    if (midiData) {
      const a = document.createElement('a');
      a.href = midiData;
      a.download = `chopin-inspired-${mood}-${Date.now()}.mid`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const getInnovationLabel = (level) => {
    if (level < 0.33) return 'Low (Traditional)';
    if (level < 0.66) return 'Medium (Balanced)';
    return 'High (Innovative)';
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-icons">
          <span className="music-icon">♫</span>
          <span className="music-icon">♪</span>
          <span className="music-icon">♬</span>
        </div>
        <h1>🎹 ReSonata</h1>
        <p className="subtitle">Reviving Classical Piano with AI Innovation</p>
        <p className="tagline">🎵 Generate original piano pieces inspired by Chopin's style 🎵</p>
        <div className="header-icons">
          <span className="music-icon">♫</span>
          <span className="music-icon">♪</span>
          <span className="music-icon">♬</span>
        </div>
      </header>

      <main className="main-content">
        <div className="controls-panel">
          <div className="control-group">
            <label htmlFor="composer">🎼 Composer</label>
            <select
              id="composer"
              value={composer}
              onChange={(e) => setComposer(e.target.value)}
              disabled
            >
              <option value="Chopin">Frédéric Chopin</option>
            </select>
            <small>📜 Public domain composer (d. 1849)</small>
          </div>

          <div className="control-group">
            <label htmlFor="mood">🎭 Mood</label>
            <select
              id="mood"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
            >
              <option value="melancholic">🎹 Melancholic</option>
              <option value="romantic">💕 Romantic</option>
              <option value="dramatic">⚡ Dramatic</option>
              <option value="lyrical">🎵 Lyrical</option>
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="innovation">
              🎚️ Innovation Level: {getInnovationLabel(innovationLevel)}
            </label>
            <input
              type="range"
              id="innovation"
              min="0"
              max="1"
              step="0.1"
              value={innovationLevel}
              onChange={(e) => setInnovationLevel(parseFloat(e.target.value))}
              className="slider"
            />
            <div className="slider-labels">
              <span>Low (Traditional)</span>
              <span>High (Innovative)</span>
            </div>
            <small>Balances classical authenticity vs modern innovation</small>
          </div>

          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? '🎼 Generating...' : '🎹 Generate Piece 🎹'}
          </button>

          {midiData && (
            <div className="playback-controls">
              <div className="comparison-player">
                <h3>🎵 Audio Comparison 🎵</h3>
                
                <div className="audio-comparison">
                  <div className="audio-player-item">
                    <h4>Original Chopin Style</h4>
                    <button
                      className="play-btn"
                      onClick={handlePlayOriginal}
                      disabled={!originalAudioRef}
                    >
                      {isPlayingOriginal ? '⏸️ Pause' : '▶️ Play Original'}
                    </button>
                    {!originalAudioRef && (
                      <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
                        Reference audio not available
                      </small>
                    )}
                  </div>
                  
                  <div className="audio-player-item">
                    <h4>ReSonata version</h4>
                    <button
                      className="play-btn"
                      onClick={handlePlayAI}
                    >
                      {isPlayingAI ? '⏸️ Pause' : '▶️ Play ReSonata'}
                    </button>
                    {audioUrl ? (
                      <small style={{ display: 'block', marginTop: '5px', color: '#000000', fontWeight: '600' }}>
                        Audio available
                      </small>
                    ) : (
                      <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
                        MIDI only (download to play)
                      </small>
                    )}
                  </div>
                </div>
                
                <button
                  className="download-btn"
                  onClick={handleDownload}
                  style={{ marginTop: '15px', width: '100%' }}
                >
                  💾 Download MIDI File
                </button>
              </div>
            </div>
          )}
        </div>

        {styleProfile && (
          <div className="style-profile">
            <h2>🎼 Chopin Style Profile 🎼</h2>
            <div className="profile-grid">
              <div className="profile-item">
                <strong>🎹 Typical Keys:</strong>
                <p>{styleProfile.typicalKeys.join(', ')}</p>
              </div>
              <div className="profile-item">
                <strong>⏱️ Tempo Range:</strong>
                <p>{styleProfile.tempoRange[0]}-{styleProfile.tempoRange[1]} BPM</p>
              </div>
              <div className="profile-item">
                <strong>🎵 Harmonic Movements:</strong>
                <p>{styleProfile.harmonicMovements.join(', ')}</p>
              </div>
              <div className="profile-item">
                <strong>🎶 Rhythm Patterns:</strong>
                <p>{styleProfile.rhythmPatterns.join(', ')}</p>
              </div>
            </div>
          </div>
        )}

        <div className="process-section">
          <h2>🎹 How It Works 🎹</h2>
          <div className="process-grid">
            <div className="process-item">
              <h3>📚 Retrieving Original Style</h3>
              <p>We analyze public-domain Chopin compositions to extract high-level patterns:</p>
              <ul>
                <li>Harmonic progressions (i-V-i, i-iv-V-i)</li>
                <li>Rhythmic characteristics (rubato, lyrical phrasing)</li>
                <li>Structural forms (intro → theme → variation → resolution)</li>
                <li>Emotional contours (melancholic, expressive)</li>
              </ul>
              <p className="note">We learn the musical "grammar," not specific melodies.</p>
            </div>
            <div className="process-item">
              <h3>🤖 AI Enhancement</h3>
              <p>Our AI system applies your preferences to generate original compositions:</p>
              <ul>
                <li><strong>Mood Selection:</strong> Shapes emotional character (melancholic, romantic, dramatic, lyrical)</li>
                <li><strong>Innovation Level:</strong> Controls balance between traditional harmony and modern twists</li>
                <li><strong>Algorithmic Generation:</strong> Creates entirely new melodies following learned patterns</li>
                <li><strong>Original Output:</strong> Every piece is unique, algorithmically generated</li>
              </ul>
              <p className="note">100% original compositions inspired by Chopin's style.</p>
            </div>
          </div>
        </div>

        <div className="comparison-section">
          <h2>🎹 Before & After Comparison 🎹</h2>
          <div className="comparison-grid">
            <div className="comparison-item">
              <h3>🎼 Original Chopin Style</h3>
              <p>🎵 Lyrical right-hand melodies</p>
              <p>🎹 Supportive left-hand harmony</p>
              <p>🎶 Romantic harmonic progressions</p>
              <p>🎚️ Expressive dynamics and rubato</p>
              <p>🎹 Minor key preferences</p>
            </div>
            <div className="comparison-item">
              <h3>ReSonata version</h3>
              <p>🧠 Learns compositional patterns</p>
              <p>✨ Generates entirely new melodies</p>
              <p>🎯 Preserves stylistic essence</p>
              <p>🚀 Adds controlled innovation</p>
              <p>✅ 100% original composition</p>
            </div>
          </div>
        </div>

        <div className="ethics-section">
          <h2>✨ Ethical & Responsible Music AI ✨</h2>
          <ul>
            <li>✅ Uses only public-domain compositions (composers died >70 years ago)</li>
            <li>✅ No melody copying - learns patterns, not specific works</li>
            <li>✅ Generates entirely original compositions</li>
            <li>✅ Cultural preservation + innovation balance</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default App;

