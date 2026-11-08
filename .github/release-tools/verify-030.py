import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

REPO = 'ydqbz/qinglu-releases'
TAG = 'v0.3.0'
TITLE = '轻录 0.3.0 · Windows 工作台与字幕工具'
EXPECTED = json.loads(r'''[{"name":"Qinglu-0.2.3-macOS-arm64.dmg","size":204406300,"sha256":"81b8b6aa3fe651d18725917df5e596386e59f49c9a956639c301d77b677076fe"},{"name":"Qinglu-0.2.3-macOS-arm64.zip","size":204137431,"sha256":"0931083e7b2562a56f0d85a2a53bd8287b34cc75f85e4c2f8c62dec31b00de52"},{"name":"Qinglu-0.2.3-macOS-x64.dmg","size":223367029,"sha256":"3666907a564ce0dc163ced3c358f9e5855b9294119eb5875e5974c48a0019eb2"},{"name":"Qinglu-0.2.3-macOS-x64.zip","size":223184956,"sha256":"07623be29b988af489e7ed1f67e53889f42d04f778dfb6513263d356b30b7766"},{"name":"Qinglu-0.3.0-AI-Windows-part1.zip","size":752372775,"sha256":"999110ff2681404cfbdda79987d33db882e2d2af4900352ba38374b41295f64a"},{"name":"Qinglu-0.3.0-AI-Windows-part2.zip","size":1176091685,"sha256":"65771cdd8d94d0623bbde403869faba70093fd20488d71536596b884bc6c3fc3"},{"name":"Qinglu-0.3.0-AI-Windows-part3.zip","size":943253277,"sha256":"47e13f3314ee6d5e6542295d95bfa98830059f992c769ae1562baa2de16f5618"},{"name":"Qinglu-0.3.0-AI-Windows-part4.zip","size":169977639,"sha256":"8a00352a5864339af2a236716031132a3ff57462bf867f903c5ac68850b67cb9"},{"name":"Qinglu-0.3.0-Guide.html","size":2585,"sha256":"50fba7df71d8c473ebabbe57433658abab1508f829fdf02c8c14f20d40550cf3"},{"name":"Qinglu-0.3.0-Portable-x64.exe","size":189531516,"sha256":"47d23ff7cb431bd64a837230a7f4a9659ff6690977c17f86b2c6d03cf0fa1afa"},{"name":"Qinglu-0.3.0-Release-Notes.md","size":2040,"sha256":"c2ec73457e74db65932a781f22c3085d3a6f1c2c48adc19cc9b76dc786dc66f7"},{"name":"Qinglu-0.3.0-Setup-x64.exe","size":189710781,"sha256":"c4fa490a37867f09941477d5c9bf1e4cd01b1f3c29ad5b98523c3113c05acf09"},{"name":"Qinglu-0.3.0-Setup-x64.exe.blockmap","size":198818,"sha256":"b159b3457e3c39d673941bca1f626f1599feca176241d04309ac2c6b646bc924"},{"name":"Qinglu-0.3.0-ThirdParty-Notices.zip","size":86985,"sha256":"aa0335735b31e6f476c18e963c30766f06ffa2dde2d4517f52dca2b7f5cfd1f2"},{"name":"latest-mac.yml","size":853,"sha256":"0f01b0342986df2f7db1d8be33212141db2e81a7b4c749a673e4830982f106c1"},{"name":"latest.yml","size":349,"sha256":"2d07333d84045ddc375bdfaaf1dedce57d8acd4ed1d7c2bf8284c6e1d87d44e8"},{"name":"SHA256SUMS.txt","size":1513,"sha256":"42b522139c29e47258020c9556c84e44a8d0c342f216036ed5dc2f39ba8e6dd8"}]''')
TRANSFER = json.loads(r'''{"schemaVersion":1,"version":"0.3.0","transportOnly":true,"chunkSize":67108864,"reconstruction":"Concatenate chunks in manifest order; verify every chunk and final ZIP size and SHA256 before upload.","archives":[{"name":"Qinglu-0.3.0-AI-Windows-part1.zip","size":752372775,"sha256":"999110ff2681404cfbdda79987d33db882e2d2af4900352ba38374b41295f64a","part":1,"chunks":[{"name":"Qinglu-0.3.0-transfer-part1-001.bin","index":1,"offset":0,"size":67108864,"sha256":"b9f20f967d715b8b9fdb52e12a7241c4bab774ac378796ef260eb9aa3983c65c"},{"name":"Qinglu-0.3.0-transfer-part1-002.bin","index":2,"offset":67108864,"size":67108864,"sha256":"4aa303472ec2c012352b613ee4d3ba977018d34a88fded3ad558916e3e0bc179"},{"name":"Qinglu-0.3.0-transfer-part1-003.bin","index":3,"offset":134217728,"size":67108864,"sha256":"128118d7420a41b67593862ab2585902c3f01c9473e56ec714d2134583dc9fd9"},{"name":"Qinglu-0.3.0-transfer-part1-004.bin","index":4,"offset":201326592,"size":67108864,"sha256":"7e72db9c7964891bfa6bd40514290a222615aef03e27b5b5365cb3c016af4adb"},{"name":"Qinglu-0.3.0-transfer-part1-005.bin","index":5,"offset":268435456,"size":67108864,"sha256":"6c176ce910242967b2ed57b8d96c6186833df542ba4df99ab82e4a01a56d1c5b"},{"name":"Qinglu-0.3.0-transfer-part1-006.bin","index":6,"offset":335544320,"size":67108864,"sha256":"cf593f301b0cceb5b997a3129ddb93d162b0108de31aa22d6bf62883f8bd5d26"},{"name":"Qinglu-0.3.0-transfer-part1-007.bin","index":7,"offset":402653184,"size":67108864,"sha256":"499195747204cf1338cb9e5bd570754dae620c85281c5ca1c13d29a2060bcf8f"},{"name":"Qinglu-0.3.0-transfer-part1-008.bin","index":8,"offset":469762048,"size":67108864,"sha256":"1b90bff7d329f97a0c833ae873d722f242f22ae0e9776b18e4b374790e4b6c13"},{"name":"Qinglu-0.3.0-transfer-part1-009.bin","index":9,"offset":536870912,"size":67108864,"sha256":"a788406b6b4ec46287843fdd5e0a1e852990c0bd122926726229ef253294015d"},{"name":"Qinglu-0.3.0-transfer-part1-010.bin","index":10,"offset":603979776,"size":67108864,"sha256":"bab5a89906dfd86c9e7ffb9bfa397374d00a442ecca425a344663c6633d75335"},{"name":"Qinglu-0.3.0-transfer-part1-011.bin","index":11,"offset":671088640,"size":67108864,"sha256":"8e3fd866b380dfd3926cd2a0d8ddd79359636afd32068c9d4110cc488ec51091"},{"name":"Qinglu-0.3.0-transfer-part1-012.bin","index":12,"offset":738197504,"size":14175271,"sha256":"ed6482ea6af69be8b96e928a4cf407c90f4a7feb8f3105c0ced6e22f917e5973"}]},{"name":"Qinglu-0.3.0-AI-Windows-part2.zip","size":1176091685,"sha256":"65771cdd8d94d0623bbde403869faba70093fd20488d71536596b884bc6c3fc3","part":2,"chunks":[{"name":"Qinglu-0.3.0-transfer-part2-001.bin","index":1,"offset":0,"size":67108864,"sha256":"dcd6d0850a2b82cb638b4570d943b8503a40a59792ee54abb340b0a0f4755aa6"},{"name":"Qinglu-0.3.0-transfer-part2-002.bin","index":2,"offset":67108864,"size":67108864,"sha256":"9f8fe8668f99a86957a47a12c0ab1f99f3dffda6301fe7b9aa8581de022909b7"},{"name":"Qinglu-0.3.0-transfer-part2-003.bin","index":3,"offset":134217728,"size":67108864,"sha256":"25f2564320f960a472aee3268d7043a192de8430a7c2e9dcaa86c1fa0aeea3bb"},{"name":"Qinglu-0.3.0-transfer-part2-004.bin","index":4,"offset":201326592,"size":67108864,"sha256":"351722690ae31f665b1b8a49fbfc727bf2e1506cd4a212ae96530047280ff1ee"},{"name":"Qinglu-0.3.0-transfer-part2-005.bin","index":5,"offset":268435456,"size":67108864,"sha256":"0737f0bd4a5ba8227af49fb376521aa3322d21ce671276a98b2c7736b7b256d6"},{"name":"Qinglu-0.3.0-transfer-part2-006.bin","index":6,"offset":335544320,"size":67108864,"sha256":"6803959c8538da8fd2347e61def6f4eb565d9133eb75b0e58868d87cbfa440ea"},{"name":"Qinglu-0.3.0-transfer-part2-007.bin","index":7,"offset":402653184,"size":67108864,"sha256":"38e826c326e23631a07fc209925768321a49f09db3b9ce8a9ccc2edcf9273bf4"},{"name":"Qinglu-0.3.0-transfer-part2-008.bin","index":8,"offset":469762048,"size":67108864,"sha256":"642946be4cc56d1bc92ea40e6124cbb54a44ffa2f5d1b5a4af6b132516124ed3"},{"name":"Qinglu-0.3.0-transfer-part2-009.bin","index":9,"offset":536870912,"size":67108864,"sha256":"4072ca2b1f28a1124f87b5763858005588c8c49bc762a18de580c27cdf88db68"},{"name":"Qinglu-0.3.0-transfer-part2-010.bin","index":10,"offset":603979776,"size":67108864,"sha256":"d1119e7264f8853ba3eb7310474c42df8acaffeeea082cf4e061eef5767c2574"},{"name":"Qinglu-0.3.0-transfer-part2-011.bin","index":11,"offset":671088640,"size":67108864,"sha256":"b0a32be9f5cd50eff6af7ea3afefe286034f1b66bf9565cf06348d1ce53d706f"},{"name":"Qinglu-0.3.0-transfer-part2-012.bin","index":12,"offset":738197504,"size":67108864,"sha256":"8c12037bf6c4e5d66af56855741e90d85627bb7a9f9075cef5f5b8d507e301f2"},{"name":"Qinglu-0.3.0-transfer-part2-013.bin","index":13,"offset":805306368,"size":67108864,"sha256":"81a7c5d9c5243c56965a0a11d62c7f07ba4891fbd9c2df5f31044d6e6335c344"},{"name":"Qinglu-0.3.0-transfer-part2-014.bin","index":14,"offset":872415232,"size":67108864,"sha256":"ad56fcb3d6dd5bd7962648c3335793d49aeaafb03a6234a0e420ae8ccae68cb6"},{"name":"Qinglu-0.3.0-transfer-part2-015.bin","index":15,"offset":939524096,"size":67108864,"sha256":"7285bf9e09247869e5b32ddc17ad129bff9756f85410131fc10afe48d34a00f4"},{"name":"Qinglu-0.3.0-transfer-part2-016.bin","index":16,"offset":1006632960,"size":67108864,"sha256":"24432e535a5d20b38305d6cc7ba7bddabd5f2d4b18a2ad0a3c0c21633b4aa7c5"},{"name":"Qinglu-0.3.0-transfer-part2-017.bin","index":17,"offset":1073741824,"size":67108864,"sha256":"b2af702dd44d2503d6056210b9583040efdac8b4e09cb8dd3b25561f29d8d19c"},{"name":"Qinglu-0.3.0-transfer-part2-018.bin","index":18,"offset":1140850688,"size":35240997,"sha256":"1fa93f4dc1ea09bac33d8a8b3a79afea0c139b514009e2a63d4e6bbb3a4c7c7e"}]},{"name":"Qinglu-0.3.0-AI-Windows-part3.zip","size":943253277,"sha256":"47e13f3314ee6d5e6542295d95bfa98830059f992c769ae1562baa2de16f5618","part":3,"chunks":[{"name":"Qinglu-0.3.0-transfer-part3-001.bin","index":1,"offset":0,"size":67108864,"sha256":"98f053773235cd85146dd3a3ca048b6555a23f749f69cb298fc35ca194457ef8"},{"name":"Qinglu-0.3.0-transfer-part3-002.bin","index":2,"offset":67108864,"size":67108864,"sha256":"9b84aec17cf51166a7439865f6bf2a255f2543f6f008d1957167304b82c03f54"},{"name":"Qinglu-0.3.0-transfer-part3-003.bin","index":3,"offset":134217728,"size":67108864,"sha256":"4c3927971fc33d044359dd660760b7daf7f5e6f36f28850ace1408db00eb7940"},{"name":"Qinglu-0.3.0-transfer-part3-004.bin","index":4,"offset":201326592,"size":67108864,"sha256":"e9287db51ecf5a2288b620b0685eca781d3828d6d2d663ccc6b810652b2035bf"},{"name":"Qinglu-0.3.0-transfer-part3-005.bin","index":5,"offset":268435456,"size":67108864,"sha256":"e717c23aa68eaa9c056cce0c907d2a42920e0ce8edb986b7e3ad12d42bf0de79"},{"name":"Qinglu-0.3.0-transfer-part3-006.bin","index":6,"offset":335544320,"size":67108864,"sha256":"af5a6523624ea1bf5121fe66694e51c9886d3ad3971a7ae0d031fbc14f5d4da9"},{"name":"Qinglu-0.3.0-transfer-part3-007.bin","index":7,"offset":402653184,"size":67108864,"sha256":"b9989d23e225f1a109f60309f3aaa9b567744377ba89a1a4ecd188ed6f415d3c"},{"name":"Qinglu-0.3.0-transfer-part3-008.bin","index":8,"offset":469762048,"size":67108864,"sha256":"fc421a4682df6df530940533990315c6b06da43e58709e2929634174fa3a21f1"},{"name":"Qinglu-0.3.0-transfer-part3-009.bin","index":9,"offset":536870912,"size":67108864,"sha256":"d254a41d938e614a417fba03aa0b9479c6543ac263fa44d2aa65641c4fe0b7dd"},{"name":"Qinglu-0.3.0-transfer-part3-010.bin","index":10,"offset":603979776,"size":67108864,"sha256":"c1c2339e436ef3d6965db632ba44484b42473923022f3fc71e7c788d1ff895b7"},{"name":"Qinglu-0.3.0-transfer-part3-011.bin","index":11,"offset":671088640,"size":67108864,"sha256":"255459c21a08f68787dcdc3603df44c25896d9ef4377d121415b9cf1beebbe9c"},{"name":"Qinglu-0.3.0-transfer-part3-012.bin","index":12,"offset":738197504,"size":67108864,"sha256":"3deb8c5060511abc8e6c32ddd9f31a103e0b032efc3478af36234e0846ba029d"},{"name":"Qinglu-0.3.0-transfer-part3-013.bin","index":13,"offset":805306368,"size":67108864,"sha256":"182b7ccb533fc76a7c266d4f440173aded9a222aeff58d02bd9cc2b844acf9f9"},{"name":"Qinglu-0.3.0-transfer-part3-014.bin","index":14,"offset":872415232,"size":67108864,"sha256":"b5c664a9d0b186e91aa3606baf14114c34bbd27e406a829b79192d9a3323680c"},{"name":"Qinglu-0.3.0-transfer-part3-015.bin","index":15,"offset":939524096,"size":3729181,"sha256":"aea504f103e7fe1199d0e1eb3ac3ea05267ac407d25ba36fb82c72840a1bd899"}]}]}''')
NOTES = json.loads(r'''"## 轻录 0.3.0 · Windows\n\n本次更新 Windows x64；Mac 继续使用 [0.2.3](https://github.com/ydqbz/qinglu-releases/releases/tag/v0.2.3)。\n\n### 更新内容\n- 工作区重新排版：左侧放功能大类，页内筛选任务；新建下载、导入视频移至右上角。\n- 统一深浅主题、字体、图标和按钮，页头按钮采用柔和紫色；新增 Ctrl+K 快捷操作。\n- 修复近期抖音、小红书分享链接解析问题；网站变化或网络限制仍可能影响解析。\n- 新增独立字幕轨无损移除，以及可框选区域、先预览后导出的 AI 画面字幕修复。\n- 安装版支持软件内检查、下载和重启更新，下载或字幕任务繁忙时等待任务结束。\n\n### 下载与安装\n- 日常使用：`Qinglu-0.3.0-Setup-x64.exe`。已有 0.2.3 安装版可检查更新，保留原有任务与设置。\n- 免安装：`Qinglu-0.3.0-Portable-x64.exe`。便携版手动替换 EXE，保留旁边的 data 和 downloads 文件夹。\n- 普通下载、独立字幕轨移除无需 AI 组件。\n- AI 画面修复：下载 **全部 4 个** `Qinglu-0.3.0-AI-Windows-part*.zip`，分别解压到 `%APPDATA%\\Qinglu`，合并成同一个 `subtitle-engine` 文件夹，然后重启轻录。四个文件是独立 ZIP，不是改名后拼接的分卷。合计下载约 3.04 GB，解压约 5.43 GB，另为视频输出留出空间。详见附件使用说明。\n\n### AI 功能范围\nAI 为实验功能，目前仅在 Windows＋NVIDIA CUDA 环境进行短片验证，建议至少 8 GB 显存。复杂运动、面部、手部、动态标题可能残留纹理或拖影，不能保证无痕效果；请先预览并保留原片。ProPainter 代码与模型遵守 S-Lab 非商业许可，许可随组件附带，商业用途需要另行授权。Mac 本轮不增加 AI 功能。\n\nWindows 包尚无发行者数字签名。请使用本仓库附件及 SHA256SUMS.txt 核对文件。latest.yml、blockmap 为更新组件；latest-mac.yml 保留 Mac 0.2.3 通道，普通用户不用手动下载这些清单。\n"''')
FINAL = {record['name']: record for record in EXPECTED}
CHUNKS = {chunk['name']: chunk for archive in TRANSFER['archives'] for chunk in archive['chunks']}
ALLOWED = set(FINAL) | set(CHUNKS)
SMALL = ('latest.yml', 'latest-mac.yml', 'SHA256SUMS.txt')
DEADLINE = None
RELEASE_ID = None


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def validate_recipe():
    require(len(EXPECTED) == len(FINAL) == 17, 'Expected exactly 17 final assets')
    require(TRANSFER['schemaVersion'] == 1 and TRANSFER['version'] == '0.3.0' and TRANSFER['transportOnly'] is True, 'Unexpected transfer recipe')
    require(len(TRANSFER['archives']) == 3 and len(CHUNKS) == 45, 'Unexpected transfer group or chunk count')
    seen = set()
    for part, archive in enumerate(TRANSFER['archives'], 1):
        require(archive['part'] == part and archive['name'] == f'Qinglu-0.3.0-AI-Windows-part{part}.zip', 'Unexpected archive order')
        expected = FINAL[archive['name']]
        require(archive['size'] == expected['size'] and archive['sha256'] == expected['sha256'], 'Archive recipe does not match final asset')
        offset = 0
        for index, chunk in enumerate(archive['chunks'], 1):
            require(chunk['name'] == f'Qinglu-0.3.0-transfer-part{part}-{index:03d}.bin', 'Unexpected chunk filename or order')
            require(chunk['name'] not in seen and chunk['index'] == index and chunk['offset'] == offset, 'Duplicate or discontinuous chunk')
            require(0 < chunk['size'] <= TRANSFER['chunkSize'] == 67108864, 'Unexpected chunk size')
            require(re.fullmatch('[a-f0-9]{64}', chunk['sha256']) is not None, 'Invalid chunk digest')
            seen.add(chunk['name'])
            offset += chunk['size']
        require(offset == archive['size'], 'Archive byte length mismatch')
    require(seen == set(CHUNKS) and not (set(FINAL) & set(CHUNKS)), 'Chunk set mismatch')


