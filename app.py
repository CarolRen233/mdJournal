from flask import Flask, request, jsonify, send_from_directory
import os
import pathlib
import logging
from datetime import datetime
import frontmatter
import win32com.client
from config import BASE_DIR

app = Flask(__name__)

# Constants
logging.basicConfig(level=logging.INFO)

# Ensure the base directory exists
BASE_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/get_outlook', methods=['GET'])
def get_outlook():
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        calendar = ns.GetDefaultFolder(9)  # olFolderCalendar
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")
        today = datetime.now()
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        restr = f"[Start] >= '{start.strftime('%m/%d/%Y %I:%M %p')}' AND [Start] <= '{end.strftime('%m/%d/%Y %I:%M %p')}'"
        restricted = items.Restrict(restr)
        events = []
        for item in restricted:
            events.append({
                "subject": item.Subject,
                "start": item.Start.strftime('%Y-%m-%d %H:%M:%S'),
                "end": item.End.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(events)
    except Exception as e:
        logging.error(f"Error fetching Outlook events: {e}")
        return jsonify({"error": "Failed to fetch Outlook events."}), 500

@app.route('/save_diary', methods=['POST'])
def save_diary():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided."}), 400

    try:
        today = datetime.now()
        filename = BASE_DIR / f"{today.strftime('%Y%m%d')}.md"
        if filename.exists():
            return jsonify({"error": "Diary already exists."}), 409

        # Build the diary content
        meta = {
            "Date": today.isoformat(),
            "Location": data.get("location", "东涌镇,中国,广东省,广州市 南沙区"),
            "Emotion": data.get("emotion"),
            "Confidence": data.get("confidence"),
            "Appetite": data.get("appetite")
        }
        body = "\n".join([
            "## 今日日程",
            "",
            *[f"- {event['start']} - {event['end']}: {event['subject']}" for event in data.get("events", [])],
            "",
            "## 随笔",
            "",
            data.get("diary", "")
        ])
        post = frontmatter.Post(body, **meta)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        return jsonify({"message": "Diary saved successfully."})
    except Exception as e:
        logging.error(f"Error saving diary: {e}")
        return jsonify({"error": "Failed to save diary."}), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    try:
        records = []
        for file in BASE_DIR.glob("*.md"):
            post = frontmatter.load(file)
            records.append({
                "date": post.metadata.get("Date"),
                "emotion": post.metadata.get("Emotion"),
                "appetite": post.metadata.get("Appetite"),
                "confidence": post.metadata.get("Confidence")
            })
        return jsonify(records)
    except Exception as e:
        logging.error(f"Error fetching history: {e}")
        return jsonify({"error": "Failed to fetch history."}), 500

@app.route('/heatmaps/<filename>')
def serve_heatmap(filename):
    return send_from_directory(BASE_DIR / "heatmaps", filename)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)