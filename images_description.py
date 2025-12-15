from transformers import LlavaProcessor, LlavaForConditionalGeneration
from PIL import Image
import torch
from log import log

# Load model once
model_id = "llava-hf/bakLlava-v1-hf"
processor = LlavaProcessor.from_pretrained(model_id)
model = LlavaForConditionalGeneration.from_pretrained(model_id)
model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

@torch.no_grad()
def get_description(img_path: str) -> str:
    """
    Returns a short description of the image.
    """
    try:
        image = Image.open(img_path).convert("RGB")
    except Exception as e:
        log(f"Error loading image: {e}")
        return f"Error loading image: {e}"

    log("Generating caption...")
    prompt = "<image>\nDescribe this image in detail:"
    
    # Correct usage: pass the image as 'images='
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)
    
    output = model.generate(**inputs, max_new_tokens=80)
    caption = processor.batch_decode(output, skip_special_tokens=True)[0]
    
    log("Done generating caption!")
    return caption

if __name__ == "__main__":
    log("TESTING SCRIPT")
    example_image = "./leads/1/images/1.jpg"
    print(get_description(example_image))