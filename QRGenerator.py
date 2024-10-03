import qrcode
import streamlit as st
from io import BytesIO
import xml.etree.ElementTree as ET

def generate_qr_code(url, format="png"):
    if format == "svg":
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img_matrix = qr.get_matrix()  # Obtén la matriz binaria (True/False) del código QR
        svg_data = create_optimized_svg_from_matrix(img_matrix)
        svg_output = BytesIO(svg_data.encode("utf-8"))
        return svg_output
    else:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        output = BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output

def create_optimized_svg_from_matrix(matrix):
    # Tamaño de cada celda en el código QR
    unit_size = 10
    width = len(matrix[0]) * unit_size
    height = len(matrix) * unit_size

    svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(width), height=str(height))
    path_data = []

    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x]:  # Si es una celda negra (1)
                # Comprobar bordes y vecinos para dibujar las líneas correspondientes

                # Comprobar borde superior
                if y == 0 or not matrix[y-1][x]:
                    path_data.append(f"M{x*unit_size},{y*unit_size} h{unit_size}")

                # Comprobar borde inferior
                if y == len(matrix) - 1 or not matrix[y+1][x]:
                    path_data.append(f"M{x*unit_size},{(y+1)*unit_size} h{unit_size}")

                # Comprobar borde izquierdo
                if x == 0 or not matrix[y][x-1]:
                    path_data.append(f"M{x*unit_size},{y*unit_size} v{unit_size}")

                # Comprobar borde derecho
                if x == len(matrix[y]) - 1 or not matrix[y][x+1]:
                    path_data.append(f"M{(x+1)*unit_size},{y*unit_size} v{unit_size}")

    # Unir todas las líneas en un solo path SVG
    path = ET.SubElement(svg, "path", d=" ".join(path_data), fill="none", stroke="black", stroke_width="1")
    return ET.tostring(svg, encoding="unicode")

# Crear la aplicación Streamlit
st.set_page_config(page_title="QR Code Generator", page_icon="🌐", layout="centered")
st.title("QR Code Generator")

# Entrada de URL
url = st.text_input("Enter the URL")

# Opción de formato (PNG o SVG)
format_option = st.selectbox("Select the file format", ("PNG", "SVG"))

if st.button("Generate QR Code"):
    # Genera el QR en el formato seleccionado
    file_extension = format_option.lower()
    qr_code = generate_qr_code(url, format=file_extension)
    
    if file_extension == "png":
        st.image(qr_code, use_column_width=True)  # Muestra la imagen si es PNG
    
    # Botón de descarga
    st.download_button(
        label=f"Download QR as {file_extension.upper()}",
        data=qr_code,
        file_name=f"qr_code.{file_extension}",
        mime="image/svg+xml" if file_extension == "svg" else "image/png"
    )
