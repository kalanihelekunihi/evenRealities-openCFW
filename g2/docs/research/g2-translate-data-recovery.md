# G2 app\gui\translate\translate_data.c zero-anchor attestation

- Retained path: `app\gui\translate\translate_data.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_data.c`
- Disposition: **linked-unanchored; code extent previously claimed by sibling closure** (zero additional body bytes)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-translate-data-closure.tsv` (sha256 `124f3b35de031eedf3634b7993b61dc071a89faf7e061217f6361e6bdaa0db0e`)
- Audit: `tools/analyze_g2_translate_data.py`; test: `tests/test_analyze_g2_translate_data.py`

## Evidence

The sole block carrying this path's 5 literal references, [0x59E6D0, 0x59E9E2), exists in the image and was absorbed as an unanchored row into the sibling `g2-translate-ui-function-map.tsv` closure (row sha256 c3ce8a7d4a0c00a26675322ceb5494b3d4f4becc210bff48812d1fe7af1eafeb). This attestation claims zero additional body bytes, pins the sibling manifest by sha256, re-verifies the covering row bytes against the official image, and pins the path string, pointer cell 0x59EA20 (pooled outside the covered extent), and all 5 literal references.

| item | value |
|---|---|
| path string run address | 0x006FE594 |
| pointer cells | 0x0059EA20 |
| literal references | 5 |
| covering manifest | `g2-translate-ui-function-map.tsv` (sha256 `4e027aa0a336ca9823ed1a0d0d4c9b95ac012fcb8b2a976ef9bd326437387a20`) |
| covering rows | [0x0059E6D0, 0x0059E9E2) |
| covering body bytes | 786 |

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_translate_data -v
```
