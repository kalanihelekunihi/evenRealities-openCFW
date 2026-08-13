# G2 app\gui\EvenAI\even_ai.c zero-anchor recovery

- Retained path: `app\gui\EvenAI\even_ai.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\even_ai.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-even-ai-closure.tsv` (sha256 `345d14c76ef409a1ef837c379e94de768b41d9b40503209b08bb0659954c0a6c`)
- Function map: `tools/manifests/g2-even-ai-function-map.tsv` (sha256 `af6335e43d2517a301f770e32c78c97380ee2885c1e0504408124124df2517cf`)
- Audit: `tools/analyze_g2_even_ai.py`; test: `tests/test_analyze_g2_even_ai.py`

## Identity evidence

- Path string at 0x0070B3A4; pointer cell(s) 0x004E2A4C 0x004E2DF4; 14 literal reference(s), all inside the mapped blocks.
- 14 module log-tag strings loaded by the mapped blocks, including:
- `0x006FA214` `[even_ai.page]recv evenai f_text_end = %d, text_len = %d, text = %.*s`
- `0x00714B48` `[even_ai.page]stop current streaming, avoid text confusion`
- `0x0071EA38` `[even_ai.page][even ai]action_id = %d, action_type = %d`
- `0x0071EA70` `[even_ai.page]recv evenai text_len = %d, text = %.*s`
- `0x0071EAE0` `[even_ai.page]not asked, not allow to show skills text`
- `0x007294BC` `[even_ai.page]not asked, not allow to show reply`
- `0x007294F0` `[even_ai.page]APP_PbRxEvenAIFrameDataProcess failed`
- `0x00733E24` `[even_ai.page]try to stop evenai, enable = %d`

## Linked extents

Physical interval `[0x004E1FD2, 0x004E2E10)` = 3646 bytes (3466 body + 222 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x4e1f7c-0x4e1fa6 | 42 | 0 | 17 | `59e7913e092ae6e0...` |
| 0x4e1fd2-0x4e20f2 | 288 | 2 | 110 | `d495c9ee8c23fba5...` |
| 0x4e20f2-0x4e2976 | 2180 | 8 | 814 | `3f96bcf987ab86c2...` |
| 0x4e2976-0x4e2a40 | 202 | 2 | 74 | `59f87112573f4879...` |
| 0x4e2a5c-0x4e2ad6 | 122 | 0 | 54 | `da45c4f47e59679c...` |
| 0x4e2ad6-0x4e2c22 | 332 | 0 | 138 | `ded428b8530bd949...` |
| 0x4e2c40-0x4e2d6c | 300 | 2 | 114 | `e95fdcb58af1eaa6...` |

## Ingress (whole-image scans)

- direct BL entry sites: 19; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 3
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Seven blocks: a detached 42-byte lazy-singleton helper [0x4E1F7C, 0x4E1FA6) (its only callers are this object's blocks, sites 0x4E297E and 0x4E2C84) and a six-block main cluster [0x4E1FD2, 0x4E2E10). Identity: 14 literal references to two retained path strings (cells 0x4E2A4C and 0x4E2DF4, both pooled inside the interval) across 4 blocks, and 14 `[even_ai.page]` tags (streaming text reception and display gating). Registration: descriptor cells 0x6A4504 and 0x6A4508 plus 0x791DB1; 19 direct BL entry sites, mostly intra-cluster.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_even_ai -v
```
