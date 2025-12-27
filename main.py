import streamlit as st
import streamlit.components.v1 as components
import yt_dlp
import os
import time
import csv
from datetime import datetime

# --- Configuration ---
DOWNLOAD_FOLDER = "downloads"
LOG_FILE = "activity_log.csv"

# Ensure download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Ensure Log file exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Video Title", "Video Link", "IP Address"])

# --- Helper Function for IP ---
def get_remote_ip():
    """
    Attempts to retrieve the client IP address using st.context.headers.
    """
    try:
        # st.context.headers is the new supported way to access headers
        headers = st.context.headers
        
        # Look for X-Forwarded-For (standard for proxies)
        if headers and "X-Forwarded-For" in headers:
            return headers["X-Forwarded-For"].split(",")[0]
        
        # Look for Real-IP
        if headers and "X-Real-Ip" in headers:
            return headers["X-Real-Ip"]
            
    except Exception:
        pass
    return "Unknown"

# --- App Layout ---
st.set_page_config(page_title="Shorts to MP3", page_icon="🎵")

# --- Custom CSS (Hiding Menu, adding Footer, Floating Buttons) ---
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT UI ELEMENTS */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* FLOATING SOCIAL BUTTONS */
    .floating-container {
        position: fixed;
        bottom: 80px; 
        right: 20px;
        display: flex;
        flex-direction: row;
        gap: 15px;
        z-index: 9999;
    }
    .bubble-link {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        text-decoration: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .bubble-link:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.3);
    }
    .bubble-link img {
        width: 24px;
        height: 24px;
        object-fit: contain;
    }

    /* CUSTOM FOOTER */
    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117; 
        color: #808495;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #262730;
        z-index: 100;
    }
    </style>

    <div class="floating-container">
        <a href="https://linktr.ee/defonotgus" target="_blank" class="bubble-link" style="background-color: #43E660;" title="Linktree">
            <img src="https://cdn.simpleicons.org/linktree/white" alt="Linktree" />
        </a>
        <a href="https://github.com/DefoNotGus" target="_blank" class="bubble-link" style="background-color: #333333;" title="GitHub">
            <img src="https://cdn.simpleicons.org/github/white" alt="GitHub" />
        </a>
        <a href="https://www.buymeacoffee.com/defonotgus" target="_blank" class="bubble-link" style="background-color: #FFDD00;" title="Buy me a coffee">
            <img src="https://cdn.simpleicons.org/buymeacoffee/000000" alt="Buy Me A Coffee" />
        </a>
    </div>

    <div class="custom-footer">
        Notice: Your IP address, video title, and download time are logged for security and analytics purposes. <br>
        © 2026 DefoNotGus. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🎵 YT-Fetch")
st.write("Paste a link or type a search term to get the MP3.")

# --- Input ---
url = st.text_input("YouTube URL or Search Query")

# --- Logic ---
if st.button("Download Audio"):
    if not url:
        st.error("Please enter a link or search term.")
    else:
        status_text = st.empty()
        status_text.info("Processing... This may take a few seconds.")

        if "youtube.com" not in url and "youtu.be" not in url:
            target = f"ytsearch1:{url}"
            st.caption(f"Searching for: '{url}'")
        else:
            target = url

        timestamp = int(time.time())
        output_template = f"{DOWNLOAD_FOLDER}/audio_{timestamp}_%(title)s.%(ext)s"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Extract Info
                info = ydl.extract_info(target, download=False)
                
                if 'entries' in info:
                    video_title = info['entries'][0]['title']
                else:
                    video_title = info['title']
                
                status_text.info(f"Downloading: {video_title}...")

                # --- LOGGING START ---
                try:
                    user_ip = get_remote_ip()
                    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now(), video_title, target, user_ip])
                except Exception as log_err:
                    print(f"Logging failed: {log_err}")
                # --- LOGGING END ---

                # 2. Download
                error_code = ydl.download([target])

            # 3. Find the generated file
            files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(f"audio_{timestamp}") and f.endswith(".mp3")]
            
            if files:
                file_path = os.path.join(DOWNLOAD_FOLDER, files[0])
                
                with open(file_path, "rb") as file:
                    file_bytes = file.read()
                
                status_text.success("Conversion Complete!")
                
                st.download_button(
                    label="⬇️ Click to Save MP3",
                    data=file_bytes,
                    file_name=f"{video_title}.mp3",
                    mime="audio/mpeg"
                )
                
                os.remove(file_path)
            else:
                st.error("Error: File was not found after processing.")

        except Exception as e:
            st.error(f"An error occurred: {e}")