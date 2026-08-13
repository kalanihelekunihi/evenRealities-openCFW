# G2 app\gui\MessageNotify\msg_notif_timer.c zero-anchor attestation

- Retained path: `app\gui\MessageNotify\msg_notif_timer.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\msg_notif_timer.c`
- Disposition: **linked-unanchored; code extent previously claimed by sibling closure** (zero additional body bytes)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-msg-notif-timer-closure.tsv` (sha256 `1e9de1ce141495b4a72a4544a18650dcf357bb78c79109bc6c634dc9df7dd89e`)
- Audit: `tools/analyze_g2_msg_notif_timer.py`; test: `tests/test_analyze_g2_msg_notif_timer.py`

## Evidence

Six blocks, each carrying exactly one literal reference to this path ([0x5528B8, 0x552AB0) in six rows), exist in the image and were absorbed as unanchored rows into the sibling `g2-ui-msg-notif-list-function-map.tsv` closure. This attestation claims zero additional body bytes, pins the sibling manifest by sha256, re-verifies all six covering row extents against the official image, and pins the path string, pointer cell 0x552AE8, and all 6 literal references. The no-reference timer-utility blocks following 0x552AB0 in the same gap were also absorbed by sibling closures (ui-msg-notif-list, text-stream-service) and are not claimed here.

| item | value |
|---|---|
| path string run address | 0x006F4604 |
| pointer cells | 0x00552AE8 |
| literal references | 6 |
| covering manifest | `g2-ui-msg-notif-list-function-map.tsv` (sha256 `67d9541d516f3a31a38e0608874acc8c4d7c9402f0eac2b748b76cbc066b3b63`) |
| covering rows | [0x005528B8, 0x00552906) [0x00552906, 0x00552948) [0x00552948, 0x005529A2) [0x005529A2, 0x005529E4) [0x005529E4, 0x00552A4A) [0x00552A4A, 0x00552AB0) |
| covering body bytes | 504 |

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_msg_notif_timer -v
```
