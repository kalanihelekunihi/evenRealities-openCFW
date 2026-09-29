# Recovered G2 configuration and patches

This directory holds byte-for-byte copies of the configuration headers and
patches recovered for the official G2 firmware `s200_v2.2.6.10`.

- **Upstream sources are not included.** Pair each file with the root
  submodule `third-party/upstream/<library>` at the commit listed in
  [../docs/reference/libraries.md](../docs/reference/libraries.md).
- **Paths.** Original paths are relative to the repository root at commit
  `832137ec`.
- **Hashes.** Every SHA-256 below was recomputed on the copy and equals the
  original.

## Confidence levels

- **Proven**: every value is pinned to bytes in the authenticated image.
- **Strong**: values rest on consistent structural evidence.
- **Compat**: an openCFW compatibility choice where the binary cannot
  discriminate, clearly separated in the file itself.
- **Not stock**: a build or tool fix that is not part of the vendor firmware.
  Never use these for a byte-equal build.

Unless a file says otherwise, each one is a partial configuration. An option
that is absent is unknown; it must not be read as the upstream default.

## Summary table

| File (in this directory) | SHA-256 | Confidence |
|---|---|---|
| `cmbacktrace/g2-config/cmb_user_cfg.h` | `9599205cc01589927c5384a316c8fd0919d2fb238f094c9f1b1933c55f85c411` | Proven (first block), Compat (CPU/language) |
| `cordio/g2-config/cordio_recovered_config.h` | `a908d4d003392c4fa2cfceef0e5d000bb448a67dbb4cf94fcb431c14366e68a2` | Proven (bounded) |
| `cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch` | `0b86bf4ff50cdae14662a9c06824404737993d966523421fd3a347d1c3fbdf52` | Strong |
| `flashdb/g2-config/fdb_cfg.h` | `9445f7c81d7a7ee55fd45868bc64733d0bb6e3f295b48ef7cda7c1346cc11cd6` | Proven |
| `freertos-plus-cli/g2-patches/0001-suppress-unknown-command-for-blank-input.patch` | `ada47a9141d44e465be3be4b878e61b1056c65986dd728003c169d9383491d70` | Proven (behaviour) |
| `freetype/g2-config/freetype/config/ftmodule.h` | `522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74` | Proven |
| `lvgl/g2-config/lv_conf_recovered.h` | `2876e2abb3821103d0f8dd7dda71e2b1cea70ab194ffe5c4955a194798d86b5b` | Proven (subset) |
| `lvgl/g2-config/lvgl_g2_abi.json` | `6e45a77ae37a9715bbf8dcc31440a845116a30ed5ff6b0de275cc04cafccef91` | Proven |
| `lvgl/tools-patches/lvgl-g2-ambiq-draw-buffer-abi.patch` | `17dedb9b304817621a0312d8231aa7426732e089c88403ea6ace98e746d31e4b` | Proven (layout) |
| `nanopb/g2-config/pb_g2_options.h` | `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` | Strong |
| `tinyframe/g2-config/TF_Config.h` | `af73f59617f4f6b63f2cd924a3f38abe0091e35dc7bc374d1814cca974c1430c` | Proven (values), Compat (error hook) |
| `freertos-kernel/g2-patches/g2-tcb-v10.5.1.patch` | `cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3` | Proven (layout) |
| `gx8002-tinyprintf/upstream-patches/tinyprintf-padding-loop.patch` | `3f5e79c0f4671f6d96c3a3a2761ead4c682769e6238164585682818f49f544c6` | Inferred (codegen shaping) |
| `toolchain-gx8002/toolchain-patches/gcc-safe-ctype.patch` | `61bdf58e166c79c394513a8df0779e5a4eb53fd9b194498af512be8e5dab76af` | Not stock |
| `toolchain-gx8002/toolchain-patches/README.md` | `095e9adb4f47fc24588f57a2c846c52f3beda55e875df21f65049bfcf5d7a39a` | documentation |

Each file is described in detail below.

## Files

### CmBacktrace: `cmbacktrace/g2-config/cmb_user_cfg.h`

