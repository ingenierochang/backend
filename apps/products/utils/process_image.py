from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def process_image(image_file):
    with Image.open(image_file) as img:
        # Resize image (example sizes)
        thumbnail = img.resize((150, 150), Image.LANCZOS)
        full_size = img.resize((800, 800), Image.LANCZOS)

        # Convert to WebP format and save in a buffer
        thumbnail_buffer = BytesIO()
        thumbnail.save(thumbnail_buffer, format='WebP')
        thumbnail_webp = thumbnail_buffer.getvalue()
        
        full_size_buffer = BytesIO()
        full_size.save(full_size_buffer, format='WebP')
        full_size_webp = full_size_buffer.getvalue()
        
        # Save to Django FileField (assuming you have implemented methods to save these)
        return {
            'thumbnail': ContentFile(thumbnail_webp, 'thumbnail.webp'),
            'full_size': ContentFile(full_size_webp, 'full_size.webp')
        }