def run_gh(*args):
    remaining = DEADLINE - time.monotonic()
    require(remaining > 0, '100-minute assembly deadline exceeded; release remains unchanged')
    result = subprocess.run(['gh', *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=min(600, remaining), check=False)
    if result.returncode:
        # gh must never be run with debug logging or token-bearing arguments.
        raise RuntimeError('GitHub command failed: ' + result.stderr.decode('utf-8', 'replace')[:1200])
    return result.stdout


def api(path, method=None):
    args = ['api', '--hostname', 'github.com', path]
    if method:
        args += ['--method', method]
    data = run_gh(*args)
    return json.loads(data) if data else None


def find_existing_target():
    # The tag may not exist yet while the release is a draft, so use the authenticated release list.
    releases = api(f'repos/{REPO}/releases?per_page=100')
    require(isinstance(releases, list) and len(releases) < 100, 'Release listing needs explicit pagination review')
    matches = [release for release in releases if release.get('tag_name') == TAG]
    require(len(matches) == 1, 'Expected exactly one existing v0.3.0 release')
    return matches[0]


def verify_uploaded(asset, expected):
    require(asset.get('state') == 'uploaded', 'Asset is not uploaded: ' + expected['name'])
    require(asset.get('size') == expected['size'], 'Asset size mismatch: ' + expected['name'])
    require(asset.get('digest') == 'sha256:' + expected['sha256'], 'Asset digest mismatch: ' + expected['name'])
    require(asset.get('name') == expected['name'] and isinstance(asset.get('id'), int), 'Invalid asset identity')


def guard_release(release):
    require(release.get('id') == RELEASE_ID, 'Release identity changed')
    require(release.get('tag_name') == TAG and release.get('name') == TITLE, 'Unexpected release target')
    require(release.get('prerelease') is False, 'Release must not be a prerelease')
    require((release.get('body') or '').replace('\r\n', '\n').strip() == NOTES.replace('\r\n', '\n').strip(), 'Release notes changed; manual review required')
    assets = release.get('assets', [])
    require(len(assets) < 100, 'Unexpected number of assets')
    by_name = {asset['name']: asset for asset in assets}
    require(len(by_name) == len(assets), 'Duplicate asset names')
    require(set(by_name) <= ALLOWED, 'Unexpected attachments; refuse to publish or delete anything')
    for name, asset in by_name.items():
        if asset.get('state') == 'uploaded':
            verify_uploaded(asset, FINAL.get(name) or CHUNKS[name])
    return by_name


def snapshot(require_draft=False):
    release = api(f'repos/{REPO}/releases/{RELEASE_ID}')
    by_name = guard_release(release)
    if require_draft:
        require(release.get('draft') is True, 'Release was published concurrently; refuse further mutations')
    return release, by_name


def verify_file(path, record):
    require(path.is_file() and path.stat().st_size == record['size'], 'Downloaded file size mismatch: ' + record['name'])
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    require(digest == record['sha256'], 'Downloaded byte hash mismatch: ' + record['name'])


def download_verified(record, destination):
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / record['name']
    if not path.exists():
        run_gh('release', 'download', TAG, '--repo', REPO, '--pattern', record['name'], '--dir', str(destination))
    verify_file(path, record)
    return path


def delete_known_asset(name, previously_seen_id, expected, allow_failed=False):
    _, assets = snapshot(require_draft=True)
    asset = assets.get(name)
    if asset is None:
        return
    require(asset['id'] == previously_seen_id, 'Asset identity changed before deletion: ' + name)
    if allow_failed:
        require(name in FINAL and name.startswith('Qinglu-0.3.0-AI-Windows-part') and asset.get('state') != 'uploaded', 'Only a failed AI starter can be replaced')
    else:
        require(name in CHUNKS, 'Cleanup may only remove exact expected transport chunks')
        verify_uploaded(asset, expected)
    api(f'repos/{REPO}/releases/assets/{asset["id"]}', 'DELETE')


def clean_archive_chunks(archive):
    # Recheck the verified final ZIP before every cleanup batch, then exact chunk IDs before each delete.
    _, assets = snapshot(require_draft=True)
    verify_uploaded(assets[archive['name']], FINAL[archive['name']])
    for chunk in archive['chunks']:
        asset = assets.get(chunk['name'])
        if asset is not None:
            verify_uploaded(asset, chunk)
            delete_known_asset(chunk['name'], asset['id'], chunk)


def assemble_archive(archive):
    _, assets = snapshot(require_draft=True)
    final = assets.get(archive['name'])
    if final and final.get('state') == 'uploaded':
        verify_uploaded(final, FINAL[archive['name']])
        clean_archive_chunks(archive)
        return True
    if any(assets.get(chunk['name'], {}).get('state') != 'uploaded' for chunk in archive['chunks']):
        return False
    for chunk in archive['chunks']:
        verify_uploaded(assets[chunk['name']], chunk)
    folder = Path('transfer-files') / str(archive['part'])
    files = [download_verified(chunk, folder) for chunk in archive['chunks']]
    output = Path('reconstructed') / archive['name']
    output.parent.mkdir(exist_ok=True)
    with output.open('wb') as destination:
        for path in files:
            with path.open('rb') as source:
                while block := source.read(8 * 1024 * 1024):
                    destination.write(block)
    verify_file(output, FINAL[archive['name']])
    _, latest = snapshot(require_draft=True)
    slot = latest.get(archive['name'])
    if slot and slot.get('state') == 'uploaded':
        verify_uploaded(slot, FINAL[archive['name']])
    else:
        if slot:
            delete_known_asset(archive['name'], slot['id'], FINAL[archive['name']], allow_failed=True)
        # No --clobber: a concurrent upload must fail safely rather than replacing it.
        run_gh('release', 'upload', TAG, str(output), '--repo', REPO)
    _, latest = snapshot(require_draft=True)
    verify_uploaded(latest[archive['name']], FINAL[archive['name']])
    print('Verified reconstructed archive: ' + archive['name'], flush=True)
    clean_archive_chunks(archive)
    return True


def verify_final_set(release):
    assets = guard_release(release)
    require(set(assets) == set(FINAL), 'Final release must contain exactly the 17 approved assets')
    for name, expected in FINAL.items():
        verify_uploaded(assets[name], expected)
    return assets


def verify_small_files():
    folder = Path('verified-manifests')
    for name in SMALL:
        download_verified(FINAL[name], folder)
    windows = (folder / 'latest.yml').read_text(encoding='utf-8')
    mac = (folder / 'latest-mac.yml').read_text(encoding='utf-8')
    require(re.search(r'^version: 0\.3\.0\s*$', windows, re.M), 'Windows channel version changed')
    require(re.search(r'^version: 0\.2\.3\s*$', mac, re.M), 'Mac channel version changed')
    require(re.findall(r'^\s*- url: (\S+)\s*$', windows, re.M) == ['Qinglu-0.3.0-Setup-x64.exe'], 'Unexpected Windows updater target')
    require(set(re.findall(r'^\s*- url: (\S+)\s*$', mac, re.M)) == {name for name in FINAL if name.startswith('Qinglu-0.2.3-macOS-')}, 'Unexpected Mac updater targets')
    checks = {}
    for line in (folder / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([a-f0-9]{64})  (.+)', line)
        require(match is not None and match[2] not in checks, 'Malformed or duplicate checksum entry')
        checks[match[2]] = match[1]
    require(checks == {name: record['sha256'] for name, record in FINAL.items() if name != 'SHA256SUMS.txt'}, 'Checksum file does not match final attachments')


def record_success(release, already_published=False):
    latest = api(f'repos/{REPO}/releases/latest')
    require(latest.get('id') == RELEASE_ID and latest.get('tag_name') == TAG, 'Latest release did not resolve to v0.3.0')
    verify_final_set(latest)
    summary = ('## Qinglu 0.3.0 verified\n\n'
               'All 17 approved release assets match exact byte sizes and SHA256 digests. '
               'Windows update manifest: 0.3.0. Mac update manifest: unchanged 0.2.3.\n\n'
               f'[Published release](https://github.com/{REPO}/releases/tag/{TAG})\n')
    if already_published:
        summary += '\nThis run found an already-published matching release and made no mutations.\n'
    Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(summary, encoding='utf-8')
    print(summary, flush=True)


def main():
    global DEADLINE, RELEASE_ID
    validate_recipe()
    require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'Unexpected repository')
    DEADLINE = time.monotonic() + 100 * 60
    release = find_existing_target()
    RELEASE_ID = release.get('id')
    require(isinstance(RELEASE_ID, int), 'Expected an existing release; never create one here')
    guard_release(release)
    if release.get('draft') is False:
        verify_final_set(release)
        verify_small_files()
        record_success(release, already_published=True)
        return
    require(release.get('draft') is True, 'Unknown release status')
    completed = set()
    while time.monotonic() < DEADLINE:
        for archive in TRANSFER['archives']:
            if archive['name'] not in completed and assemble_archive(archive):
                completed.add(archive['name'])
        release, assets = snapshot(require_draft=True)
        if len(completed) == 3 and set(assets) == set(FINAL) and all(a.get('state') == 'uploaded' for a in assets.values()):
            verify_final_set(release)
            verify_small_files()
            # Fetch by tag again and by pinned ID immediately before the only publishing call.
            current = find_existing_target()
            require(current.get('id') == RELEASE_ID and current.get('draft') is True, 'Publication target changed')
            verify_final_set(current)
            snapshot(require_draft=True)
            run_gh('release', 'edit', TAG, '--repo', REPO, '--draft=false', '--latest')
            published, _ = snapshot()
            require(published.get('draft') is False, 'Publication did not complete')
            verify_final_set(published)
            record_success(published)
            return
        ready = sum(1 for a in assets.values() if a.get('state') == 'uploaded')
        print(f'Waiting for approved uploads: {ready} uploaded entries; {len(completed)}/3 reconstructed archives.', flush=True)
        time.sleep(min(30, max(0, DEADLINE - time.monotonic())))
    raise RuntimeError('Upload deadline reached. v0.3.0 was not published by this workflow; rerun after uploads complete.')


if __name__ == '__main__':
    main()