- **Original path:** `g2/third_party/cmbacktrace/g2-config/cmb_user_cfg.h`
- **Applies to:** CmBacktrace `73714489`.
- **Configures:** CmBacktrace user configuration.
- **Recovered values (Proven):**
  - the FreeRTOS OS platform;
  - dump stack info;
  - `CMB_NAME_MAX 40`;
  - call-stack depth 32;
  - dump depth 16.
- **Compatibility choices (Compat):** the CPU is set to Cortex-M33 and the
  language to English, because the binary cannot tell these apart from the
  alternatives.
- **Unresolved:** `cmb_println` must be supplied by the build.
- **Evidence:** `g2/third_party/cmbacktrace/README.openCFW.md:33-40`,
  `g2/docs/research/cmbacktrace-identity-audit.md:40-50`.

### Cordio configuration: `cordio/g2-config/cordio_recovered_config.h`

- **Original path:** `g2/third_party/cordio/g2-config/cordio_recovered_config.h`
- **Applies to:** Cordio r20.05c `3656312d`.
- **Configures:** the Cordio host.
- **Recovered values (Proven, bounded):**
  - `DM_CONN_MAX 3`;
  - `WSF_BUF_FREE_CHECK_ASSERT 1`;
  - `WSF_BUF_STATS 0`, `WSF_BUF_STATS_HIST 0`;
  - `WSF_OS_DIAG 0`.
- **Not covered:** the header says nothing about the Ambiq port settings or
  the application database.
- **Evidence:** `g2/third_party/cordio/README.openCFW.md:50-56`.

### Cordio SMP patch: `cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch`

- **Original path:** `g2/third_party/cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch`
- **Applies to:** r20.05c `ble-host/sources/stack/smp/smp_main.c`.
- **Patches:** on an AES token mismatch, the patched code drains and frees
  `secCb.aesEncQueue`. This is Ambiq's AmbiqSuite 2.5.1 stale-AES cleanup
  (Strong).
- **Caveat:** stock also shows minor line-number drift, so the patched file is
  not the exact vendor text.
- **Evidence:**
  - `g2/third_party/cordio/README.openCFW.md:38-47`;
  - `g2/docs/research/cordio-ble-stack-identity-audit.md:398-406`;
  - `g2/tools/analyze_g2_cordio_smp_main.py`.

### FlashDB: `flashdb/g2-config/fdb_cfg.h`

- **Original path:** `g2/third_party/flashdb/g2-config/fdb_cfg.h`
- **Applies to:** FlashDB 2.1.1 `714d6159`.
- **Configures:** the FlashDB build.
- **Recovered values (Proven):**
  - `FDB_USING_KVDB`;
  - `FDB_USING_FAL_MODE`;
  - `FDB_WRITE_GRAN 1`;
  - KV and sector cache tables of 64 each.
- **Proven absent:** file modes, auto-update, and debug.
- **Unresolved:** the TSDB macro state; linker garbage collection may have
  removed TSDB code.
- **Target ABI requirement:** 32-bit short-enum.
- **Evidence:**
  - `g2/third_party/flashdb/README.openCFW.md:14-21`;
  - `g2/docs/research/flashdb-configuration-recovery-audit.md:13-45`.

### FreeRTOS+CLI: `freertos-plus-cli/g2-patches/0001-suppress-unknown-command-for-blank-input.patch`

- **Original path:** `g2/third_party/freertos-plus-cli/g2-patches/0001-suppress-unknown-command-for-blank-input.patch`
- **Applies to:** `FreeRTOS_CLI.c` at `43defa56`.
- **Patches:** for input that is only `"\r"` or empty, the "Command not
  recognised" text is suppressed. This is the only authenticated G2 delta.
- **Stock span:** `[0x005848CA,0x005848F4)`, SHA-256 `4ed35ac8…`.
- **Confidence:** Proven for the behaviour. The exact text is a reconstruction.
- **Evidence:** `g2/third_party/freertos-plus-cli/README.openCFW.md:29-37`.

### FreeType: `freetype/g2-config/freetype/config/ftmodule.h`

- **Original path:** `g2/third_party/freetype/g2-config/freetype/config/ftmodule.h`
- **Applies to:** FreeType 2.9.1 `86bc8a95`.
- **Configures:** the module list, in this exact order:
  1. autofit
  2. truetype
  3. cff
  4. psaux
  5. psnames
  6. pshinter
  7. sfnt
  8. smooth
  9. smooth_lcd
  10. smooth_lcdv
