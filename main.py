import streamlit as st
import streamlit.components.v1 as components
import yt_dlp
import os
import time

# --- Configuration ---
DOWNLOAD_FOLDER = "downloads"

# Ensure download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- App Layout ---
st.set_page_config(page_title="Shorts to MP3", page_icon="🎵")
st.title("🎵 YT-Fetch")

st.markdown(
    """
    <style>
    .floating-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: flex;
        flex-direction: row; /* Align bubbles in a row */
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
    </style>

    <div class="floating-container">
        <!-- Linktree -->
        <a href="https://linktr.ee/defonotgus" target="_blank" class="bubble-link" style="background-color: #43E660;" title="Linktree">
            <img src="https://cdn.simpleicons.org/linktree/white" alt="Linktree" />
        </a>
        <!-- GitHub -->
        <a href="https://github.com/DefoNotGus" target="_blank" class="bubble-link" style="background-color: #333333;" title="GitHub">
            <img src="https://cdn.simpleicons.org/github/white" alt="GitHub" />
        </a>
        <!-- Buy Me a Coffee -->
        <a href="https://www.buymeacoffee.com/defonotgus" target="_blank" class="bubble-link" style="background-color: #FFDD00;" title="Buy me a coffee">
            <img src="https://cdn.simpleicons.org/buymeacoffee/000000" alt="Buy Me A Coffee" />
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

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
            'noplaylist': True, # Download only single video, not playlists
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Extract Info (to get the title for display)
                info = ydl.extract_info(target, download=False)
                
                # Handle search results structure
                if 'entries' in info:
                    video_title = info['entries'][0]['title']
                else:
                    video_title = info['title']
                
                status_text.info(f"Downloading: {video_title}...")

                # 2. Download
                error_code = ydl.download([target])

            # 3. Find the generated file
            # yt-dlp might change the extension during conversion, so we look for the newest mp3
            # We use the timestamp we generated to ensure we get the right file
            files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(f"audio_{timestamp}") and f.endswith(".mp3")]
            
            if files:
                file_path = os.path.join(DOWNLOAD_FOLDER, files[0])
                
                # Open in binary mode for the download button
                with open(file_path, "rb") as file:
                    file_bytes = file.read()
                
                status_text.success("Conversion Complete!")
                
                # 4. Provide Download Button
                st.download_button(
                    label="⬇️ Click to Save MP3",
                    data=file_bytes,
                    file_name=f"{video_title}.mp3",
                    mime="audio/mpeg"
                )
                
                # 5. Clean up the file after download
                os.remove(file_path)
                
            else:
                st.error("Error: File was not found after processing.")

        except Exception as e:
            st.error(f"An error occurred: {e}")