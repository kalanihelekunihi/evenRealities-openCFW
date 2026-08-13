# G2 kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c zero-anchor recovery

- Retained path: `kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-freertos-plus-cli-filesystem-closure.tsv` (sha256 `3fee797ff3f27bb8cdf6ab826bbe820ca843eca0a1291aa2f5dedf44a2a797d3`)
- Function map: `tools/manifests/g2-freertos-plus-cli-filesystem-function-map.tsv` (sha256 `4687cfb65b7331807a36e84efd75d664b85f3c26f19ab3d66800e6dcc050d340`)
- Audit: `tools/analyze_g2_freertos_plus_cli_filesystem.py`; test: `tests/test_analyze_g2_freertos_plus_cli_filesystem.py`

## Identity evidence

- Path string at 0x006DE434; pointer cell(s) 0x0057F950; 6 literal reference(s), all inside the mapped blocks.
- 6 module log-tag strings loaded by the mapped blocks, including:
- `0x007049AC` `[prvCommand_filesystem]Block info: size=%lu, total=%lu, used=%ld`
- `0x00741B7C` `[prvCommand_filesystem]final_dst_path: %s`
- `0x0075837C` `[prvCommand_filesystem]param1: %s`
- `0x007583A0` `[prvCommand_filesystem]param2: %s`
- `0x007583C4` `[prvCommand_filesystem]src_path: %s`
- `0x007583E8` `[prvCommand_filesystem]dst_path: %s`

## Linked extents

Physical interval `[0x0057E898, 0x0057F550)` = 3256 bytes (3200 body + 56 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x57e898-0x57e920 | 136 | 0 | 56 | `72717b305e0cfb2b...` |
| 0x57e920-0x57ea0a | 234 | 0 | 97 | `f67ac2ff98c707fd...` |
| 0x57ea0a-0x57eaa8 | 158 | 0 | 61 | `6f38bad57a72a9b7...` |
| 0x57eaa8-0x57eb84 | 220 | 0 | 91 | `8f3eea08961aa119...` |
| 0x57eb94-0x57ec7c | 232 | 0 | 89 | `050584dd12627dee...` |
| 0x57ec7c-0x57ed26 | 170 | 0 | 65 | `48c6583ba57209d4...` |
| 0x57ed26-0x57ede2 | 188 | 0 | 72 | `bb4e1f8ee290ff8f...` |
| 0x57ede2-0x57ee02 | 32 | 0 | 12 | `49b3a9dd8fe038f3...` |
| 0x57ee0c-0x57f26a | 1118 | 5 | 421 | `2e62caeb232a6772...` |
| 0x57f274-0x57f3be | 330 | 0 | 129 | `b574bd91b5910989...` |
| 0x57f3cc-0x57f52a | 350 | 1 | 120 | `e914a5c82d985041...` |
| 0x57f530-0x57f550 | 32 | 0 | 16 | `83ddbe3ccd98fe6d...` |

## Ingress (whole-image scans)

- direct BL entry sites: 6; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 1
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

The object fills the corpus gap between the preceding CLI-core function ending at 0x57E825 and the next Ghidra-discovered function at 0x57F550. The head bytes [0x57E826, 0x57E898) are a version-info string table owned by the preceding unpathed CLI object (referenced from code at 0x57E6EA-0x57E7EC) and are excluded; the boundary is guard-pinned.

Identity rests on 6 literal references to the retained path across 4 blocks plus 6 `[prvCommand_filesystem]` log tags loaded by the same blocks. Literal pools hold the strings `.`, `..`, `/`, `%s`; block 0x57EE0C logs `param1`/`param2`/`src_path`/`dst_path` (a copy/move command), block 0x57E898 walks a directory skipping `.`/`..`, and block 0x57F3CC prints `Block info: size=%lu, total=%lu, used=%ld` (statfs-style). This is CLI filesystem command code.

Ingress is sparse by measurement: only entry 0x57EAA8 has direct BL sites (4 intra-gap, 2 from the following CLI-core region at 0x57F81C/0x57F836) and entry 0x57F530 is registered through data-table cell 0x57FFB4. The other 10 entries have zero static ingress across BL, B.W, 16-bit B, stored-word, and movw/movt materialization scans of the whole image; registration is presumed dynamic (a runtime-built command table). This is recorded as a scanned fact, not resolved.

The path pointer cell 0x57F950 lies in the following object's literal region; IAR pooled the constant across the object boundary. The cell and all 6 references are pinned regardless.

Provenance: the retained path places the file under a vendored `kernel\FreeRTOS-Plus-CLI\prvCommand` directory. The pinned `third_party/freertos-plus-cli` mirror (FreeRTOS.git commit 43defa566cc440251dbd6b48d1fcca27f88cfcdd) contains only `FreeRTOS_CLI.c`/`FreeRTOS_CLI.h`; no `prvCommand_filesystem.c` exists in the pinned tree. This object is therefore first-party, demo-style CLI code in a vendor-named directory; no upstream commit is claimed for it. Whether any upstream FreeRTOS-Plus-CLI core code is linked is answered separately by the anchored closures around `FreeRTOS_CLI.c`; this audit only attests the prvCommand_filesystem.c seam.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_freertos_plus_cli_filesystem -v
```