- **Source of the order (Proven):** the 10-entry `ft_default_modules[]` table
  at `0x0073EEF8`.
- **Evidence:** `g2/third_party/freetype/README.openCFW.md:18-20`.

### LVGL configuration: `lvgl/g2-config/lv_conf_recovered.h`

- **Original path:** `g2/third_party/lvgl/g2-config/lv_conf_recovered.h`
- **Applies to:** LVGL `344c7c31` plus the Ambiq backend `5be8e0ae`.
- **Configures:** an `lv_conf.h` subset (Proven subset). Every value is backed
  by image bytes:
  - **Colour and OS:** L8 at 8 bpp, FreeRTOS.
  - **Features:** FreeType, flex, grid, littlefs, BMP, span, and built-in
    object IDs.
  - **Ambiq backend:** the Ambiq draw backend and Ambiq VG, with command-list
    sectors of 100 × 1024.
  - **Nema and drawing:** `NEMAGFX_POWER_SAVE 1`, and complex software
    drawing off.
  - **Runtime:** a custom stdlib malloc, log level WARN, null assertions on,
    and little-endian.
- **Evidence:**
  - `g2/third_party/lvgl/README.openCFW.md:51-60`;
  - `g2/docs/upstream-inventory.md:744-778`.

### LVGL ABI record: `lvgl/g2-config/lvgl_g2_abi.json`

- **Original path:** `g2/third_party/lvgl/g2-config/lvgl_g2_abi.json`
- **Applies to:** LVGL.
- **Records (Proven):**
  - the Cortex-M55 short-enum ABI;
  - `sizeof(lv_global_t)=492` (`0x1EC`), `lv_display_t=796`,
    `lv_indev_t=220`, `lv_draw_buf_t=28`;
  - all `lv_global` field offsets;
  - the 576×288 display, native L8, Ambiq A4 output buffer of 82,944 B.
- **Contrast:** the official-ceiling reference compile gives 504 B for
  `lv_global_t`.
- **Evidence:** `g2/third_party/lvgl/README.openCFW.md:55-60`.

### LVGL Ambiq patch: `lvgl/tools-patches/lvgl-g2-ambiq-draw-buffer-abi.patch`

- **Original path:** `g2/tools/patches/lvgl-g2-ambiq-draw-buffer-abi.patch`
- **Applies to:** LVGL `344c7c31`, `src/draw/lv_draw_buf.h` and
  `lv_draw_buf_private.h`.
- **Patches:** adds the `clear_cb`/`copy_cb` members to
  `lv_draw_buf_handlers_t`. This is Ambiq's `d4dcd26b` ABI.
- **Why it matters (Proven layout):** with this patch the stock `lv_global_t`
  offsets are reproduced. The handler tables sit at `+0xC8`, `+0xE8` and
  `+0x108`.
- **Evidence:**
  - `g2/docs/research/lvgl-ambiq-source-abi-recovery-audit.md:50-60`;
  - `lvgl_g2_abi.json` (key `recovered_vendor_compile.ambiq_abi_patch`).

### nanopb: `nanopb/g2-config/pb_g2_options.h`

- **Original path:** `g2/third_party/nanopb/g2-config/pb_g2_options.h`
- **Applies to:** nanopb 0.4.9 `98bf4db6`.
- **Configures:** nanopb option guards (Strong). The header fails the build on
  any contradicting flag. It enforces:
  - no malloc;
  - 16-bit `pb_size_t`;
  - 64-bit support;
  - native double;
  - no UTF-8 validation;
  - packed structs;
  - packed arrays;
  - callback streams;
  - error messages;
  - `PB_MAX_REQUIRED_FIELDS=64`.
- **Nature of the file:** openCFW glue, not a vendor header.
- **Evidence:**
  - `g2/third_party/nanopb/README.openCFW.md:31-48`;
  - `g2/docs/upstream-inventory.md:1232-1239`.

### TinyFrame: `tinyframe/g2-config/TF_Config.h`

