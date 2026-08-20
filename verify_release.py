"""Verify the frozen public-release payload using only Python's stdlib."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    root = Path(__file__).resolve().parent
    checksum_file = root / "SHA256SUMS.txt"
    failures: list[str] = []
    checked = 0
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        target = root / Path(relative)
        if not target.is_file():
            failures.append(f"MISSING {relative}")
            continue
        actual = sha256(target)
        checked += 1
        if actual != expected:
            failures.append(f"HASH {relative}")
    if failures:
        raise SystemExit("Release verification failed:\n" + "\n".join(failures))
    print(f"PASS: {checked} files match SHA256SUMS.txt")


if __name__ == "__main__":
    main()
