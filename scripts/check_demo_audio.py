"""Check that every demo audio URL resolves to a bundled MP3 file."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class AudioSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "audio":
            self.sources.append(dict(attrs).get("src", ""))


def main():
    root = Path(__file__).resolve().parents[1]
    parser = AudioSources()
    parser.feed((root / "index.html").read_text(encoding="utf-8"))
    errors = []
    if not parser.sources:
        errors.append("No audio players found in index.html")

    for source in parser.sources:
        url = urlsplit(source)
        path = (root / unquote(url.path)).resolve()
        if not source or url.scheme or url.netloc or root not in path.parents:
            errors.append(f"Audio must use a site-relative file: {source!r}")
            continue
        if path.suffix.lower() != ".mp3" or not path.is_file():
            errors.append(f"Missing MP3 file: {source}")
            continue
        with path.open("rb") as audio:
            header = audio.read(3)
        is_frame = len(header) == 3 and header[0] == 0xFF and header[1] & 0xE0 == 0xE0
        if header != b"ID3" and not is_frame:
            errors.append(f"Invalid MP3 header (or Git LFS pointer): {source}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Verified {len(parser.sources)} bundled demo audio files.")


if __name__ == "__main__":
    main()