- **Original path:** `g2/third_party/tinyframe/g2-config/TF_Config.h`
- **Applies to:** TinyFrame `eb75483e`.
- **Configures:** the TinyFrame build (Proven values):
  - **Field widths:** ID, LEN and TYPE are 2 bytes each.
  - **Framing:** CRC16 checksum; SOF `0x01`.
  - **Types:** `TF_TICKS` is `u16` and `TF_COUNT` is `u8`.
  - **Buffers:** RX payload `0x6000`; send buffer `0x400`.
  - **Listener tables:** 128/32/10.
  - **Timeout and locking:** timeout 100; no mutex.
- **Compatibility choice (Compat):** the `TF_Error` hook is a port seam.
- **Also required:** `-fshort-enums`, and the G2 bookend magic words, which
  belong in the port rather than upstream.
- **Evidence:**
  - `g2/third_party/tinyframe/README.openCFW.md:11-17`;
  - `g2/docs/upstream-inventory.md:1224`.

### FreeRTOS TCB patch: `freertos-kernel/g2-patches/g2-tcb-v10.5.1.patch`

- **Original path:** `g2/components/shared/freertos/g2-tcb-v10.5.1.patch`
- **Note:** this file is outside the requested set. It is included because it
  is the only recovered FreeRTOS vendor delta.
- **Applies to:** FreeRTOS-Kernel V10.5.1 `def7d2df`, `tasks.c` and
  `include/FreeRTOS.h`.
- **Patches:** adds one `uint32_t` stack-depth field after `pcTaskName[32]`,
  mirrored in `StaticTask_t`, and assigns it in `prvInitialiseNewTask`.
- **Why it matters (Proven layout):** the patch reproduces the stock 112-byte
  TCB and all later offsets.
- **Unobservable:** the vendor's field name.
- **Evidence:**
  - `g2/docs/research/freertos-g2-tcb-vendor-patch-audit.md:7-30`;
  - `g2/components/README.md:1622-1632`.

### GX8002 tinyprintf: `gx8002-tinyprintf/upstream-patches/tinyprintf-padding-loop.patch`

- **Original path:** `g2/tools/upstream-patches/tinyprintf-padding-loop.patch`
- **Applies to:** `lvp_kws` `8bf9ee5c`, `utility/libc/tinyprintf.c`.
- **Patches:** moves the padding-loop decrement into the loop body. The
  behaviour is unchanged.
- **Why it exists (Inferred):** together with `-fno-tree-loop-optimize`, the
  patched `putchw` compiles to 204 bytes, which fits the stock 212-byte
  envelope. It shapes the generated code; it is not a proven vendor edit.
- **Evidence:** `g2/docs/research/gx8002-printf-recovery.md:100-109`.

### GX8002 host toolchain: `toolchain-gx8002/toolchain-patches/gcc-safe-ctype.patch`

- **Original path:** `g2/tools/toolchain-patches/gcc-safe-ctype.patch`
- **Applies to:** the host build of C-SKY GCC `1e9b7044` (13.0.1),
  `gcc/system.h`.
- **Patches:** upstream GCC commit `9970b576`, which moves `safe-ctype.h`
  after the C++ headers. This is required to build on macOS with libc++.
- **Confidence:** Not stock. It is a host build fix only.
- **Evidence:** `g2/tools/toolchain-patches/README.md:1-20`;
  `g2/tools/build_g2_csky_macos.py:22-39`.

### `toolchain-gx8002/toolchain-patches/README.md`

- **Original path:** `g2/tools/toolchain-patches/README.md`
- **Content:** provenance of the patch above, and the SHA-256 values of
  `system.h` before and after the patch.

## Related material not copied

These files are not copied here.

- **Kept in place (vendored trees):** the LVGL compile-compatibility patches
  and the musl-math patch under `g2/third_party/lvgl-ambiq-backend/g2-compat/`.
  They are tied to that vendored tree, which is being kept.
- **Deliberate deviations from stock:** `gcc-fp-bit-sticky-rounding.patch`,
  `newlib-kernel-{sin,cos}-loop.patch` and `newlib-fmod-signed-zero.patch`
  under `g2/components/shared/gx8002/`. They are corrections or experiments
  that differ from stock, so they are not usable for byte equality.
- **Application feature patches:** `canvas480`, `evenai_thumb` and
  `ring_gesture` under `g2/components/apollo_main/`. They are not recovered
  configuration.
