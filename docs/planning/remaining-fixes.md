# Remaining Cleanup Report

Generated: 2026-03-11

## Scope

This report analyzes `openCFW/src` C and header files to estimate how much of the tree still contains Rizin/Ghidra-style placeholder naming versus how much appears to have already been rewritten to use more explicit names.

I used two scan modes:

1. High-confidence auto-id scan
   - Looks for tokens that are strongly decompiler-shaped:
   - `paramN`, `local_*`, `saved_reg_*`, `ptr_N`, `w_N`, `FUN_*`, `LAB_*`, `DAT_*`, `uStack*`, `iVar*`, `bVar*`, `auStack*`, `puVar*`, `__fp`
2. Broad cleanup-needed scan
   - Includes the high-confidence tokens above plus weaker leftovers such as:
   - `buf`, `bits`, `undefined`

Important caveat:

- This is a text-pattern heuristic, not a full semantic review.
- A line with no match is not guaranteed to be perfectly named.
- A line with `bits` or `buf` is not always wrong, which is why the report separates high-confidence auto-ids from the broader cleanup scan.
- The raw `openCFW/src` tree includes bundled `third_party/` code and `_unclassified.c`, which heavily distort the apparent completion rate. Because of that, the report shows both:
  - raw `openCFW/src`
  - repo-owned/actionable subset excluding `third_party/` and `_unclassified.c`

## Summary Metrics

| View | Files | Total lines | High-confidence auto-id lines | High-confidence clean % | Broad cleanup-needed lines | Broad clean % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Raw `openCFW/src` | 377 | 487,532 | 29,535 | 93.94% | 36,995 | 92.41% |
| Repo-owned subset | 279 | 264,879 | 1,080 | 99.59% | 1,933 | 99.27% |

## Key Findings

- The raw tree still shows a noticeable amount of auto-id style text, but most of it is coming from bundled or decompiler-heavy areas rather than the actively cleaned repo-owned code.
- In the repo-owned subset, only `1,080` lines still contain high-confidence decompiler-style names, and `1,933` lines contain either those names or broader vague leftovers.
- Only `66` repo-owned files still have any broad cleanup hits, and only `45` still have high-confidence auto-id hits.
- That means the remaining cleanup is highly concentrated rather than spread broadly across the tree.

## What Is Still Left

### Repo-owned token counts

High-confidence auto-id occurrences:

- `paramN`: 465
- `saved_reg_*`: 357
- `ptr_N`: 256
- `w_N`: 122
- `local_*`: 60
- `FUN_*` / `LAB_*` / `DAT_*`: 0
- `uStack*` / `iVar*` / `bVar*` / `auStack*` / `puVar*` / `__fp`: 0

Broader cleanup-needed occurrences:

- `bits`: 982
- `buf`: 192
- `undefined`: 0

Interpretation:

- The most obvious function-label style artifacts appear to be gone from repo-owned `.c/.h` files.
- The remaining work is now dominated by parameter/local/register alias cleanup and lingering vague names like `bits` and `buf`.

## Current Hotspots

Top repo-owned files by remaining broad cleanup-needed hit lines:

| File | Broad hit lines | High-confidence hit lines |
| --- | ---: | ---: |
| `openCFW/src/platform/apollo510b/bootloader/hal/am_hal.c` | 1,125 | 459 |
| `openCFW/src/platform/apollo510b/bootloader/littlefs/lfs.c` | 266 | 224 |
| `openCFW/src/platform/apollo510b/main_firmware/platform/ble/app_ble.c` | 92 | 92 |
| `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c` | 87 | 87 |
| `openCFW/src/peripherals/touch_controller/libc/libc_math.c` | 21 | 10 |
| `openCFW/src/platform/apollo510b/main_firmware/app/gui/menu/menu_page.c` | 17 | 17 |
| `openCFW/src/platform/apollo510b/bootloader/hal/am_devices.c` | 16 | 9 |
| `openCFW/src/platform/apollo510b/main_firmware/app/gui/quicklist/quicklist.c` | 16 | 16 |
| `openCFW/src/peripherals/touch_controller/driver/clock.c` | 14 | 0 |
| `openCFW/src/peripherals/case_mcu/driver/uart.c` | 13 | 0 |

Concentration:

- The top 4 files account for `81.2%` of all remaining broad repo-owned hits.
- The top 4 files account for `79.8%` of all remaining high-confidence repo-owned hits.

This is the strongest signal in the scan: the project is not broadly dirty anymore, but it still has a few dense low-level files carrying most of the remaining cleanup burden.

## Sample Evidence

Examples from the current tree show that the scanner is finding real decompiler leftovers rather than only false positives:

- `bootloader/hal/am_hal.c`
  - `param2`, `param3`, `param4`
  - `ptr_1`, `ptr_2`
  - `bits`
- `bootloader/littlefs/lfs.c`
  - `ptr_1`, `ptr_3`, `ptr_6`
  - `w_1`, `w_2`, `w_3`
  - `buf`
- `main_firmware/platform/ble/app_ble.c`
  - `saved_reg_5`, `saved_reg_7`, `saved_reg_2`
- `main_firmware/platform/protocols/protocol_common.c`
  - `saved_reg_1c`, `saved_reg_18`, `saved_reg_24`

## Estimated Progress

There are two reasonable ways to express progress:

### 1. By line-level scan coverage

Using the repo-owned subset, the tree appears to be approximately:

- `99.59%` free of high-confidence decompiler auto-ids
- `99.27%` free of the broader cleanup-needed patterns

If you measure progress only by how many source lines still match these placeholder-style patterns, the cleanup looks almost finished.

### 2. By likely remaining human effort

A better estimate for the actual cleanup project is lower:

- Roughly `80%` complete by effort

Why the effort estimate is much lower than the line scan percentage:

- The remaining work is concentrated in hard low-level files.
- `bootloader/hal/am_hal.c` and `bootloader/littlefs/lfs.c` are dense and decompiler-heavy.
- The easy and medium cleanup passes are mostly already done; what remains is the slower long tail where each rename takes more validation.

## Bottom Line

- If the question is "how much of repo-owned `openCFW/src` still visibly contains placeholder/decompiler-style names," the answer is:
  - about `0.4%` of lines for high-confidence auto-id leftovers
  - about `0.7%` of lines for the broader cleanup-needed heuristic
- If the question is "how far are we likely into the cleanup process overall," the practical estimate is:
  - about `80%` complete

## Suggested Next Targets

1. `openCFW/src/platform/apollo510b/bootloader/hal/am_hal.c`
2. `openCFW/src/platform/apollo510b/bootloader/littlefs/lfs.c`
3. `openCFW/src/platform/apollo510b/main_firmware/platform/ble/app_ble.c`
4. `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c`

Cleaning those four files first should remove most of the remaining visible decompiler-style naming in the repo-owned `openCFW/src` tree.
