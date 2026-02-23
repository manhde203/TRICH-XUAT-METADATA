import subprocess
import json
from tkinter import Tk, filedialog

# 1. Chọn file video
root = Tk()
root.withdraw()  # Ẩn cửa sổ chính

video_path = filedialog.askopenfilename(
    title="Chọn video",
    filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")]
)

if not video_path:
    print("Bạn chưa chọn file.")
    exit()

# 2. Gọi ffprobe để lấy metadata
command = [
    "ffprobe",
    "-v", "error",
    "-print_format", "json",
    "-show_format",
    "-show_streams",
    video_path
]

result = subprocess.run(command, capture_output=True, text=True)

# 3. Chuyển kết quả sang dạng JSON
metadata = json.loads(result.stdout)

# 4. In toàn bộ metadata ra màn hình
print("\n===== METADATA VIDEO =====")
print(json.dumps(metadata, indent=4, ensure_ascii=False))