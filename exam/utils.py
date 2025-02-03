# utils.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib.units import inch
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os
from reportlab.lib.utils import ImageReader
from django.core.files.storage import default_storage
from pathlib import Path
from django.templatetags.static import static
from PIL import Image, ImageDraw, ImageFont




# def generate_certificate(user, attempt_date):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=landscape(letter))
#     # Define page size
#     page_width, page_height = letter

    
#     # Define multiple possible paths for the certificate template
#     possible_paths = [
#         # Direct path in static folder
#         os.path.join(settings.BASE_DIR, 'static', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
#         # Path in staticfiles
#         os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
#         # Path relative to media root
#         os.path.join(settings.MEDIA_ROOT, 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
#         # Direct path in app folder
#         os.path.join(settings.BASE_DIR, 'exam', 'static', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg')
#     ]
    
#     # Find the first existing path
#     base_image_path = os.path.join(settings.BASE_DIR, static('images/Cream_Bordered_Appreciation_Certificate.jpg'))

#     for path in possible_paths:
#         if os.path.exists(path):
#             base_image_path = path
#             break
    
#     if base_image_path is None:
#         raise FileNotFoundError(
#             f"Certificate template not found. Tried paths: {possible_paths}. "
#             f"Please ensure the image is placed in one of these locations."
#         )
    

#     # Load the image to get its actual dimensions
#     image = ImageReader(base_image_path)
#     image_width, image_height = image.getSize()


#     # Optionally, scale the image to fit the page
#     scaled_width = min(image_width, page_width)
#     scaled_height = min(image_height, page_height)

#     # Draw the base certificate image
#     p.drawImage(image, 0, 0, width=scaled_width, height=scaled_height)
    
#     # Add user name
#     p.setFont("Helvetica-Bold", 30)
#     p.setFillColorRGB(0, 0, 0)
#     p.drawCentredString(image_width/2, image_height/2, f"{user.full_name}")
    
#     # Add date
#     p.setFont("Helvetica", 20)
#     formatted_date = attempt_date.strftime('%B %d, %Y')
#     p.drawCentredString(image_width/2, image_height/3, formatted_date)
    
#     p.save()
#     buffer.seek(0)
#     return buffer

def generate_certificate(user,attempt_date):
    try:
        # Define multiple possible paths for the certificate template
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
            os.path.join(settings.MEDIA_ROOT, 'images', 'Cream_Bordered_Appreciation_Certificate.jpg'),
            os.path.join(settings.BASE_DIR, 'exam', 'static', 'images', 'Cream_Bordered_Appreciation_Certificate.jpg')
        ]
        
        # Find the first existing path
        base_image_path = os.path.join(settings.BASE_DIR, static('images/Cream_Bordered_Appreciation_Certificate.jpg'))
        for path in possible_paths:
            if os.path.exists(path):
                base_image_path = path
                break
        
        if base_image_path is None:
            raise FileNotFoundError(f"Certificate template not found. Tried paths: {possible_paths}. Please ensure the image is placed in one of these locations.")

        # Open the base image
        base_image = Image.open(base_image_path)
        draw = ImageDraw.Draw(base_image)
        
        # Use the default font (no font file required)
        # Set font and text color
        font = ImageFont.truetype("arial.ttf", 45)  # Adjust path and font size as needed
  
        
        # Define text properties
        text_color = (0, 0, 0)  # Black text (change if necessary)
        user_name = user.full_name
        # formatted_date = attempt_date.strftime('%B %d, %Y')
        
        # Get the dimensions of the image for positioning text centrally
        image_width, image_height = base_image.size
        
        # Calculate text bounding box using textbbox for Pillow versions >=9.2
        user_bbox = draw.textbbox((0, 0), user_name, font=font)
        text_width = user_bbox[2] - user_bbox[0]
        text_height = user_bbox[3] - user_bbox[1]

        x_position =(image_width - text_width) / 2
        print(x_position)
        x_position -= 50
        print(x_position)
        # Calculate current y position (center of the image)
        y_position = image_height / 2

        # Move the text 50px above the current position
        y_position -= 78  # Move text 50px upwards


        # Add user name at the center
        draw.text((x_position,y_position), user_name, fill=text_color, font=font)
        
        # Calculate bounding box for the date
        # date_bbox = draw.textbbox((0, 0), formatted_date, font=font)
        # date_width = date_bbox[2] - date_bbox[0]
        # date_height = date_bbox[3] - date_bbox[1]

        # Add the date below the name
        # draw.text(((image_width - date_width) / 2, image_height / 1.5), formatted_date, fill=text_color, font=font)

        # Save the generated image to a BytesIO object
        buffer = BytesIO()
        base_image.save(buffer, format="JPEG")
        buffer.seek(0)

        # Now, you can either return the buffer for download or email it
        return buffer

    except Exception as e:
        print(f"Error: {e}")
        return None

# Sending the certificate via email

def send_certificate_email(user, attempt_date):
    buffer = generate_certificate(user, attempt_date)
    
    if buffer is not None:
        email = EmailMessage(
            subject="Your Certificate",
            body="Dear {0},\n\nPlease find attached your certificate.".format(user.full_name),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        # Attach the certificate as an email attachment
        email.attach('certificate.jpg', buffer.getvalue(), 'image/jpeg')

        # Send the email
        email.send()
        print(f"Email sent to {user.email}")
    else:
        print("Error generating the certificate.")