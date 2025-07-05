import os
from datetime import datetime
from typing import Optional
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from .supabase_client import get_supabase_client
import io


class ImageUploadService:
    
    def process_image(self, image_file: InMemoryUploadedFile, max_width: int = 600, max_height: int = 600, quality: int = 70) -> bytes:
        """
        Process and compress the uploaded image
        """
        try:
            # Open the image
            img = Image.open(image_file)
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize image while maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def upload_profile_image(self, image_file: InMemoryUploadedFile, storage_path: str) -> Optional[str]:
        """
        Upload profile image to Supabase storage
        """
        try:
            # Process the image
            processed_bytes = self.process_image(image_file)
            
            # Get file extension
            file_ext = image_file.name.split('.')[-1].lower() if '.' in image_file.name else 'jpg'
            
            # Create unique filename
            file_name = f"{datetime.now().timestamp() * 1000:.0f}.{file_ext}"
            file_path = f"{storage_path}/{file_name}"
            
            bucket_name = 'profile-images'
            
            # Upload to Supabase
            supabase = get_supabase_client()
            supabase.storage.from_(bucket_name).upload(file_path, processed_bytes)
            
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            return "There was an error uploading the image. Please try again."

    def upload_artefact_image(self, image_file: InMemoryUploadedFile, storage_path: str) -> Optional[str]:
        """
        Upload artefact image to Supabase storage
        """
        try:
            # Process the image
            processed_bytes = self.process_image(image_file)
            
            # Get file extension
            file_ext = image_file.name.split('.')[-1].lower() if '.' in image_file.name else 'jpg'
            
            # Create unique filename
            file_name = f"{datetime.now().timestamp() * 1000:.0f}.{file_ext}"
            file_path = f"{storage_path}/{file_name}"
            
            bucket_name = 'artefact-images'
            
            # Upload to Supabase
            supabase = get_supabase_client()
            supabase.storage.from_(bucket_name).upload(file_path, processed_bytes)
            
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            return None

    def upload_product_image(self, image_file: InMemoryUploadedFile, storage_path: str) -> Optional[str]:
        """
        Upload product image to Supabase storage
        """
        try:
            # Process the image
            processed_bytes = self.process_image(image_file)
            
            # Get file extension
            file_ext = image_file.name.split('.')[-1].lower() if '.' in image_file.name else 'jpg'
            
            # Create unique filename
            file_name = f"{datetime.now().timestamp() * 1000:.0f}.{file_ext}"
            file_path = f"{storage_path}/{file_name}"
            
            bucket_name = 'product-images'
            
            # Upload to Supabase
            supabase = get_supabase_client()
            supabase.storage.from_(bucket_name).upload(file_path, processed_bytes)
            
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            return None
