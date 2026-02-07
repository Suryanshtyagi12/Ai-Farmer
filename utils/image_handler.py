import PIL.Image
import io

class ImageHandler:
    @staticmethod
    def process_image(uploaded_file):
        """
        Processes Streamlit uploaded file into a PIL Image.
        """
        if uploaded_file is not None:
            image = PIL.Image.open(uploaded_file)
            return image
        return None

    @staticmethod
    def image_to_bytes(image):
        """
        Converts PIL Image to bytes for LLM consumption if needed.
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
        return img_byte_arr.getvalue()

image_handler = ImageHandler()
