"""Rebuild release ZIPs using original ZIP records and verified upstream binaries."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlsplit
import zipfile
import zlib


def verify_file(path, expected):
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise ValueError(f"SHA256 mismatch for {path.name}")


def get_sources(sources, directory):
    paths = {}
    for number, (key, source) in enumerate(sources.items()):
        url = source["url"]
        if urlsplit(url).scheme != "https":
            raise ValueError("Expected HTTPS URL")
        path = directory / str(number)
        print(f"Downloading {key}", flush=True)
        subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                        "--proto", "=https", "--proto-redir", "=https", "--retry", "3",
                        "--connect-timeout", "30", "--max-time", "1200",
                        "--output", str(path), url], check=True)
        if source.get("sha256"):
            verify_file(path, source["sha256"])
        paths[key] = path
    return paths


def compress_member(stream, output, entry):
    compressor = zlib.compressobj(3, zlib.DEFLATED, -15)
    digest = hashlib.sha256()
    size = 0
    while block := stream.read(1024 * 1024):
        digest.update(block)
        size += len(block)
        output.write(compressor.compress(block))
    output.write(compressor.flush())
    if size != entry["size"] or digest.hexdigest() != entry["sha256"]:
        raise ValueError("Upstream member mismatch for " + entry["name"])


def build_archives(recipe, sources, directory, local_engine=None):
    directory.mkdir(exist_ok=True, parents=True)
    for archive in recipe["archives"]:
        target = directory / archive["name"]
        temporary = target.with_suffix(".partial")
        with temporary.open("wb") as output:
            for entry in archive["entries"]:
                output.write(base64.b64decode(entry["header"], validate=True))
                if "data" in entry:
                    output.write(base64.b64decode(entry["data"], validate=True))
                elif local_engine:
                    path = local_engine / entry["name"].removeprefix("subtitle-engine/")
                    with path.open("rb") as stream:
                        compress_member(stream, output, entry)
                elif entry.get("member"):
                    with zipfile.ZipFile(sources[entry["source"]]) as src, src.open(entry["member"]) as stream:
                        compress_member(stream, output, entry)
                else:
                    with sources[entry["source"]].open("rb") as stream:
                        compress_member(stream, output, entry)
            output.write(base64.b64decode(archive["end"], validate=True))
        if temporary.stat().st_size != archive["size"]:
            raise ValueError("Reconstructed ZIP size mismatch for " + target.name)
        verify_file(temporary, archive["sha256"])
        temporary.replace(target)
        print(f"Verified {target.name}  {archive['sha256']}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--local-engine", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reconstructed"))
    args = parser.parse_args()
    opener = gzip.open if args.recipe.suffix == ".gz" else open
    with opener(args.recipe, "rt", encoding="utf8") as stream:
        recipe = json.load(stream)
    with tempfile.TemporaryDirectory() as directory:
        sources = {} if args.local_engine else get_sources(recipe["sources"], Path(directory))
        build_archives(recipe, sources, args.output, args.local_engine)


if __name__ == "__main__":
    main()
