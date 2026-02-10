/* ================================================= */
/* 1. جلب عناصر الصفحة من الـ DOM                   */
/* ================================================= */

// منطقة السحب والإفلات
const dropArea = document.getElementById("dropArea");

// حقل اختيار الملف المخفي
const fileInput = document.getElementById("fileInput");

// عناصر المعاينة
const previewContainer = document.getElementById("previewContainer");
const imagePreview = document.getElementById("imagePreview");

// زر حذف الصورة
const removeBtn = document.getElementById("removeBtn");

// نموذج الرفع
const uploadForm = document.getElementById("uploadForm");

// مؤشر التحميل (Loader)
const loader = document.querySelector(".loader");


/* ================================================= */
/* 2. الحالة الابتدائية                              */
/* ================================================= */

// في البداية تأكدي أن زر الحذف مخفي
removeBtn.style.display = "none";


/* ================================================= */
/* 3. الضغط على منطقة الرفع                          */
/* ================================================= */

// عند الضغط على منطقة السحب → افتحي نافذة اختيار الملفات
dropArea.addEventListener("click", () => fileInput.click());


/* ================================================= */
/* 4. اختيار ملف من الجهاز                           */
/* ================================================= */

// عند اختيار صورة من الجهاز → عرض المعاينة
fileInput.addEventListener("change", function () {
    if (this.files && this.files[0]) {
        showPreview(this.files[0]);
    }
});


/* ================================================= */
/* 5. دعم السحب والإفلات (Drag & Drop)              */
/* ================================================= */

// أثناء سحب الملف فوق المنطقة
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();                 // منع السلوك الافتراضي
    dropArea.classList.add("dragover"); // إضافة تأثير بصري
});

// عند مغادرة الملف لمنطقة السحب
dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragover");
});

// عند إفلات الملف داخل المنطقة
dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");

    // إذا وُجد ملف → خزّنيه في input واعرضي المعاينة
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        showPreview(e.dataTransfer.files[0]);
    }
});


/* ================================================= */
/* 6. دالة عرض معاينة الصورة                         */
/* ================================================= */

function showPreview(file) {

    const reader = new FileReader();

    // بعد قراءة الملف → ضعيه كمصدر للصورة
    reader.onload = function (e) {
        imagePreview.src = e.target.result;

        // إظهار صندوق المعاينة
        previewContainer.classList.remove("hidden");

        // إظهار زر الحذف
        removeBtn.style.display = "block";
    };

    // قراءة الصورة كـ DataURL لعرضها في <img>
    reader.readAsDataURL(file);
}


/* ================================================= */
/* 7. حذف الصورة المختارة                            */
/* ================================================= */

// عند الضغط على زر الحذف
removeBtn.addEventListener("click", () => {

    // تفريغ input
    fileInput.value = "";

    // إخفاء المعاينة
    previewContainer.classList.add("hidden");
    imagePreview.src = "";

    // إخفاء زر الحذف مرة أخرى
    removeBtn.style.display = "none";
});


/* ================================================= */
/* 8. عند إرسال النموذج                              */
/* ================================================= */

// عند إرسال النموذج → إظهار اللودر
uploadForm.addEventListener("submit", () => {
    loader.classList.remove("hidden");
});
