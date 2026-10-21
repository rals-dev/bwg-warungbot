import base64
import uuid
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-0b38cd6a0a3b"
LOCATION = "global"
BUCKET_NAME = "warungbot-media-qwiklabs-gcp-03-0b38cd6a0a3b"

def generate_video(
    item_name: str,
    prompt_details: str = "",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """Generate a short promotional video clip for a menu item or product using Gemini Omni, save as an artifact, and upload to Cloud Storage.
    
    Args:
        item_name: The name of the coffee or pastry item (e.g., 'Es Kopi Susu Gula Aren', 'Croissant', 'Avocado Coffee').
        prompt_details: Optional specific motion, aesthetic, or scene details (e.g., 'cinematic slow motion of pouring milk and espresso into ice with rising caramel swirls', 'steaming hot coffee with latte art').
        tool_context: Injected ADK ToolContext for artifact persistence.
        
    Returns:
        A dictionary containing the status, public Cloud Storage URL of the video, and artifact details.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    prompt = f"Cinematic high quality short video of '{item_name}', delicious cafe beverage presentation, warm coffee shop atmosphere, smooth motion."
    if prompt_details:
        prompt += f" {prompt_details}"
        
    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )
        
        output_video = getattr(interaction, "output_video", None)
        if not output_video or not getattr(output_video, "data", None):
            return {"status": "error", "message": "No video data returned from gemini-omni-flash-preview."}
            
        raw_data = output_video.data
        if isinstance(raw_data, bytes):
            video_bytes = raw_data
        elif isinstance(raw_data, str):
            video_bytes = base64.b64decode(raw_data)
        else:
            return {"status": "error", "message": f"Unexpected video data format: {type(raw_data)}"}
            
        mime_type = getattr(output_video, "mime_type", None) or "video/mp4"
        
        clean_name = item_name.lower().replace(" ", "_")
        unique_suffix = uuid.uuid4().hex[:8]
        artifact_filename = f"video_{clean_name}_{unique_suffix}.mp4"
        gcs_object_name = f"videos/{artifact_filename}"
        
        # 1. Save to ADK Artifacts via tool_context
        if tool_context:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
            
        # 2. Upload video bytes directly to Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)
        
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_object_name}"
        
        return {
            "status": "success",
            "item_name": item_name,
            "artifact_filename": artifact_filename,
            "public_url": public_url,
            "message": f"Video for '{item_name}' generated successfully and uploaded to Cloud Storage."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Video generation or upload failed: {str(e)}"
        }
