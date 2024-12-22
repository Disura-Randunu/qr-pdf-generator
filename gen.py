from PIL import Image
from fpdf import FPDF
from PIL import ImageOps  # Add at the top of your script

import os

# Parameters
qr_folder = "qr_images"  # Folder containing QR images
output_pdf = "output_qr_codes.pdf"  # Output PDF file name
tile_size = 25  # Size of each QR code tile (in mm)
tiles_per_row = 8  # Number of QR codes per row
page_margin = 5  # Margin around the page (in mm)
spacing = 10  # Space between tiles (in mm)
border_size = 1  # Border size in pixels



# Initialize PDF
pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=page_margin)

# Get list of QR images
qr_files = [f for f in os.listdir(qr_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Calculate tile positions
page_width, page_height = 210, 297  # A4 dimensions in mm
usable_width = page_width - 2 * page_margin
usable_height = page_height - 2 * page_margin
tiles_per_column = int(usable_height // (tile_size + spacing))
tiles_per_page = tiles_per_row * tiles_per_column

# Function to add a page
def add_page():
    pdf.add_page()
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')

# Process images
current_tile = 0
add_page()

for index, qr_file in enumerate(qr_files):
    img_path = os.path.join(qr_folder, qr_file)
    img = Image.open(img_path)
    img.thumbnail((tile_size * 3.78, tile_size * 3.78))  # Resize to fit within the tile size

    # Add borders of equal size on all sides (top, left, right, and bottom)
    if img.mode != "RGB":
        img = img.convert("RGB")  # Convert to RGB if necessary
    
    # Apply the same border on all sides (left, top, right, and bottom)
    img_with_border = ImageOps.expand(img, (border_size, border_size, border_size, border_size), fill="black")
    
    # Save to a temporary file
    temp_path = f"temp_{index}.jpg"
    img_with_border.save(temp_path)

    # Calculate positions for the image
    x_pos = page_margin + (current_tile % tiles_per_row) * (tile_size + spacing)
    y_pos = page_margin + (current_tile // tiles_per_row) * (tile_size + spacing)

    # Add image to PDF
    pdf.image(temp_path, x=x_pos, y=y_pos, w=tile_size, h=tile_size)

    # Get the file name without extension
    file_name_without_extension = os.path.splitext(qr_file)[0]

    # Add the filename text **inside the border, below the QR image**
    text_x = x_pos + border_size  # Align text with the border
    text_y = y_pos + tile_size + 2  # Place it just below the QR code inside the border (a small gap)
    pdf.set_xy(text_x, text_y)
    pdf.set_font("Arial", size=8)  # Font size for the file name
    pdf.cell(tile_size - (border_size * 2), 5, file_name_without_extension, align="C")  # Fit within the border width

    # Add a bottom border **connected to left and right borders**
    border_y_position = text_y + 5  # 5 pixels after the filename text (no overlap)
    pdf.line(x_pos, border_y_position, x_pos + tile_size, border_y_position)  # Add bottom border after the text

    # Add left and right connecting borders (to form a complete border around the QR code and filename)
    pdf.line(x_pos, y_pos, x_pos, border_y_position)  # Left border from top to bottom
    pdf.line(x_pos + tile_size, y_pos, x_pos + tile_size, border_y_position)  # Right border from top to bottom

    current_tile += 1

    # Add a new page if the current page is full
    if current_tile >= tiles_per_page:
        current_tile = 0
        add_page()

    # Clean up temporary files
    os.remove(temp_path)
# Save PDF
pdf.output(output_pdf)
print(f"PDF saved as {output_pdf}")
