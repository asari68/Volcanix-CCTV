import requests
import base64
import io
from flask import Flask, request, jsonify, render_template
from PIL import Image

app = Flask(__name__)

# ======== MODEL CONFIG =========
CLASSIFY_MODEL_URL = "https://classify.roboflow.com/volcanix-nkna6/1"
CLASSIFY_API_KEY = "PwaUtc1AVZCv3mjR6LA6"

SEGMENT_MODEL_URL = "https://outline.roboflow.com/segmentasi-gunungapi-ospcf/1"
SEGMENT_API_KEY = "PwaUtc1AVZCv3mjR6LA6"
# ===============================


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file gambar"}), 400

    file = request.files["file"]

    try:
        # ubah ke base64
        image = Image.open(file.stream).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # ====== 1️⃣ KLASIFIKASI ======
        classify_response = requests.post(
            f"{CLASSIFY_MODEL_URL}?api_key={CLASSIFY_API_KEY}",
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        classification_result = classify_response.json()

        # ====== 2️⃣ SEGMENTASI (HASIL GAMBAR OVERLAY) ======
        segment_response = requests.post(
            f"{SEGMENT_MODEL_URL}?api_key={SEGMENT_API_KEY}&format=image",
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # hasil berupa bytes gambar → ubah jadi base64 untuk dikirim ke frontend
        segment_image_b64 = base64.b64encode(segment_response.content).decode("utf-8")

        return jsonify({
            "classification": classification_result,
            "segmentation": {
                "image": f"data:image/jpeg;base64,{segment_image_b64}"
            }
        })

    except Exception as e:
        return jsonify({"error": f"Gagal memproses gambar: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
