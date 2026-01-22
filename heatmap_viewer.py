from flask import Flask, render_template, request, send_from_directory
import pathlib
import logging
from obsidian_daily import generate_all_heatmaps

# Initialize Flask app
app = Flask(__name__)

# Set the base directory for heatmaps
BASE_DIR = pathlib.Path(r"D:\jianguo\我的坚果云\obsidian\Personal\2026")
HEATMAP_DIR = BASE_DIR / "heatmaps"

@app.route('/')
def index():
    # Render the main page with options
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_heatmaps():
    year = request.form.get('year', None)
    if not year or not year.isdigit():
        return "Invalid year provided.", 400

    year = int(year)
    try:
        generate_all_heatmaps(BASE_DIR, year)
        return f"Heatmaps for {year} generated successfully!"
    except Exception as e:
        logging.error(f"Error generating heatmaps: {e}")
        return f"Failed to generate heatmaps: {e}", 500

@app.route('/heatmaps/<filename>')
def serve_heatmap(filename):
    # Serve heatmap images from the heatmap directory
    return send_from_directory(HEATMAP_DIR, filename)

if __name__ == '__main__':
    # Ensure the heatmap directory exists
    HEATMAP_DIR.mkdir(exist_ok=True)
    app.run(debug=True)