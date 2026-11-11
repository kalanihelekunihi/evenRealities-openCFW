# Wave 20 markers

## Scanner changes (.waves/inventory.py; backup .waves/w20-bak/inventory.py.w20pre)
1. raw_decompile no longer counts a "Ghidra" on a line that is an evidence citation: the line names a 6-hex-digit stock address and says verified/address-verified (CITE). It also no longer counts "Ghidra <version>" tool provenance (TOOLVER). AUTO-LIFTED and TODO-RAW always count.
   - Effect: the 4 wave19 stroke/fill citations are restored to their original "Ghidra label" wording and are not counted. The apollo-main .ld "Ghidra 12.1.4" provenance line is not counted.
2. inferred no longer counts an explicit negation: "no/not/without" followed by at most 3 words, then "inferred". The check also looks at the previous line, for wrapped comments.
   - Not counted any more: display_lv_init_children "no storage initializer inferred", file_ready_200746a8.ld "without an inferred initializer", l2c_signaling "no product initializer is / inferred", and 3 em9305 negations.
   - Still counted: cb_ring_battery ("no log strings ..., so its stock file is inferred") is a real inference.

## Resolved with evidence (apollo-main)
- g2c_nema_vg_path.c: UNVERIFIED x2 and GUESS (header). No ambient temps remain (nvg_leftover 0; wave19 per-site citations). The RMode argument is RN by the 5-vmsr scan.
- g2c_nema_leaves.c GUESS (context size 0x100). memzero 256 at 0x4b110e/0x4b1112; the next referenced RAM object is 0x20070aec = base+0x100.
- gpu_patch.h GUESS+inferred. Stock call sites 0x53de06/0x53eaa6 (gradient: r0 count, r1/r2 stack arrays, r3=#1) and 0x53ef2e (dash line).
- g2-apollo-main.ld GUESS (MRAM end / SSRAM size). Upstream ambiqhal-apollo510 am_reg_base_addresses.h:74-81. The raw marker is the tool provenance line (scanner rule 1).
- svc_dis_g2.c INFERRED. Stock DIS attribute record at 0x6d277c has pValue 0x20003ac4 and UUID 0x2A25 (Serial Number String).
- g2c_ble_leaves.c: the inferred marker is removed. +0x2f/+0x30 match upstream cordio app_db.c appDbRec_t (offsetof over every 200-byte config; AppDbRecordInUse body). The GUESS is narrowed to the vendor +0xc3 byte.

## Resolved (other targets)
- em9305 myapp sizes (UNVERIFIED (sizes) removed). From the ARC objdump corpus: ctor 0x30ea08; start 0x30eabc..0x30eaf4 with r2=0x80f97c and r3=4 (qLen). The next stock RAM refs are 0x801994 (+36) and 0x80f98c (+16).
- em9305 .ld: the wave18 "not plain ARC" claim is corrected. The code is plain ARCv2 (1274 prologues). The only SP write is 0x32e53a mov sp,r17.
- codec-a XIP: 11 ck803 libgcc bodies and crc32_no_comp match stock image_a_xip (addresses in g2-codec-a.ld).

## Still unresolved, and why
| marker | where | why |
|---|---|---|
| GUESS | hal/clkmgr-g2c/am_hal_clkmgr_g2.c | Needs a RAM map of stock g_sClkMgr* versus upstream. The hand copy and upstream copy are separate objects by design. Not attempted beyond review this wave. |
| GUESS | runtime/g2c-gnu/g2c_vectors.c | 10 IRQ handlers (0x442114 ... 0x5fa120) have no g2/src body. Resolving this means reconstructing those handlers, not finding evidence. |
| GUESS | g2c-nema/include/g2c_ghidra_shim.h | Describes a decompiler-compat shim that is not ABI-faithful. There is nothing to verify until the files using it are de-shimmed. |
| GUESS | ble/g2c-leaves (+0xc3) | Vendor field with no upstream counterpart; meaning is known only from the counter's use. |
| stub ("placeholders") | ui/a-61-navigation-data/notify_app_icon.c | No stock string names this file or function (checked notif/icon/app_id strings). No phone-app or BLE protocol doc in the repo mentions these tables (searched docs, g2/docs, g2/research, reviews, resources for MobileSMS/notify_app/app_icon). |
| weak x3 | runtime/a-68-iar-stdout/iar_stdout.c | Intentional weak overrides (unchanged). |
| inferred | cb_ring_battery.c | The forwarder at 0x500378 sits between a literal pool and CB_RING_BAT_Init with no strings, so its object membership cannot be proven. |
| inferred | aging_test_page.c | LVGL callee meanings come from their arguments. Those stock LVGL bodies have no strings and no name map. |
| inferred | g2_als.h | Roles without a DRV_ __func__ string. |
| inferred | dmic/i2s_request_provider.c | The transaction protocol is reconstructed from 0x57ce78/0x57d024 bodies. That is a real inference. |
| GUESS+FLAG | codec-a .ld | The csky_* DSP bodies occur in firmware_codec.bin only at 0x478a4..0x48164, outside image_a. __ashldi3/__lshrdi3/__cmpdf2/__eqdf2/__unorddf2/__fe_* have no image_a body. |
| FLAG+UNVERIFIED | em9305 .ld | The stack top is set from r17 by the caller/ROM. The 0x80fe20..0x80fe28 window has no direct refs, but 16 gp-relative loads were not resolved. |
| FLAG | touch, codec-a | unchanged |
