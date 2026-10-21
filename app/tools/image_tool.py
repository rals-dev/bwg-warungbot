import uuid
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-0b38cd6a0a3b"
LOCATION = "global"
BUCKET_NAME = "warungbot-media-qwiklabs-gcp-03-0b38cd6a0a3b"

def generate_poster(item_name: str, prompt_details: str = "", tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Generate a promotional marketing poster for a menu item or product using Gemini image generation, save as an artifact, and upload to Cloud Storage.
    
    Args:
        item_name: The name of the product or menu item (e.g., 'Es Kopi Susu Gula Aren', 'Croissant', 'Matcha Latte').
        prompt_details: Optional specific design, aesthetic, or promotional themes (e.g., 'vintage rustic cafe vibes', 'rainy day promo discount', 'modern minimalist').
        tool_context: Injected ADK ToolContext for artifact persistence.
        
    Returns:
        A dictionary containing the status, public Cloud Storage URL of the image, and artifact details.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    prompt = f"Professional promotional poster for an Indonesian coffee shop featuring '{item_name}', warm atmospheric cafe lighting, appetizing presentation, high resolution commercial photography."
    if prompt_details:
        prompt += f" Additional style and theme requirements: {prompt_details}."
        
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt
        )
        
        image_bytes = None
        mime_type = "image/jpeg"
        
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type or "image/jpeg"
                            break
                            
        if not image_bytes:
            return {"status": "error", "message": "Failed to generate image bytes from model."}
            
        clean_name = item_name.lower().replace(" ", "_")
        unique_suffix = uuid.uuid4().hex[:8]
        artifact_filename = f"poster_{clean_name}_{unique_suffix}.jpg"
        gcs_object_name = f"posters/{artifact_filename}"
        
        # 1. Save to ADK Artifacts via tool_context
        if tool_context:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
            
        # 2. Upload image bytes directly to Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_object_name}"
        
        return {
            "status": "success",
            "item_name": item_name,
            "artifact_filename": artifact_filename,
            "public_url": public_url,
            "message": f"Poster for '{item_name}' generated successfully and uploaded to Cloud Storage."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Image generation or upload failed: {str(e)}"
        }
