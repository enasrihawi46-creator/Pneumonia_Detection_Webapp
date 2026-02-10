from flask import Flask, render_template, request, send_file, session
import os
import numpy as np
from datetime import datetime

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display


# ===== تسجيل الخط العربي =====
pdfmetrics.registerFont(TTFont('Amiri', 'fonts/Amiri-Regular.ttf'))

def ar(text):
    return get_display(arabic_reshaper.reshape(text))


app = Flask(__name__)
app.secret_key = "longo_secret_key"


# ================== إعدادات المجلدات ==================
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================== تحميل المودل ==================
MODEL_PATH = "vgg19_model_best.h5"
model = load_model(MODEL_PATH)


# ================== المسارات ==================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ================== التنبؤ ==================
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return "لم يتم رفع أي صورة", 400

    file = request.files["image"]
    if file.filename == "":
        return "لم يتم اختيار ملف", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    img = image.load_img(filepath, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    pred_full = model.predict(img_array)
    probability_raw = float(pred_full[0][0])

    threshold = 0.6

    if probability_raw > threshold:
        label = "PNEUMONIA"
        label_ar = "التهاب رئوي"
        display_probability = probability_raw
        status_class = "status-pneumonia"
    else:
        label = "NORMAL"
        label_ar = "سليم"
        display_probability = 1 - probability_raw
        status_class = "status-normal"

    confidence_percent = round(display_probability * 100, 2)

    # تخزين بالجلسة للتقرير فقط
    session["last_result"] = {
        "prediction": label,
        "prediction_ar": label_ar,
        "confidence": confidence_percent,
        "image_path": filepath
    }

    return render_template(
        "result.html",
        image_url=filepath,
        prediction=label,
        probability=confidence_percent,
        status_class=status_class
    )


# ================== تحميل التقرير==================
@app.route("/download_report")
def download_report():

    data = session.get("last_result")
    if not data:
        return "لا يوجد تقرير", 400

    filename = "prediction_report.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    # ===== عنوان =====
    c.setFont("Amiri", 24)
    c.setFillColor(colors.teal)
    c.drawRightString(550, 800, ar("تقرير تحليل صورة الأشعة السينية للرئة"))
    c.line(50, 780, 550, 780)

    # ===== معلومات =====
    y = 740
    c.setFont("Amiri", 16)
    c.setFillColor(colors.black)
    c.drawRightString(550, y, ar(":نظام الكشف عن الالتهاب الرئوي باستخدام التعلم العميق"))

    y -= 30

    if data["prediction"] == "PNEUMONIA":
        c.setFillColor(colors.red)
    else:
        c.setFillColor(colors.green)

    c.drawRightString(550, y, ar(f"التشخيص: {data['prediction_ar']}"))

    y -= 30
    c.setFillColor(colors.black)
    c.drawRightString(550, y, ar(f"نسبة الثقة: {data['confidence']} %"))

    y -= 30
    c.drawRightString(
        550,
        y,
        ar("التاريخ: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    # ===== صورة الأشعة =====
    try:
        img = ImageReader(data["image_path"])
        c.drawImage(img, 150, 300, width=300, height=250, preserveAspectRatio=True)
    except:
        c.drawRightString(550, 450, ar("تعذر تحميل الصورة"))

    # ===== مربع تنبيه =====
    c.setFillColor(colors.lightseagreen)
    c.rect(40, 230, 520, 45, fill=1)

    c.setFillColor(colors.black)
    c.setFont("Amiri", 14)
    c.drawRightString(
        540,
        250,
        ar("تنبيه: هذا التقرير لأغراض تعليمية ولا يغني عن استشارة الطبيب")
    )

    # ===== خط فاصل بعد التنبيه =====
    c.setStrokeColor(colors.black)
    c.line(60, 170, 540, 170)

    # ===== تذييل (خط أصغر) =====
    c.setFillColor(colors.teal)
    c.setFont("Amiri", 12)  
    c.drawCentredString(400, 40, ar("تم إنشاء التقرير بواسطة نظام LUNGO"))

    c.save()
    return send_file(filename, as_attachment=True)



# ================== تشغيل التطبيق ==================
if __name__ == "__main__":
    app.run(debug=True)
