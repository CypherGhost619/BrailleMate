from gtts import gTTS

def text_to_speech(text, filename, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return filename
    except:
        return None
