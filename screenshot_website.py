from html.entities import html5
from playwright.sync_api import sync_playwright
import pathlib
import time
import subprocess
import pathlib

def webm_to_mp4(webm_path: pathlib.Path) -> pathlib.Path:
    mp4_path = webm_path.with_suffix(".mp4")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", str(webm_path),
        "-movflags", "faststart",
        "-pix_fmt", "yuv420p",
        str(mp4_path)
    ], check=True)

    return mp4_path


import pathlib
import time
from playwright.sync_api import sync_playwright


def html_file_to_scrolling_video(
    html_path: str,
    output_dir: str = "videos",
    width: int = 1200,
    height: int = 800,
    scroll_step: int = 5,
    scroll_delay: float = 0.01
) -> pathlib.Path:
    html_path = pathlib.Path(html_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(html_path)

    output_dir = pathlib.Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    file_url = html_path.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": width, "height": height},
            record_video_dir=str(output_dir),
            record_video_size={"width": width, "height": height}
        )

        page = context.new_page()
        page.goto(file_url, wait_until="load")

        page.add_style_tag("::-webkit-scrollbar { display: none; }")
        page.wait_for_timeout(500)

        max_scroll = page.evaluate(
            "() => document.documentElement.scrollHeight - window.innerHeight"
        )

        scroll_y = 0
        while scroll_y < max_scroll:
            page.evaluate(f"window.scrollTo(0, {scroll_y})")
            scroll_y += scroll_step
            time.sleep(scroll_delay)

        page.evaluate(f"window.scrollTo(0, {max_scroll})")
        page.wait_for_timeout(500)

        video = page.video
        page.close()      # finalizes recording
        context.close()
        browser.close()

        return pathlib.Path(video.path()).resolve()


def test_1():
    paths: list = [f"./leads/{l}/index.html" for l in range (1, 6)]
    for path in paths:
        html_file_to_scrolling_video(html_path=path, output_dir="./videos_beta_testing/6 - 400x900/", width=390, height=844, scroll_step=20, scroll_delay=0.03)
        html_file_to_scrolling_video(html_path=path, output_dir="./videos_beta_testing/6 - 1440x900/", width=1440, height=900, scroll_step=20, scroll_delay=0.03)


if __name__ == "__main__":
    test_1()