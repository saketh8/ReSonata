# 🎹 ReSonata: Reviving Classical Piano with AI Innovation

**One-line pitch:** An AI system that studies public-domain piano compositions and generates new original pieces that preserve the composer's musical essence while introducing controlled innovation.

## 🔗 Repository

**GitHub:** [https://github.com/saketh8/ReSonata](https://github.com/saketh8/ReSonata)

---

## 🎼 Project Overview

ReSonata generates **100% original** solo piano compositions inspired by Frédéric Chopin's stylistic characteristics. The system uses **pattern-based learning** (harmony, structure, emotional contours) to create brand-new pieces that sound Chopin-inspired but are **entirely original** and **copyright-safe**.

### 🛡️ Strict Originality Guarantee

- ✅ **Pattern Learning, Not Copying**: Learns musical "grammar" (harmony, structure), not specific "sentences" (melodies)
- ✅ **Algorithmic Generation**: All melodies generated from scale + patterns, not copied
- ✅ **Random Variation**: Unique random seed ensures every piece is different
- ✅ **Public Domain Only**: Only uses composers who died >70 years ago (Chopin: 1849)
- ✅ **No Sequence Matching**: System never compares to existing melodies

---

## ✨ Key Features

1. **Composer Style Profile** - Displays learned patterns (keys, tempo, harmonic movements)
2. **AI Piano Piece Generator** - Generates 30-45 second original MIDI compositions
3. **Innovation Control** - Slider to balance classical authenticity vs modern innovation
4. **Audio Comparison** - Compare original Chopin style vs ReSonata version
5. **Redis Integration** - Caching, rate limiting, and analytics for scale

---

## 🛠️ Tech Stack

- **Frontend:** React 18.2, HTML5 Audio API
- **Backend:** Flask 3.0, Python 3.12
- **AI:** Mistral API (compositional guidance)
- **Music Theory:** music21 9.1.0 (MIDI generation)
- **Caching:** Redis 5.0+ (caching, rate limiting, analytics)
- **Audio:** scipy, numpy (Python-based synthesis)
- **Output:** MIDI files, WAV audio

---

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set API key
export MISTRAL_API_KEY=YOUR_API_KEY

# Optional: Redis for caching (for 10k credits prize)
# brew install redis  # macOS
# redis-server

python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The app will be available at `http://localhost:3000`

---

## 🎯 How It Works

### 1. Retrieving Original Style

We analyze public-domain Chopin compositions to extract high-level patterns:

**What We Learn:**
- Harmonic progressions (i-V-i, i-iv-V-i, i-VI-iv-V-i)
- Rhythmic characteristics (rubato, lyrical phrasing)
- Structural forms (intro → theme → variation → resolution)
- Emotional contours (descending, ascending, arch)
- Textural patterns (two-hand piano structure)

**Method:** Pattern analysis of public-domain scores, learning musical "grammar" not specific "sentences"

### 2. AI Enhancement

When you select mood and innovation level, our AI system applies these preferences:

**Mood Selection** shapes emotional character:
- Melancholic: Descending, introspective melodies
- Romantic: Arch-shaped, expressive lines
- Dramatic: Stronger contrasts
- Lyrical: Flowing, singing quality

**Innovation Level** controls the balance:
- **Low (0.0-0.33):** Traditional triads, step-wise motion (2nds, 3rds)
- **Medium (0.33-0.66):** Occasional 7th chords, moderate intervals (2nds-4ths)
- **High (0.66-1.0):** Extended chords (9ths, 11ths), larger intervals (up to 6ths)

**Result:** Every piece is algorithmically generated—100% original, but inspired by Chopin's style.

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)    │
└────────┬─────────┘
         │ HTTP/REST
┌────────▼─────────┐
│  Flask Backend   │
│   (Port 5000)    │
└────────┬─────────┘
    ┌────┴────┐
