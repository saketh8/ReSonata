"""
Script to create a reference Chopin-style piece for comparison.
This generates a simple reference piece that demonstrates Chopin's style.
In production, you would use an actual public-domain Chopin recording.
"""

from music21 import stream, note, chord, tempo, meter, key, instrument
from music21.midi import translate as midi_translate
import os
import numpy as np
try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Note: scipy not available. Install with: pip install scipy")

def create_reference_piece():
    """Create a simple Chopin-style reference piece"""
    
    # Create score
    score = stream.Score()
    score.insert(0, key.Key('d', 'minor'))
    score.insert(0, tempo.MetronomeMark(number=70))
    score.insert(0, meter.TimeSignature('4/4'))
    
    # Create piano part
    piano_part = stream.Part()
    piano_part.insert(0, instrument.Piano())
    
    # Simple Chopin-style progression: i-iv-V-i
    # D minor - G minor - A major - D minor
    
    # Measure 1: D minor
    piano_part.append(chord.Chord(['D3', 'F3', 'A3', 'D4']))
    piano_part.append(note.Rest(quarterLength=3.0))
    
    # Measure 2: G minor
    piano_part.append(chord.Chord(['G3', 'Bb3', 'D4', 'G4']))
    piano_part.append(note.Rest(quarterLength=3.0))
    
    # Measure 3: A major
    piano_part.append(chord.Chord(['A3', 'C#4', 'E4', 'A4']))
    piano_part.append(note.Rest(quarterLength=3.0))
    
    # Measure 4: D minor (resolution)
    piano_part.append(chord.Chord(['D3', 'F3', 'A3', 'D4']))
    piano_part.append(note.Rest(quarterLength=3.0))
    
    score.append(piano_part)
    
    # Save MIDI
    midi_path = 'original_reference.mid'
    score.write('midi', fp=midi_path)
    print(f"Reference MIDI created: {midi_path}")
    
    # Try to convert to audio using multiple methods
    audio_created = False
    
    # Method 1: Try fluidsynth with soundfont
    try:
        import subprocess
        result = subprocess.run(['which', 'fluidsynth'], capture_output=True, text=True)
        if result.returncode == 0:
            # Check common soundfont locations
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
                result = subprocess.run(
                    ['fluidsynth', '-F', 'original_reference.wav', '-q', soundfont, midi_path],
                    capture_output=True,
                    check=True
                )
                print("✅ Reference audio created: original_reference.wav (using fluidsynth)")
                audio_created = True
    except Exception as e:
        pass
    
    # Method 2: Try using music21's built-in audio (requires timidity or other)
    if not audio_created:
        try:
            # Use music21's audio capabilities if available
            score.write('wav', fp='original_reference.wav')
            if os.path.exists('original_reference.wav'):
                print("✅ Reference audio created: original_reference.wav (using music21)")
                audio_created = True
        except Exception as e:
            pass
    
    # Method 3: Simple Python-based audio generation (fallback)
    if not audio_created and SCIPY_AVAILABLE:
        try:
            print("Generating audio using Python synthesis...")
            generate_simple_audio(score, 'original_reference.wav')
            if os.path.exists('original_reference.wav'):
                print("✅ Reference audio created: original_reference.wav (using Python synthesis)")
                audio_created = True
        except Exception as e:
            print(f"Python synthesis failed: {e}")
    
    if not audio_created:
        print("\n⚠️  Could not automatically create audio file.")
        print("Options to create audio:")
        print("1. Install a soundfont: brew install fluid-soundfont-gm")
        print("2. Convert manually: Open original_reference.mid in GarageBand/MuseScore and export as WAV")
        print("3. Use online converter: https://www.online-convert.com/convert/midi-to-wav")
        print("4. Install scipy: pip install scipy (for Python-based synthesis)")

def generate_simple_audio(score, output_path, sample_rate=44100):
    """Generate simple audio from music21 score using Python"""
    duration = float(score.duration.quarterLength) * (60.0 / 70.0)  # 70 BPM
    total_samples = int(duration * sample_rate)
    audio = np.zeros(total_samples, dtype=np.float32)
    
    # Simple sine wave synthesis for each note
    for element in score.flatten().notes:
        if isinstance(element, note.Note):
            freq = element.pitch.frequency
            start_time = float(element.offset) * (60.0 / 70.0)
            note_duration = float(element.duration.quarterLength) * (60.0 / 70.0)
            
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
            start_time = float(element.offset) * (60.0 / 70.0)
            note_duration = float(element.duration.quarterLength) * (60.0 / 70.0)
            
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

if __name__ == '__main__':
    create_reference_piece()

