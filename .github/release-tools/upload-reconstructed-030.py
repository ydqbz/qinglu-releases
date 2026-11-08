import argparse
import datetime as dt
import http.client
import importlib.util
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode


spec = importlib.util.spec_from_file_location("verify", Path(__file__).with_name("verify-030.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

RELEASE_ID = 429695398
RELEASE_PATH = f"repos/{verify.REPO}/releases/{RELEASE_ID}"
ARCHIVES = [f"Qinglu-0.3.0-AI-Windows-part{n}.zip" for n in (1, 2, 3)]
TRANSFER_STARTER = "Qinglu-0.3.0-transfer-part1-001.bin"
STARTER_IDS = {ARCHIVES[0]: 705992884, ARCHIVES[1]: 705996183, ARCHIVES[2]: 705998105,
               TRANSFER_STARTER: 707952347}


def inventory():
    release, embedded = verify.snapshot()
    assets = verify.api(f"{RELEASE_PATH}/assets?per_page=100")
    verify.require(isinstance(assets, list) and len(assets) < 100, "Unexpected asset pagination")
    # The dedicated asset list may also expose unfinished uploads. Preserve both views.
    combined = dict(embedded)
    seen = set()
    for asset in assets:
        name = asset["name"]
        verify.require(name not in seen, "Duplicate asset: " + name)
        seen.add(name)
        if name in embedded:
            verify.require(embedded[name]["id"] == asset["id"], "Asset changed during inspection: " + name)
        combined[name] = asset
    release = dict(release, assets=list(combined.values()))
    verify.guard_release(release)
    verify.require(set(combined) <= set(verify.FINAL) | {TRANSFER_STARTER}, "Unapproved release attachment")
    if TRANSFER_STARTER in combined:
        verify.require(release["draft"] is True and stale_starter(combined[TRANSFER_STARTER]),
                       "Unexpected transport attachment")
    for name, record in verify.FINAL.items():
        asset = combined.get(name)
        if name in ARCHIVES and asset and asset.get("state") != "uploaded":
            verify.require(stale_starter(asset), "Unexpected unfinished archive: " + name)
        if name not in ARCHIVES or (asset and asset.get("state") == "uploaded"):
            verify.require(asset is not None, "Missing pre-existing asset: " + name)
            verify.verify_uploaded(asset, record)
    if release["draft"] is False:
        verify.verify_final_set(release)
    else:
        verify.require(release["draft"] is True, "Unknown release state")
    return release, combined


def stale_starter(asset):
    name = asset.get("name")
    if name not in STARTER_IDS or asset.get("id") != STARTER_IDS[name]:
        return False
    expected = verify.FINAL.get(name) or verify.CHUNKS[name]
    if asset.get("state") != "starter" or asset.get("size") != expected["size"] or asset.get("digest") is not None:
        return False
    updated = dt.datetime.fromisoformat(asset["updated_at"].replace("Z", "+00:00"))
    return (dt.datetime.now(dt.timezone.utc) - updated) >= dt.timedelta(hours=2)


def remove_starter(name):
    release, assets = inventory()
    asset = assets.get(name)
    if not asset:
        return
    verify.require(release["draft"] is True and stale_starter(asset), "Starter changed: " + name)
    if name == TRANSFER_STARTER:
        verify.require(ARCHIVES[0] in assets, "Expected verified part 1 before transport cleanup")
        verify.verify_uploaded(assets[ARCHIVES[0]], verify.FINAL[ARCHIVES[0]])
    path = f"repos/{verify.REPO}/releases/assets/{asset['id']}"
    current = verify.api(path)
    verify.require(current["name"] == name and current["id"] == asset["id"] and stale_starter(current),
                   "Starter changed before removal: " + name)
    verify.api(path, "DELETE")


def upload(name):
    release, assets = inventory()
    if name in assets and assets[name].get("state") == "uploaded":
        return
    verify.require(name in ARCHIVES and release["draft"], "Expected missing AI archive in draft")
    if name in assets:
        remove_starter(name)
    # Upload by pinned release ID. Never follow redirects with the write token.
    record = verify.FINAL[name]
    connection = http.client.HTTPSConnection("uploads.github.com", timeout=600)
    try:
        with (Path("reconstructed") / name).open("rb") as stream:
            connection.request("POST", f"/{RELEASE_PATH}/assets?{urlencode({'name': name})}", body=stream,
                               headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                                        "User-Agent": "Qinglu-release-publisher",
                                        "Content-Type": "application/zip", "Content-Length": str(record["size"])})
            response = connection.getresponse()
            content = response.read()
        verify.require(response.status == 201, f"Upload failed ({response.status}): {name}")
        verify.verify_uploaded(json.loads(content), record)
    finally:
        connection.close()
    print("Verified uploaded archive: " + name, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["inspect", "publish"])
    args = parser.parse_args()
    verify.require(os.environ.get("GITHUB_REPOSITORY") == "ydqbz/qinglu-releases", "Unexpected repository")
    verify.require(verify.TAG == "v0.3.0", "Unexpected tag")
    verify.RELEASE_ID = RELEASE_ID
    verify.DEADLINE = time.monotonic() + 60 * 60
    verify.validate_recipe()
    release, assets = inventory()
    missing = [name for name in ARCHIVES if assets.get(name, {}).get("state") != "uploaded"]
    if args.action == "inspect":
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            print("rebuild=" + str(bool(missing)).lower(), file=output)
        print("Archives to rebuild: " + (", ".join(missing) or "none"), flush=True)
        return

    # Validate every required local archive before making any remote changes.
    for name in missing:
        verify.verify_file(Path("reconstructed") / name, verify.FINAL[name])
    for name in missing:
        upload(name)
    remove_starter(TRANSFER_STARTER)
    release, _ = inventory()
    verify.verify_final_set(release)
    verify.verify_small_files()
    already_published = not release["draft"]
    if not already_published:
        release, _ = inventory()
        verify.verify_final_set(release)
        if release["draft"]:
            verify.run_gh("api", RELEASE_PATH, "--method", "PATCH", "-F", "draft=false", "-f", "make_latest=true")
        release, _ = inventory()
        verify.require(release["draft"] is False, "Publication still pending")
    verify.record_success(release, already_published=already_published)


if __name__ == "__main__":
    main()
