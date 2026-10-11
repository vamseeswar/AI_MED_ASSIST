import os
import shutil
from PIL import Image, ImageSequence
import cv2
import numpy as np

src_webp = r"C:\Users\vamseeswara reddy\.gemini\antigravity-ide\brain\65cd4679-009a-443c-871a-d2eba0434506\medassist_web_verification_1791707630788.webp"
dst_dir = r"c:\AI_MED_ASSIST"
pub_dir = r"c:\AI_MED_ASSIST\frontend\public"
desktop_dir = r"C:\Users\vamseeswara reddy\OneDrive\Desktop"

print("Source WebP exists:", os.path.exists(src_webp))

# 1. Copy WebP
for target_dir in [dst_dir, pub_dir, desktop_dir]:
    try:
        shutil.copy2(src_webp, os.path.join(target_dir, "medassist_demo.webp"))
        print(f"[OK] Copied WebP to {target_dir}")
    except Exception as e:
        print(f"[FAIL] Failed to copy WebP to {target_dir}: {e}")

# 2. Extract frames and convert to MP4
try:
    im = Image.open(src_webp)
    frames = []
    print(f"Reading {im.n_frames} frames from WebP...")
    
    for frame in ImageSequence.Iterator(im):
        rgb_frame = frame.convert("RGB")
        np_frame = np.array(rgb_frame)
        bgr_frame = cv2.cvtColor(np_frame, cv2.COLOR_RGB2BGR)
        frames.append(bgr_frame)

    if frames:
        height, width, _ = frames[0].shape
        # Total 343 frames over ~30 seconds => ~11-12 fps
        fps = 11.5
        print(f"Total frames: {len(frames)}, Resolution: {width}x{height}, Target FPS: {fps}")

        mp4_temp = os.path.join(dst_dir, "medassist_demo.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(mp4_temp, fourcc, fps, (width, height))
        for f in frames:
            out.write(f)
        out.release()
        print(f"[OK] Generated medassist_demo.mp4 ({os.path.getsize(mp4_temp)} bytes)")

        # Copy MP4 to public and desktop
        shutil.copy2(mp4_temp, os.path.join(pub_dir, "medassist_demo.mp4"))
        shutil.copy2(mp4_temp, os.path.join(desktop_dir, "medassist_demo.mp4"))
        print("[OK] Distributed MP4 to public and Desktop.")

    # 3. Save as optimized animated GIF (sampled every 2nd frame for smooth compact GIF)
    try:
        gif_frames = []
        im = Image.open(src_webp)
        step = 2  # sample for lightweight web display
        for idx, frame in enumerate(ImageSequence.Iterator(im)):
            if idx % step == 0:
                # Resize slightly for crisp, lightweight GIF
                resized = frame.copy()
                resized.thumbnail((960, 540), Image.Resampling.LANCZOS)
                gif_frames.append(resized.convert("P", palette=Image.Palette.ADAPTIVE))

        if gif_frames:
            gif_dst = os.path.join(dst_dir, "medassist_demo.gif")
            gif_frames[0].save(
                gif_dst,
                save_all=True,
                append_images=gif_frames[1:],
                duration=int((1000 / fps) * step),
                loop=0,
                optimize=True
            )
            print(f"[OK] Generated medassist_demo.gif ({os.path.getsize(gif_dst)} bytes)")
            shutil.copy2(gif_dst, os.path.join(pub_dir, "medassist_demo.gif"))
            shutil.copy2(gif_dst, os.path.join(desktop_dir, "medassist_demo.gif"))
            print("[OK] Distributed GIF to public and Desktop.")
    except Exception as e:
        print(f"[NOTE] GIF generation: {e}")

except Exception as e:
    print(f"[ERROR] Video conversion failed: {e}")
