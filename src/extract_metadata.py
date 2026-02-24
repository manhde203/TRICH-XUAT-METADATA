import json
import subprocess
from tkinter import Tk, filedialog


def main() -> None:
    # 1. Chọn file video
    root = Tk()
    root.withdraw()  # Ẩn cửa sổ chính

    video_path = filedialog.askopenfilename(
        title="Chọn video",
        filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")],
    )
    root.destroy()

    if not video_path:
        print("Bạn chưa chọn file.")
        return

    # 2. Gọi ffprobe để lấy metadata
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print("Không tìm thấy ffprobe. Hãy cài FFmpeg và thêm vào PATH.")
        return

    if result.returncode != 0:
        print("ffprobe chạy thất bại:")
        print(result.stderr.strip() or "Không có thông báo lỗi.")
        return

    # 3. Chuyển kết quả sang dạng JSON
    try:
        metadata = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Không thể parse JSON từ ffprobe.")
        return

    # 4. In toàn bộ metadata ra màn hình
    print("\n===== METADATA VIDEO =====")
    print(json.dumps(metadata, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
