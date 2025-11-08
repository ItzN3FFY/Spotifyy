from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for
import downloader
import os
import time

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_url = request.form["playlist"].strip()
        clean_url = input_url.split("?")[0]
        full_url = downloader.expand_spotify_link(clean_url) if "spotify.link" in clean_url else clean_url
        link_type = downloader.detect_spotify_type(full_url)

        return Response(stream_download(full_url, link_type), mimetype='text/html')
    return render_template("index.html")

def stream_download(url, link_type):
    yield "<pre>"
    try:
        yield f"🔗 Expanded URL: {url}\n"
        if "accounts.spotify.com/login" in url:
            yield "⚠️ This link redirects to Spotify login. Please share a public playlist or track.\n</pre>"
            return

        if link_type == "playlist":
            tracks = downloader.get_tracks_from_playlist(url)
        elif link_type == "track":
            tracks = downloader.get_track_name(url)
        else:
            yield "⚠️ Unsupported Spotify link type.\n</pre>"
            return

        if not tracks:
            yield "⚠️ No tracks found. Please check the link.\n</pre>"
            return

        yield f"✅ Found {len(tracks)} track(s)\n\n"

        for i, track in enumerate(tracks, 1):
            yield f"🎵 [{i}/{len(tracks)}] Downloading: {track}\n"
            try:
                downloader.download_tracks([track])
                yield f"✅ Finished: {track}\n\n"
            except Exception as e:
                yield f"❌ Failed: {track} → {e}\n\n"
            time.sleep(0.5)

        zip_path = downloader.zip_and_cleanup()
        yield f"\n📦 Zipped into: {zip_path}\n"
        yield f"\n<a href='/{zip_path}' download>⬇️ Click here to download ZIP</a>\n"
    except Exception as e:
        print(f"🔥 Internal error: {e}")
        yield f"\n❌ Internal error: {e}\n"
    yield "</pre>"

@app.route("/clear")
def clear_downloads():
    downloader.clear_old_downloads()
    return redirect(url_for("index"))

@app.route("/<path:filename>")
def download_file(filename):
    return send_from_directory(".", filename, as_attachment=True)

app.run(host="0.0.0.0", port=8080)