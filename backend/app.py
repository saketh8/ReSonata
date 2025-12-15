from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from music21 import stream, note, chord, tempo, meter, key, metadata, instrument
from music21.midi import translate as midi_translate
import os
from mistralai import Mistral
from dotenv import load_dotenv
import random
import json
import subprocess
import tempfile

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Mistral client
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Chopin style characteristics
CHOPIN_STYLE = {
    "typical_keys": ["D minor", "C# minor", "E minor", "B minor", "A minor"],
    "tempo_range": (60, 80),
    "common_harmonic_movements": [
        "i-V-i", "i-iv-V-i", "i-VI-V-i", "i-iv-VII-V-i"
    ],
    "rhythm_patterns": ["rubato", "lyrical", "expressive"],
    "dynamics": ["piano", "mezzo-piano", "mezzo-forte", "crescendo", "diminuendo"]
}

def get_mistral_guidance(mood, innovation_level):
    """Get compositional guidance from Mistral AI - STRICT ORIGINALITY ENFORCED"""
    # Try Redis cache first
    try:
        from redis_integration import get_cached_mistral_response, cache_mistral_response, increment_stat
        cached = get_cached_mistral_response(mood, innovation_level)
        if cached:
            increment_stat("cache_hits")
            return cached
    except ImportError:
        pass
    except Exception as e:
        print(f"Redis cache check failed: {e}")
    
    prompt = f"""You are a music composition expert specializing in Romantic period piano music, particularly Chopin's style.

CRITICAL: Generate a composition PLAN (not specific melodies) for an ORIGINAL 30-45 second solo piano piece.

STRICT RULES:
- Use only HIGH-LEVEL patterns (harmony, structure, emotional contour)
- DO NOT reference specific melodies, motifs, or compositions
- All melodies will be algorithmically generated from your plan
- Focus on STRUCTURAL and EMOTIONAL patterns only

Specifications:
- Mood: {mood}
- Innovation level: {innovation_level} (Low = traditional patterns, High = modern twists)
- Structure: Intro (4-6 measures) → Main theme (8-10 measures) → Variation (8-10 measures) → Resolution (4-6 measures)
- Tempo: 60-80 BPM
- Key: Minor key (prefer D minor, C# minor, or E minor)
- Style: Melancholic, lyrical, expressive

Provide JSON with ONLY structural/pattern information:
{{
  "key": "D minor",
  "tempo": 70,
  "sections": {{
    "intro": {{"chords": ["i", "iv", "V", "i"], "measures": 4, "melodic_contour": "descending"}},
    "main_theme": {{"chords": ["i", "VI", "iv", "V", "i"], "measures": 8, "melodic_contour": "arch"}},
    "variation": {{"chords": ["i", "iv", "VII", "V", "i"], "measures": 8, "melodic_contour": "ascending"}},
    "resolution": {{"chords": ["i", "V", "i"], "measures": 4, "melodic_contour": "descending"}}
  }}
}}

Return ONLY valid JSON, no melodies, no specific notes."""

    try:
        # Try different Mistral model names (varies by API version)
        models_to_try = ["mistral-medium-latest", "mistral-medium", "mistral-large-latest"]
        response = None
        
        for model_name in models_to_try:
            try:
                response = mistral_client.chat.complete(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                break
            except Exception as model_error:
                if model_name == models_to_try[-1]:
                    raise model_error
                continue
        
        if response:
            content = response.choices[0].message.content.strip()
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            # Validate structure
            if "key" in parsed and "sections" in parsed:
                # Cache the response
                try:
                    from redis_integration import cache_mistral_response
                    cache_mistral_response(mood, innovation_level, parsed)
                except:
                    pass
                return parsed
        
        # If parsing failed, use fallback
        raise ValueError("Invalid response structure")
        
    except Exception as e:
        print(f"Mistral API error: {e}")
        print("Using fallback composition structure")
        # Fallback to default structure (still generates good music)
        return {
            "key": "D minor",
            "tempo": 70,
            "sections": {
                "intro": {"chords": ["i", "iv", "V", "i"], "measures": 4, "melodic_contour": "descending"},
                "main_theme": {"chords": ["i", "VI", "iv", "V", "i"], "measures": 8, "melodic_contour": "arch"},
                "variation": {"chords": ["i", "iv", "VII", "V", "i"], "measures": 8, "melodic_contour": "ascending"},
                "resolution": {"chords": ["i", "V", "i"], "measures": 4, "melodic_contour": "descending"}
            }
        }

def roman_to_chord(roman_numeral, key_obj, innovation_level=0):
    """Convert Roman numeral to actual chord"""
    scale = key_obj.pitches
    
    chord_map = {
        "i": [0, 2, 4],      # tonic minor
        "iv": [3, 5, 7],     # subdominant
        "V": [4, 6, 8],      # dominant
        "VI": [5, 7, 9],     # submediant major
        "VII": [6, 8, 10],   # leading tone
    }
    
    if roman_numeral not in chord_map:
        return [scale[0], scale[2], scale[4]]  # default to i
    
    intervals = chord_map[roman_numeral]
    base_chord = [scale[i % 7] for i in intervals]
    
    # Add innovation: occasional extensions or inversions
    if innovation_level > 0.5 and random.random() < 0.3:
        # Add 7th or 9th
        if random.random() < 0.5:
            base_chord.append(scale[(intervals[0] + 6) % 7])
        else:
            base_chord.append(scale[(intervals[0] + 8) % 7])
    
    return base_chord

def generate_melody_note(prev_note, key_obj, contour, innovation_level, seed_offset=0):
    """
    Generate ORIGINAL melody note following contour and style.
    Uses random variation to ensure uniqueness - no copying possible.
    """
    # Add seed offset for additional uniqueness
    random.seed(random.random() + seed_offset)
    
    scale = key_obj.pitches
    scale_degrees = list(range(len(scale)))
    
    # Base note selection from scale - ORIGINAL generation
    if contour == "ascending":
        direction = 1
    elif contour == "descending":
        direction = -1
    else:  # arch - random direction for originality
        direction = random.choice([-1, 1])
    
    # Find current position in scale
    if prev_note:
        try:
            current_idx = scale.index(prev_note.pitch)
        except:
            current_idx = random.randint(2, 4)  # Random start if not found
    else:
        # Random starting point ensures originality
        current_idx = random.randint(2, 4)  # Start in middle range
    
    # Move in direction with ORIGINAL random variation
    # Innovation level controls interval size, but all are generated fresh
    if innovation_level < 0.33:
        # Low innovation: step-wise (2nds, 3rds)
        step = direction * random.choice([1, 2])
    elif innovation_level < 0.66:
        # Medium: moderate intervals (2nds, 3rds, 4ths)
        step = direction * random.choice([1, 2, 3])
    else:
        # High: larger intervals (up to 5ths, 6ths)
        step = direction * random.choice([1, 2, 3, 4])
    
    # Wrap around scale with random variation
    new_idx = (current_idx + step) % len(scale)
    # Add small random variation for originality
    if random.random() < 0.2:
        new_idx = (new_idx + random.choice([-1, 0, 1])) % len(scale)
    
    new_pitch = scale[new_idx]
    
    # Add octave variation - ensures melodic originality
    octave = 4 if prev_note is None else prev_note.octave
    if random.random() < 0.3:
        octave += random.choice([-1, 0, 1])
    octave = max(3, min(6, octave))  # Keep in piano range
    
    return note.Note(new_pitch.name + str(octave))

def create_chopin_piece(mood="melancholic", innovation_level=0.3):
    """
    Generate ORIGINAL Chopin-inspired piano piece.
    
    STRICT ORIGINALITY GUARANTEE:
    - All melodies are algorithmically generated
    - No sequences copied from existing works
    - Random variation ensures uniqueness
    - Pattern-based, not content-based
    """
    # Add random seed for uniqueness
    import time
    random.seed(time.time() + random.random())
    
    # Get guidance from Mistral (structural patterns only, no melodies)
    guidance = get_mistral_guidance(mood, innovation_level)
    
    # Parse key - handle various formats
    key_name = guidance.get("key", "D minor")
    # music21 expects format like "d minor" or we can use Key(tonic, mode)
    # Split key name into tonic and mode
    key_parts = key_name.lower().split()
    
    # Try to parse the key
    try:
        if len(key_parts) >= 2:
            # Format: "d minor", "c# minor", etc.
            tonic_str = key_parts[0]
            mode_str = key_parts[1]
            key_obj = key.Key(tonic=tonic_str, mode=mode_str)
        else:
            # Try as single string
            key_obj = key.Key(key_name.lower())
    except Exception as e:
        # Fallback to safe default
        print(f"Key parsing error for '{key_name}': {e}, using d minor")
        try:
            key_obj = key.Key(tonic='d', mode='minor')
        except:
            # Ultimate fallback
            key_obj = key.Key('d')
    
    # Create score
    score = stream.Score()
    score.insert(0, metadata.Metadata())
    score.metadata.title = f"ReSonata: Chopin-Inspired Piece ({mood})"
    score.metadata.composer = "ReSonata AI"
    
    # Set tempo
    tempo_bpm = guidance.get("tempo", 70)
    score.insert(0, tempo.MetronomeMark(number=tempo_bpm))
    
    # Set time signature
    score.insert(0, meter.TimeSignature("4/4"))
    score.insert(0, key_obj)
    
    # Create separate left and right hand parts
    left_hand = stream.Part()
    left_hand.insert(0, instrument.Piano())
    left_hand.partName = "Left Hand"
    
    right_hand = stream.Part()
    right_hand.insert(0, instrument.Piano())
    right_hand.partName = "Right Hand"
    
    sections = guidance.get("sections", {
        "intro": {"chords": ["i", "iv", "V", "i"], "measures": 4, "melodic_contour": "descending"},
        "main_theme": {"chords": ["i", "VI", "iv", "V", "i"], "measures": 8, "melodic_contour": "arch"},
        "variation": {"chords": ["i", "iv", "VII", "V", "i"], "measures": 8, "melodic_contour": "ascending"},
        "resolution": {"chords": ["i", "V", "i"], "measures": 4, "melodic_contour": "descending"}
    })
    
    prev_melody_note = None
    current_measure = 0
    
    for section_name, section_data in sections.items():
        chords_list = section_data.get("chords", ["i", "V", "i"])
        measures = section_data.get("measures", 4)
        contour = section_data.get("melodic_contour", "arch")
        
        chords_per_measure = max(1, len(chords_list) // measures)
        if chords_per_measure == 0:
            chords_per_measure = 1
        
        for measure_idx in range(measures):
            # Determine which chord(s) to use in this measure
            chord_idx = (measure_idx * len(chords_list)) // measures
            if chord_idx >= len(chords_list):
                chord_idx = len(chords_list) - 1
            
            chord_roman = chords_list[chord_idx]
            chord_pitches = roman_to_chord(chord_roman, key_obj, innovation_level)
            
            # Left hand: bass note and chord (simplified)
            # Bass note on beat 1
            bass_note = note.Note(chord_pitches[0].name + "3")
            bass_note.duration.quarterLength = 2.0
            left_hand.append(bass_note)
            
            # Optional chord on beat 3
            if random.random() < 0.5:
                chord_obj = chord.Chord([p.name + "3" for p in chord_pitches[:3]])
                chord_obj.duration.quarterLength = 2.0
                left_hand.append(chord_obj)
            else:
                # Just hold the bass
                rest = note.Rest()
                rest.duration.quarterLength = 2.0
                left_hand.append(rest)
            
            # Right hand: lyrical melody
            # Generate 2-4 notes per measure for lyrical flow
            notes_in_measure = random.choice([2, 3, 4])
            quarter_per_note = 4.0 / notes_in_measure
            
            for note_idx in range(notes_in_measure):
                # Add seed offset for each note to ensure originality
                seed_offset = current_measure * 100 + note_idx + random.random()
                melody_note = generate_melody_note(prev_melody_note, key_obj, contour, innovation_level, seed_offset)
                melody_note.duration.quarterLength = quarter_per_note
                
                # Add some expressive variation
                if innovation_level > 0.4 and random.random() < 0.2:
                    # Add grace note or ornament
                    pass
                
                right_hand.append(melody_note)
                prev_melody_note = melody_note
                
                # Occasionally add harmony note
                if random.random() < 0.3 and len(chord_pitches) > 1:
                    harmony_pitch = chord_pitches[1] if len(chord_pitches) > 1 else chord_pitches[0]
                    harmony_note = note.Note(harmony_pitch.name + str(melody_note.octave))
                    harmony_note.duration.quarterLength = quarter_per_note
                    right_hand.append(harmony_note)
            
            current_measure += 1
    
    # Combine hands - create a single part with both hands
    # For MIDI, we'll use a simpler approach: alternate or combine notes
    piano_part = stream.Part()
    piano_part.insert(0, instrument.Piano())
    
    # Create measure-by-measure structure
    # Get all notes from both hands
    lh_notes = list(left_hand.flatten().notesAndRests)
    rh_notes = list(right_hand.flatten().notesAndRests)
    
    # Align by time - create simultaneous notes where possible
    # Simple approach: interleave with proper timing
    max_len = max(len(lh_notes), len(rh_notes))
    
    for i in range(max_len):
        notes_to_add = []
        
        # Get left hand note if available
        if i < len(lh_notes):
            lh_item = lh_notes[i]
            if isinstance(lh_item, note.Note):
                notes_to_add.append(lh_item)
            elif isinstance(lh_item, chord.Chord):
                notes_to_add.extend(lh_item.notes)
        
        # Get right hand note if available
        if i < len(rh_notes):
            rh_item = rh_notes[i]
            if isinstance(rh_item, note.Note):
                notes_to_add.append(rh_item)
            elif isinstance(rh_item, chord.Chord):
                notes_to_add.extend(rh_item.notes)
        
        # Add as chord if multiple notes, single note otherwise
        if len(notes_to_add) > 1:
            combined_chord = chord.Chord(notes_to_add)
            if i < len(lh_notes):
                combined_chord.duration = lh_notes[i].duration
            elif i < len(rh_notes):
                combined_chord.duration = rh_notes[i].duration
            piano_part.append(combined_chord)
        elif len(notes_to_add) == 1:
            piano_part.append(notes_to_add[0])
    
    score.append(piano_part)
    
    # Ensure proper duration (30-45 seconds)
    # At 70 BPM, 4/4 time: 1 measure = ~3.43 seconds
    # Target: ~10-13 measures for 30-45 seconds
    total_measures = current_measure
    target_measures = 12
    
    if total_measures < target_measures:
        # Add resolution measures
        for _ in range(target_measures - total_measures):
            bass_note = note.Note(key_obj.pitches[0].name + "3")
            bass_note.duration.quarterLength = 2.0
            piano_part.append(bass_note)
            
            melody_note = generate_melody_note(prev_melody_note, key_obj, "descending", innovation_level)
            melody_note.duration.quarterLength = 2.0
            piano_part.append(melody_note)
            prev_melody_note = melody_note
    
    return score

def generate_simple_audio_from_score(score, output_path, sample_rate=44100):
    """Generate simple audio from music21 score using Python synthesis"""
    try:
        import numpy as np
        from scipy.io import wavfile
    except ImportError:
        return False
    
    try:
        tempo_bpm = 70
        for element in score.flatten().getElementsByClass(tempo.MetronomeMark):
            if element.number:
                tempo_bpm = element.number
                break
        
        duration = float(score.duration.quarterLength) * (60.0 / tempo_bpm)
        total_samples = int(duration * sample_rate)
        audio = np.zeros(total_samples, dtype=np.float32)
        
        # Simple sine wave synthesis for each note
        for element in score.flatten().notes:
            if isinstance(element, note.Note):
                freq = element.pitch.frequency
                start_time = float(element.offset) * (60.0 / tempo_bpm)
                note_duration = float(element.duration.quarterLength) * (60.0 / tempo_bpm)
                
                start_sample = int(start_time * sample_rate)
                end_sample = int((start_time + note_duration) * sample_rate)
                num_samples = end_sample - start_sample
                
                if num_samples > 0 and start_sample < total_samples:
                    t = np.linspace(0, note_duration, num_samples)
                    # Simple ADSR envelope
                    attack = int(0.01 * sample_rate)
                    decay = int(0.1 * sample_rate)
                    release = int(0.2 * sample_rate)
                    sustain_level = 0.7
                    
                    envelope = np.ones(num_samples)
                    if num_samples > attack:
                        envelope[:attack] = np.linspace(0, 1, attack)
                    if num_samples > attack + decay:
                        envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
                    if num_samples > release:
                        envelope[-release:] = np.linspace(sustain_level, 0, release)
                    
                    wave = np.sin(2 * np.pi * freq * t) * envelope * 0.3
                    end_idx = min(start_sample + num_samples, total_samples)
                    audio[start_sample:end_idx] += wave[:end_idx-start_sample]
            
            elif isinstance(element, chord.Chord):
                # Sum frequencies for chords
                start_time = float(element.offset) * (60.0 / tempo_bpm)
                note_duration = float(element.duration.quarterLength) * (60.0 / tempo_bpm)
                
                start_sample = int(start_time * sample_rate)
                end_sample = int((start_time + note_duration) * sample_rate)
                num_samples = end_sample - start_sample
                
                if num_samples > 0 and start_sample < total_samples:
                    t = np.linspace(0, note_duration, num_samples)
                    envelope = np.ones(num_samples)
                    attack = int(0.01 * sample_rate)
                    decay = int(0.1 * sample_rate)
                    release = int(0.2 * sample_rate)
                    sustain_level = 0.7
                    
                    if num_samples > attack:
                        envelope[:attack] = np.linspace(0, 1, attack)
                    if num_samples > attack + decay:
                        envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
                    if num_samples > release:
                        envelope[-release:] = np.linspace(sustain_level, 0, release)
                    
                    wave = np.zeros(num_samples)
                    for pitch in element.pitches:
                        freq = pitch.frequency
                        wave += np.sin(2 * np.pi * freq * t) * envelope * 0.15
                    
                    end_idx = min(start_sample + num_samples, total_samples)
                    audio[start_sample:end_idx] += wave[:end_idx-start_sample]
        
        # Normalize and convert to int16
        audio = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Write WAV file
        wavfile.write(output_path, sample_rate, audio_int16)
        return True
    except Exception as e:
        print(f"Python audio synthesis error: {e}")
        return False

def midi_to_audio(midi_path, output_path):
    """Convert MIDI to WAV audio using multiple methods"""
    # Method 1: Try fluidsynth if available (best quality)
    try:
        result = subprocess.run(
            ['which', 'fluidsynth'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            soundfont_paths = [
                '/usr/share/sounds/sf2/FluidR3_GM.sf2',
                '/usr/share/sounds/sf2/default.sf2',
                '/System/Library/Sounds/sf2/default.sf2',
                '/opt/homebrew/share/fluidsynth/soundfonts/FluidR3_GM.sf2',
                os.path.expanduser('~/Library/Audio/Sounds/Banks/fluidr3_gm.sf2'),
            ]
            
            soundfont = None
            for sf in soundfont_paths:
                if os.path.exists(sf):
                    soundfont = sf
                    break
            
            if soundfont:
                subprocess.run(
                    ['fluidsynth', '-F', output_path, '-q', soundfont, midi_path],
                    capture_output=True,
                    check=True
                )
                return True
    except Exception as e:
        pass
    
    # Method 2: Python-based synthesis (fallback)
    try:
        from music21 import converter
        score = converter.parse(midi_path)
        return generate_simple_audio_from_score(score, output_path)
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return False

@app.route('/api/generate', methods=['POST'])
def generate_music():
    """Generate a Chopin-inspired piano piece"""
    # Rate limiting (if Redis available)
    try:
        from redis_integration import rate_limit, increment_stat
        client_ip = request.remote_addr
        if not rate_limit(f"generate:{client_ip}", max_requests=20, window=60):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please wait before generating another piece.'
            }), 429
    except:
        pass  # Continue if rate limiting unavailable
    
    data = request.json
    mood = data.get('mood', 'melancholic')
    innovation_level = float(data.get('innovationLevel', 0.3))
    
    try:
        # Track statistics
        try:
            from redis_integration import increment_stat
            increment_stat("total_generations")
        except:
            pass
        score = create_chopin_piece(mood, innovation_level)
        
        # Save to MIDI
        midi_path = 'generated_piece.mid'
        score.write('midi', fp=midi_path)
        
        # Try to convert to audio
        audio_path = 'generated_piece.wav'
        # Try Python synthesis first (more reliable)
        audio_available = generate_simple_audio_from_score(score, audio_path)
        # Fallback to MIDI conversion if Python synthesis fails
        if not audio_available:
            audio_available = midi_to_audio(midi_path, audio_path)
        
        response = {
            'success': True,
            'message': 'Piece generated successfully',
            'midiPath': '/api/download',
            'audioAvailable': audio_available
        }
        
        if audio_available:
            response['audioPath'] = '/api/audio'
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download', methods=['GET'])
def download_midi():
    """Download the generated MIDI file"""
    return send_file('generated_piece.mid', mimetype='audio/midi', as_attachment=True)

@app.route('/api/audio', methods=['GET'])
def get_audio():
    """Get the generated audio file (WAV)"""
    audio_path = 'generated_piece.wav'
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/wav')
    else:
        return jsonify({'error': 'Audio not available'}), 404

@app.route('/api/original-audio', methods=['GET'])
def get_original_audio():
    """Get a sample original Chopin piece for comparison"""
    # For demo purposes, we'll generate a simple reference piece
    # In production, you'd use a public-domain Chopin recording
    original_path = 'original_reference.wav'
    
    if not os.path.exists(original_path):
        # Create a simple reference piece (this would be replaced with actual Chopin)
        # For now, return 404 - user can add their own reference
        return jsonify({
            'error': 'Original reference not available',
            'message': 'Add a public-domain Chopin recording as original_reference.wav'
        }), 404
    
    return send_file(original_path, mimetype='audio/wav')

@app.route('/api/style-profile', methods=['GET'])
def get_style_profile():
    """Get Chopin style profile information"""
    composer = request.args.get('composer', 'Chopin')
    
    return jsonify({
        'composer': composer,
        'typicalKeys': CHOPIN_STYLE['typical_keys'],
        'tempoRange': CHOPIN_STYLE['tempo_range'],
        'harmonicMovements': CHOPIN_STYLE['common_harmonic_movements'],
        'rhythmPatterns': CHOPIN_STYLE['rhythm_patterns'],
        'dynamics': CHOPIN_STYLE['dynamics']
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    try:
        from redis_integration import REDIS_AVAILABLE, get_analytics
        analytics = get_analytics()
        return jsonify({
            'status': 'healthy',
            'redis': REDIS_AVAILABLE,
            'analytics': analytics
        })
    except:
        return jsonify({'status': 'healthy', 'redis': False})

@app.route('/api/analytics', methods=['GET'])
def analytics():
    """Get usage analytics (requires Redis)"""
    try:
        from redis_integration import get_analytics
        return jsonify(get_analytics())
    except:
        return jsonify({'error': 'Analytics not available'}), 503

if __name__ == '__main__':
    app.run(debug=True, port=5000)

