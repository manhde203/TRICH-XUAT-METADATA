
import subprocess
import json
import os
import sys


# ==============================
# 1. TRÍCH XUẤT METADATA
# ==============================

def extract_metadata(video_path):
    command = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    except FileNotFoundError:
        print("❌ Không tìm thấy ffprobe. Kiểm tra lại PATH.")
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        print("❌ Lỗi ffprobe:")
        print(e.stderr)
        sys.exit(1)

# ==============================
# 2. TÓM TẮT VIDEO
# ==============================

def summarize_metadata(metadata):
    format_info = metadata.get("format", {})
    streams = metadata.get("streams", [])

    summary = {}

    summary["format_name"] = format_info.get("format_name")
    summary["duration"] = float(format_info.get("duration", 0))
    summary["bit_rate"] = int(format_info.get("bit_rate", 0))

    for stream in streams:
        if stream.get("codec_type") == "video":
            summary["codec"] = stream.get("codec_name")
            summary["width"] = stream.get("width")
            summary["height"] = stream.get("height")
            summary["fps"] = stream.get("avg_frame_rate")
            summary["profile"] = stream.get("profile")

    return summary


# ==============================
# 3. PHÁT HIỆN DẤU HIỆU NGHI VẤN
# ==============================

def detect_suspicious_signs(metadata):
    warnings = []

    format_info = metadata.get("format", {})
    streams = metadata.get("streams", [])

    # Kiểm tra encoder
    tags = format_info.get("tags", {})
    encoder = tags.get("encoder", "")

    if "Lavf" in encoder:
        warnings.append("⚠ Video có dấu hiệu re-encode bằng FFmpeg.")

    for stream in streams:
        if stream.get("codec_type") == "video":
            bitrate = int(stream.get("bit_rate", 0))
            width = stream.get("width", 0)
            height = stream.get("height", 0)

            if bitrate < 500000:
                warnings.append("⚠ Bitrate video thấp bất thường.")

            if width < 640:
                warnings.append("⚠ Độ phân giải thấp bất thường.")

    if not warnings:
        warnings.append("✅ Không phát hiện dấu hiệu bất thường rõ ràng.")

    return warnings


# ==============================
# 4. SO SÁNH 2 VIDEO
# ==============================

def compare_videos(meta1, meta2):
    summary1 = summarize_metadata(meta1)
    summary2 = summarize_metadata(meta2)

    differences = {}

    for key in summary1:
        if summary1.get(key) != summary2.get(key):
            differences[key] = {
                "video_1": summary1.get(key),
                "video_2": summary2.get(key)
            }

    return differences

def save_report(video_path, summary, warnings):
    os.makedirs("results", exist_ok=True)
    output_path = "results/all_reports.json"

    new_entry = {
        "video": video_path,
        "summary": summary,
        "analysis": warnings
    }

    # Nếu file đã tồn tại thì đọc dữ liệu cũ
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    # Thêm bản ghi mới
    data.append(new_entry)

    # Ghi lại toàn bộ
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n📁 Đã cập nhật báo cáo vào: {output_path}")
# ==============================
# 5. MAIN MENU
# ==============================

def main():
    print("====== VIDEO FORENSIC TOOL ======")
    print("1. Phân tích 1 video")
    print("2. So sánh 2 video")
    choice = input("Chọn chức năng (1/2): ")

    if choice == "1":
        video_path = input("Nhập đường dẫn video: ").strip('"')

        if not os.path.exists(video_path):
            print("❌ File không tồn tại!")
            return

        metadata = extract_metadata(video_path)
        summary = summarize_metadata(metadata)
        warnings = detect_suspicious_signs(metadata)

        print("\n===== TÓM TẮT =====")
        print(json.dumps(summary, indent=4))

        print("\n===== PHÂN TÍCH =====")
        for w in warnings:
            print(w)

        save_report(video_path, summary, warnings)

    elif choice == "2":
        video1 = input("Video 1: ").strip('"')
        video2 = input("Video 2: ").strip('"')

        if not os.path.exists(video1) or not os.path.exists(video2):
            print("❌ Một trong hai file không tồn tại!")
            return

        meta1 = extract_metadata(video1)
        meta2 = extract_metadata(video2)

        differences = compare_videos(meta1, meta2)

        print("\n===== KHÁC BIỆT =====")
        if differences:
            print(json.dumps(differences, indent=4))
        else:
            print("✅ Hai video có metadata giống nhau.")
        save_report(video1, video2, differences)
    else:
        print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()