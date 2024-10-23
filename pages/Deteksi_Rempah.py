from PIL import Image
import tensorflow as tf
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import cv2

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title='Rempah Detection😱',
    page_icon='😱',
    layout='wide'
)

# Menu navigasi
selected_tab = option_menu(
    menu_title=None,
    options=["Upload", "Realtime Scan", "Capture"],
    icons=["upload", "camera", "camera-fill"],
    menu_icon="cast",
    default_index=0,
    key="nav",
    orientation="horizontal"
)

# Load model (dengan caching)
@st.cache_resource()
def load_model():
    try:
        model_path = r'rempah_detection_final.keras'
        model = tf.keras.models.load_model(model_path)
        return model
    except IOError:
        st.error(f"Model tidak ditemukan di path: {model_path}")
        return None

model = load_model()

if model is None:
    st.stop()

# Daftar kategori rempah
categories = ['Adas', 'Andaliman', 'Asam Jawa', 'Bawang Bombai', 'Bawang Merah', 'Bawang Putih', 'Biji Ketumbar', 'Bukan Rempah', 'Bunga Lawang', 'Cengkeh', 'Daun Jeruk', 'Daun Kemangi', 'Daun Ketumbar', 'Daun Salam', 'Jahe', 'Jinten', 'Kapulaga', 'Kayu Manis', 'Kayu Secang', 'Kemiri', 'Kemukus', 'Kencur', 'Kluwek', 'Kunyit', 'Lada', 'Lengkuas', 'Pala', 'Saffron', 'Serai', 'Vanili', 'Wijen']

# Dictionary untuk mapping indeks ke nama kategori
int_label = {i: class_name for i, class_name in enumerate(categories)}

# Fungsi untuk preprocessing gambar
def preprocess_image(image):
    """Memuat dan memproses gambar."""
    img = cv2.resize(image, (110, 110))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Fungsi untuk prediksi gambar yang diupload
def predict_uploaded_image(uploaded_file, model, transform, categories):
    """Predicts the class of an uploaded image using the provided model."""
    image = Image.open(uploaded_file).convert('RGB')

    # Simpan gambar ke file sementara
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        image.save(temp_file.name)
        image_path = temp_file.name

    # Preprocessing
    image = transform(image_path)
    img_array = np.array(image)

    # Prediksi
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction)
    predicted_class = categories[predicted_class_index]
    return predicted_class

# Logika untuk setiap tab
if selected_tab == "Upload":
    # Form untuk upload file
    uploaded_file = st.file_uploader("Pilih gambar Anda", type=["jpg", "png", "jpeg"])

    # Prediksi jenis rempah
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption='Gambar yang diunggah', use_column_width=True)

        if st.button('Prediksi'):
            with st.spinner('Sedang memprediksi...'):
                predicted_class = predict_uploaded_image(uploaded_file, model, preprocess_image, int_label)

            st.write(f'Rempah: **{predicted_class}**')

elif selected_tab == "Realtime Scan":
    st.write("Pastikan browser telah memberikan izin akses kamera.")

    # Inisialisasi predicted_class 
    predicted_class = "None" 

    # Frame untuk menampilkan video
    frame_placeholder = st.empty()

    # Tombol untuk menghentikan kamera
    stop = st.button("Stop")
    
    # Inisialisasi key untuk st.camera_input di luar loop
    camera_key = "realtime_camera"
    
   # Loop untuk menampilkan video dan mengambil gambar
    while not stop:  # Loop selama tombol stop tidak ditekan
        picture = st.camera_input("Ambil gambar rempah", key=camera_key) 
        camera_key += str(np.random.randint(1000))
        
        if picture:
            # Konversi gambar dari st.camera_input ke OpenCV
            image = Image.open(picture).convert('RGB')
            frame = np.array(image)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Konversi dari RGB ke BGR

            # Prediksi gambar yang diambil
            with st.spinner('Sedang memprediksi...'):
                preprocessed_image = preprocess_image(frame)
                prediction = model.predict(preprocessed_image)
                predicted_class_index = np.argmax(prediction)
                predicted_class = int_label[predicted_class_index]

            # Menambahkan teks prediksi ke frame
            cv2.putText(frame, f'Rempah: {predicted_class}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(frame, f'Rempah: {predicted_class}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

            # Menampilkan frame di Streamlit
            frame_placeholder.image(frame, channels="BGR")

        if stop:  # Hentikan loop jika tombol stop ditekan
            break
    
    
# Fitur Ambil Gambar
elif selected_tab == "Capture":
    
    # Inisialisasi key untuk st.camera_input di luar loop
    camera_key = "caputre_camera_key" 
    
    st.write("Pastikan browser telah memberikan izin akses kamera.")
    picture = st.camera_input("Ambil gambar rempah", key= "Capture")
    
    if picture:
        st.image(picture, caption='Gambar yang diambil', use_column_width=True)
        if st.button('Prediksi'):
            with st.spinner('Sedang memprediksi...'):
                # Konversi gambar dari st.camera_input ke format yang sesuai untuk model
                image = Image.open(picture).convert('RGB') 
                img_array = preprocess_image(np.array(image))

                prediction = model.predict(img_array)
                predicted_class_index = np.argmax(prediction)
                predicted_class = int_label[predicted_class_index]

            st.write(f'Rempah: **{predicted_class}**')