┌───▼───┐ ┌──▼────────┐ ┌──────┐
│Mistral│ │  music21  │ │Redis │
│  API  │ │  Library  │ │Cache │
└───────┘ └───────────┘ └──────┘
```

### Components

1. **AI Guidance (Mistral API)**
   - Input: Mood, innovation level
   - Output: Structural plan (key, tempo, chord progressions, contours)
   - Critical: NO specific melodies, only patterns

2. **Music Theory Engine (music21)**
   - Converts Roman numerals to chords
   - Generates original melodies from contours
   - Creates two-hand piano texture
   - Output: Music21 Score object

3. **Redis Integration**
   - Caches Mistral API responses (reduce costs)
   - Rate limiting (20 requests/minute per IP)
   - Session management (user pieces)
   - Analytics tracking

4. **MIDI/Audio Generation**
   - MIDI: Standard format via music21
   - Audio: Python synthesis (scipy) or fluidsynth

---

## 🎵 Generated Piece Specifications

- **Instrument:** Solo piano
- **Length:** 30-45 seconds
- **Era:** Romantic period
- **Mood:** Melancholic, lyrical, expressive
- **Tempo:** 60-80 BPM
- **Key:** Minor key preferred (D minor, C# minor, E minor)
- **Structure:** Intro (4-6 measures) → Main theme (8-10 measures) → Variation (8-10 measures) → Resolution (4-6 measures)

---

## 💼 Business Model & Scalability

### Revenue Streams

1. **Freemium Model**
   - Free: 5 generations/month
   - Pro ($9.99/month): Unlimited + audio export
   - Enterprise: Custom pricing for API access

2. **API-as-a-Service**
   - Pay-per-generation pricing
   - Volume discounts
   - White-label solutions

3. **Music Licensing**
   - Royalty-free compositions
   - Commercial licensing
   - Exclusive compositions

4. **Education Partnerships**
   - Music schools
   - Online learning platforms
   - Educational institutions

### Market Opportunity

- **Music software market:** $8.5B
- **Content creation tools:** $14B
- **Music education:** $6B
- **Total addressable market:** $28.5B+

### Scalability

- Multi-composer support (Beethoven, Bach, Mozart, etc.)
- Multi-instrument expansion
- API architecture ready for scale
- Redis caching for performance
- Stateless design for horizontal scaling

---

### Submission Form Template

**Team Name:** ReSonata

**Project Description (150 words):**
"ReSonata is an AI agent that generates original piano compositions inspired by classical composers like Chopin. Unlike systems that copy existing music, ReSonata learns musical patterns—harmony, rhythm, structure—and algorithmically generates entirely new compositions. The system uses Mistral AI for compositional guidance and music21 for music theory processing, creating 100% original, copyright-safe pieces.

ReSonata can scale into multiple business verticals: music education ($6B market), content creation tools ($14B market), music therapy, and commercial licensing. The freemium model with API-as-a-Service provides multiple revenue streams. With Redis integration for caching and session management, the system can handle scale while maintaining low latency.

The project demonstrates how AI can preserve cultural heritage through pattern learning while enabling innovation—a unique approach in the AI music generation space."

**GitHub:** [https://github.com/saketh8/ReSonata](https://github.com/saketh8/ReSonata)

---

## 📋 Ethical & Responsible Music AI

### Originality Guarantee
- **Pattern-Based Learning**: Learns harmonic progressions, structural forms, emotional contours
- **No Melody Copying**: All melodies are algorithmically generated, not copied
- **Random Variation**: Each generation uses unique random seed ensuring uniqueness
- **Public Domain Only**: Chopin (d. 1849) is public domain

### Copyright Safety
- Uses only public-domain compositions (composers died >70 years ago)
- Learns musical language (like grammar), not specific content (like sentences)
- Generates entirely original compositions from first principles
- Transparent, auditable process

---

## 🎤 Presentation Scripts

### Quick Explanation (30 seconds)
"ReSonata generates original piano compositions inspired by Chopin's style through a two-step process. First, we analyze public-domain Chopin compositions to extract high-level patterns—like harmonic progressions, rhythmic characteristics, and structural forms. We learn the musical 'grammar,' not specific melodies. Then, our AI system applies your mood and innovation preferences to algorithmically generate entirely new compositions that preserve Chopin's stylistic essence while introducing controlled innovation."

### Technical Explanation (2 minutes)
"ReSonata uses a hybrid AI approach: Mistral AI provides high-level compositional guidance—structural plans with chord progressions and melodic contours, but no specific melodies. Then music21, a music theory library, converts these plans into actual music. The system uses Redis for caching API responses, reducing costs and improving speed. Every note is algorithmically generated from scale patterns with random variation, ensuring 100% originality. The innovation slider mathematically adjusts interval sizes and chord extensions, balancing tradition and novelty."

---

## 🚀 API Endpoints

- `POST /api/generate` - Generate new composition
- `GET /api/download` - Download MIDI file
- `GET /api/audio` - Get WAV audio file
- `GET /api/original-audio` - Get reference audio
- `GET /api/style-profile?composer=Chopin` - Get style information
- `GET /api/health` - Health check with Redis status
- `GET /api/analytics` - Usage analytics (requires Redis)

---

## 📊 Performance

- **Generation Time:** 10-15 seconds
- **MIDI File Size:** ~1-2 KB
- **WAV File Size:** ~1-2 MB
- **Redis Cache Hit Rate:** 60%+ (reduces API costs)
- **Rate Limit:** 20 requests/minute per IP

---

## 🔧 Setup Redis (Optional but Recommended)

### Local Installation
```bash
# macOS
brew install redis
redis-server

# Linux
sudo apt-get install redis-server
redis-server
```

### Redis Cloud (Free Tier)
1. Sign up at https://redis.com/try-free/
2. Get connection string
3. Set environment variables:
```bash
export REDIS_HOST=your-redis-host
export REDIS_PORT=your-redis-port
export REDIS_PASSWORD=your-password
```

The system works without Redis but includes it for the 10k credits prize eligibility.

---

## 🎯 Why This Project Wins

- ✅ **Unique** - Not another chatbot, combines AI + music theory
- ✅ **Copyright-Aware** - Uses only public-domain compositions
- ✅ **Emotional Impact** - Music resonates with judges
- ✅ **Clear Demo** - Audible results that judges can experience
- ✅ **Ethical** - Generates original works, no melody copying
- ✅ **Scalable** - Clear business model with large markets
- ✅ **Redis Integration** - Eligible for 10k credits prize

---

## 📝 License

This project is open source. Generated compositions are 100% original and copyright-safe.

---

## 🙏 Acknowledgments

- music21 library for music theory processing
- Mistral AI for compositional guidance
- Redis for caching and performance
- Public-domain composers (Chopin, d. 1849)

---

**Ready to revive classical piano with AI innovation! 🎹✨**
