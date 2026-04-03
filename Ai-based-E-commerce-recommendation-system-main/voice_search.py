import streamlit as st
import speech_recognition as sr

def sidebar_product_search():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎙 Voice Product Search")

    def voice_to_text():
        r = sr.Recognizer()
        # Note: Microphone requires PyAudio to be installed locally
        try:
            with sr.Microphone() as source:
                st.sidebar.info("🎙 Listening... Speak product name")
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            
            text = r.recognize_google(audio)
            return text
        except sr.RequestError:
            st.sidebar.error("API unavailable")
            return ""
        except sr.UnknownValueError:
            st.sidebar.error("Could not understand audio")
            return ""
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
            st.sidebar.warning("Note: Voice search requires a microphone and PyAudio installed.")
            return ""

    selected_product = st.sidebar.text_input(
        "Search Products",
        placeholder="Search products...",
        label_visibility="collapsed",
        key="sidebar_search_input_unique"
    )

    if st.sidebar.button("🎙 Start Voice Search", use_container_width=True):
        spoken_text = voice_to_text()
        if spoken_text:
            st.sidebar.success(f"You said: {spoken_text}")
            return spoken_text
        
    return selected_product
