import os
import cv2
import shutil
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageClassification

# Load NSFW model once
processor = AutoProcessor.from_pretrained("Falconsai/nsfw_image_detection")
model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")

def extract_frames_with_time(video_path, output_folder="frames", frame_rate=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count, saved_count = 0, 0
    timestamps = []

    while True:
        success, frame = cap.read()
        if not success:
            break

        if fps > 0 and frame_count % int(fps / frame_rate) == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            timestamps.append(saved_count / frame_rate)
            saved_count += 1
        frame_count += 1

    cap.release()
    return timestamps

def classify_image(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    labels = model.config.id2label
    top_pred = torch.argmax(probs).item()
    return labels[top_pred], probs[top_pred].item()

def analyze_video(video_path):
    frame_dir = "frames"
    timestamps = extract_frames_with_time(video_path, frame_dir)
    results = []

    # ✅ Filter only valid .jpg files
    frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])

    for i, file in enumerate(frame_files):
        frame_path = os.path.join(frame_dir, file)
        label, conf = classify_image(frame_path)
        if label not in ["neutral", "normal"]:
            if i < len(timestamps):  # ✅ safeguard to prevent index error
                results.append({
                    "time": round(timestamps[i], 2),
                    "label": label,
                    "confidence": round(conf, 2)
                })

    # ✅ Cleanup the extracted frames after processing
    shutil.rmtree(frame_dir)

    return results
