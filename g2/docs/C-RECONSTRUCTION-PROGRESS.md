STATUS: IN-PROGRESS

# G2 compilable-C reconstruction ledger

## Verified mid-level helpers + standard memcpy/memset — 2026-11-22 (10:48 AM CST, America/Chicago)

Bottom-up batch 2, same method as the leaf batch: idiomatic scalar-float
C, function-level compare against typographic bodies on Renode M55, then
replace only what passed. `fg_memcpy` / `fg_memset` now call standard
`memcpy` / `memset` instead of the typographic IAR bodies. No `fg_call`.
Emulator only; no flash; no commit.

**Verified (13,508 cases, 0 mismatches on the replaced symbols).** MAGIC
`0xF6A11E02`, final PC `0x30000000`.

| Symbol | Cases | Notes |
| --- | ---: | --- |
| `fg_memcpy` | 1472 | standard `memcpy`; vs IAR forward-copy, sizes 0..200, align 0..7 |
| `fg_memset` | 912 | standard `memset`; sizes 0..200, several fills and alignments |
| `fg_439ca4` | 1 | stores `0x21` to `fg_iar_err[0]` |
| `fg_4397a8` | 1056 | nonnegative `sqrt`; negative → error + qNaN `0x7FFFFFFF` |
| `fg_439e9c` | 2976 | 3-float max, skip leading `43a0f4` hit |
| `fg_439f24` | 2976 | 3-float min, same skip |
| `fg_439fb4` | 768 | 3-byte nonzero index list, return count 0..3 |
| `fg_43ba6c` | 9 | `fabs` of `2*count` floats; `out={count,2}` |
| `fg_43bc58` | 10 | `fabs` of `p[1]` floats; `out={1,p[1]}` |
| `fg_43baf4` | 3328 | two-double integer-ABI predicate (`!C` of `43c0b0`) |

**Not replaced.** `fg_43a5dc` (quadratic interpolation) had 1 mismatch
in 288 cases: a canonical qNaN `t` (which `43a0f4` does not treat as
special) produced VFP NaN payload `0x7FC00001` vs C `0x7FC00000`. The
typographic body stays in `g2c_fuel_gauge_cores.S`.

**Production replace.** Extended `g2c_fuel_gauge_leaves.c` / `.h`.
Removed typographic `fg_memcpy`, `fg_439be4`, `fg_memset`,
`fg_memset_inner`, `fg_4397a8`, `fg_439ca4`, `fg_439e9c`, `fg_439f24`,
`fg_439fb4`, `fg_43ba6c`, `fg_43bc58`, `fg_43baf4`, and `fg_43c0b0`.
Ten typographic globals remain: `fg_43a5dc`, `fg_439ce0`, `fg_439fe4`,
`fg_43bb14`, `fg_43bc84`, `fg_43be18`, `fg_43bfac`,
`nrf_model_process_43a698`, `nrf_model_init_43a1b0`,
`nrf_model_ttf_58eac4`.

**Not in this batch.** apollo-main was not rebuilt and the
version-match paired sim was not re-run (that check is due after a few
batches; this is batch 2). Linker-report string unchanged. Official
`opencfw-otap-disarm.app.bin` was not overwritten.

Evidence:
[`g2-20261122-fuel-gauge-mid-c.json`](../evidence/g2-20261122-fuel-gauge-mid-c.json).
Harness: `build/fuel-gauge-recon-20261122/c-leaves/mid_test.bin`.


## Verified leaf-callee C (bottom-up, no trampoline) — 2026-11-22 (10:35 AM CST, America/Chicago)

Changed approach as asked. The machine-level CFG lifter (`fg_cpu` +
`fg_call`) is not the translation method; that WIP remains in
`build/fuel-gauge-recon-20261122/c-lift/` and is still **not
verified**. This batch goes bottom-up: idiomatic scalar-float C for
true leaf callees, function-level compare against the typographic
bodies on the Renode M55 golden, then replace those typographic
bodies one batch at a time. No `fg_call` trampoline; normal AAPCS
(hard-float for s0/s1 leaves, integer r0:r1 for `fg_43a110` /
`fg_43a19c` / `fg_43a5b0`). Emulator only; no flash; no commit.

**Verified (12,464 cases, 0 mismatches).** MAGIC `0xF6A11E01`, COUNT
68 words, MISMATCH 0, final PC `0x30000000`. Inputs were IEEE
specials (signed zeros, denorms, inf, qNaN, sNaN) plus xorshift
randoms (seed `0xC0FFEE`); two-arg leaves also ran the specials ×
specials grid.

| Symbol | Cases | Notes |
| --- | ---: | --- |
| `fg_43a110` | 1060 | f32 bits → f64 bits, including denormals and sNaN quieting |
| `fg_43a19c` | 1280 | dual high-word qNaN-style HI check, not isnan/isfinite |
| `fg_43a0f4` | 1060 | promote s0 via 43a110, then 43a19c |
| `fg_439efc` | 2320 | min-like; ARM unordered LT; +0 vs ±0 returns b |
| `fg_439f88` | 2320 | max-like; -0 vs ±0 takes b; a NaN selects b |
| `fg_43a5b0` | 2084 | floor-like bit chop; ±0 preserved; Inf/NaN unchanged |
| `fg_43a5a0` | 2084 | hard-float wrapper around 43a5b0 |
| `nrf_model_tte_params_58eab0` | 256 | copy two floats to model state +0x48 / +0x4c |

**Production replace.** Added
`g2c_fuel_gauge_leaves.c` / `.h` and a `sources.json` unit (clang,
`g2-apollo-main-1`). Removed the eight typographic bodies from
`g2c_fuel_gauge_cores.S` (23 typographic globals remain, including
process, init, ttf, memcpy/memset, and mid-level helpers). Remaining
`.S` `bl` sites now resolve to the C symbols.

**Not in this batch.** Mid-level helpers, `nrf_model_process_43a698`,
and `nrf_model_init_43a1b0` are still typographic. The linker-report
canned "source-only uncalibrated" string is unchanged. apollo-main
was not rebuilt and paired sims were not re-run. Official
`opencfw-otap-disarm.app.bin` was not overwritten.

Evidence:
[`g2-20261122-fuel-gauge-leaves-c.json`](../evidence/g2-20261122-fuel-gauge-leaves-c.json).
Harness: `build/fuel-gauge-recon-20261122/c-leaves/`.


## WIP C lift of nrf_model_process_43a698 — 2026-11-22 (10:23 AM CST, America/Chicago)

Biggest core first, as asked. This batch is **not verified**. Production
`g2c_fuel_gauge_cores.S` is unchanged; the typographic body was not
removed. No linker-report string fix, no apollo-main rebuild, no paired
sims, no flash, no commit.

**Intent.** Replace the typographic process core (4864 B, 1458 reachable
insns) with scalar C, expanding MVE to 4-lane float operations and
DLS/LE to counted loops. Callees stay typographic for this batch and
are called through a small `fg_call` trampoline. Work lives only under
`build/fuel-gauge-recon-20261122/c-lift/`.

**Lifter fixes so far.** Condition-suffix mis-parses (`movs`/`dls`);
`sl` vs `s-register`; VMOV immediates taken from the objdump `@
0x40000000` annotation (the `#0` form is 2.0); PC-relative `vldr`/`adr`
now read baked `core_proc.bin` pool bytes via `fg_stock_ptr`; `fg_call`
saves the cpu pointer and hardware SP in BSS so typographic helpers
cannot clobber them.

**Renode M55.** The standalone EVENBAT harness writes MAGIC
`0xF6A11E00` but COUNT stays 0 after 2 s of guest time (250 MIPS). PC
remains around typographic `memcpy`. A helper-call log showed a sane
first `memcpy(..., 8)` as call 9, then the run never finished. No
golden compare (EVENBAT / 24 random / param_9 mutant) was completed.

Next: finish debugging this process lift until it matches `golden2` /
`mutant2`, then remove the process body from `.S`. Evidence:
[`g2-20261122-fuel-gauge-process-c-lift-wip.json`](../evidence/g2-20261122-fuel-gauge-process-c-lift-wip.json).



## Verified nrf_fuel_gauge C + MVE cores rebuilt and paired sims — 2026-11-22 (10:00 AM CST, America/Chicago)

Follow-on to the Renode-M55 golden and in-tree replacement below. Emulator
only; no flash; no commit. Official `opencfw-otap-disarm.app.bin` was not
overwritten. `source_completeness_proven` stays **false**.

**Build.** `sources.py` 2719/2719, 0 failures, 0 duplicate strong symbols,
21 composed unresolved. Linked image
`build/g2-apollo-recovery-20261122-fuel-gauge-c-link/g2-apollo-main/g2-apollo-main.bin`
is **3,629,904 B**, SHA-256
`78e7cd88d07aaafe9427e42ec915b81a7f1eeddcc50924221ecf40bf37b20457`,
reset PC `0x0052EA35` (SP `0x2007FB00`). That is +9,860 B versus the
gc-fnsec image (typographic cores vs the source-only estimate). Installed
only as `build/em9305-nor-20261122/opencfw-fuel-gauge-c.app.bin`. The
linker report's canned "source-only uncalibrated" qualification string
was not edited.

**Version-match (8 s).** CHIPREV stays `0x22`. OTAP `0xAFD1363A` at 0.01 s
and `0` at 8 s. Host packets `0x3A`, unsupported `0`, advertising
`010A200101`, display frame
`0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`.
End PC `0x4ce6ec` (layout; gc was `0x4cbdd4`, stock `0x44adfa`).

**Forced-mismatch DFU (controller word `00010304`, 8 s, completed path).**
922 HCI host packets, identical opcode histogram to stock: 1× FD06
`NVMEraseMain`; 857× FD03; 4× FC4E CRC32 with the same digests
(`0xD2C17B4C`, `0x6E09DDA8`, `0xDA9653E5`, `0xE498BC06`); 1× FD07 INFO
erase at `0x00402000`; 1× FD03 commit at `0x00402000` starting
`00020404`; SYSRESETREQ; SBL *application* handoff (not wired-load)
VTOR `0x00438000` SP `0x2007FB00` PC `0x0052EA35`; then advertising
`010A200101`. At 8 s: OTAP `0`, config mode false, `NvmMainErased`
false, unsupported 0, host monitor `0x3A`. Same display hash.

Verdict: PASS. Evidence:
[`g2-20261122-fuel-gauge-c-paired-sims.json`](../evidence/g2-20261122-fuel-gauge-c-paired-sims.json).


## Renode M55 golden and typographic nrf_fuel_gauge translation — 2026-11-22 (09:51 AM CST, America/Chicago)

Supersedes the 09:21 AM CST Unicorn NOP+hook harness note. That method
is **not** the official golden: NOP-patching 155 MVE sites would corrupt
computed values. `qemu-system-arm -M mps3-an547` has M55/MVE but does
not map stock `0x00438000`, and this machine has no `qemu-arm`
user-mode. The reference is **Renode 1.17** (`cortex-m55`, native MVE
and LOB), RESULT at `0x20068000` (away from SP `0x2007FB00`).

**Golden (real EVENBAT at `0x00646BF8`).** `init(NULL)` / null model
return -22. `init(4.10 V, 0 A, 25 C)` returns 0; first process SOC
70.84683990478516, yhat 4.099989414215088, r0 2.3588204383850098, T
truncated to 26 C, TTE 0, TTF NaN. At 4.20 V rest, SOC
80.03155517578125. After 120 s at 50 mA from 4.20 V: SOC
78.98108673095703, TTE 27427.212890625. Doubling EVENBAT `param_9[0]`
doubles r0 to 4.7176408767700195; first rest SOC is unchanged. 24
xorshift cases (seed `0xC0FFEE` after init 4.05 V).

**Translation.** C wrappers in `g2c_fuel_gauge_source.c` plus typographic
relocation of `0x43A698` / `0x43A1B0` and callees in
`g2c_fuel_gauge_cores.S` (MVE/LOB kept as `.byte`; hard-float AAPCS).
Not a portable scalar lift. Cores use profile `g2-apollo-main-mve-1`
(`-mcpu=cortex-m55`). Apple clang rejected `.arch_extension mve`, so
those directives were stripped (bytes do not need them). IAR `expf` /
`logf` go through the existing in-tree shims.

**Match.** Tag-aligned records against `golden2` / `mutant2` are
bit-exact through end-tag `0xE0D00000`, including all 24 random cases
and the `param_9` mutant. Raw 2048-byte dumps are not SHA-identical
because the stock harness overwrote tag `0x1001` with the count word.
The source-only estimate was **replaced** in-tree (`sources.json`
units 4880). Evidence:
[`g2-20261122-nrf-fuel-gauge-renode-m55-c-recon.json`](../evidence/g2-20261122-nrf-fuel-gauge-renode-m55-c-recon.json).



## Stock nrf_fuel_gauge Unicorn harness — 2026-11-22 (09:21 AM CST, America/Chicago)

Item (2). Emulator/host only; no flash; no commit. The source-only estimate
in `g2c_fuel_gauge_source.c` was **not** replaced: a verified C body of the
stock algorithm is not ready yet.

**Stock identity.** The linked library is **c205a2 / 2025-04-28**, not the
in-tree Nordic 1.0.1 M4 `.a`. EVENBAT tables were already extracted
(`0x00646BF8`, name at `+0x15C0`). Entries: init `0x0043C150`, ext-state
`0x0055F74C`, process `0x0055F848`, TTE `0x0055F994`/`0x0058EABC`, TTF
`0x0055F9A0`/`0x0058EAC4`. Model state lives at `0x20070CE0` (0xE8 bytes,
TTE at `+0x84`, model pointer at `+0xE0`).

**Why this is not a straight decompile-and-link.** Stock IAR code uses MVE
(155 sites: `vstrw`/`vldrw`, `vmul`/`vadd`/`vsub.f32` on Q regs, `vdup.32`,
structured `vld4`/`vst4`) and 16 Armv8.1-M `dls`/`le` loops, plus one
`vcvt.f64.f32` isfinite helper. Unicorn has no native MVE or low-overhead
loops. A Cortex-M7 Unicorn harness now patches those sites to NOP and
emulates them from an objdump site table. `qemu-system-arm` *does* provide
`mps3-an547` (M55), but that machine does not map the stock 0x00438000
window, so it was not used as the golden this step.

**Golden results (real EVENBAT).** `init(NULL)` and `init` with a null
model return -22. `init(4.10 V, 0 A, 25 C)` returns 0, writes the
adjusted voltage, sets ext-block `{idle, 1.0, 1.0, NaN, NaN}`, and stores
the EVENBAT pointer. First `process` at 4.10 V rest yields SOC
70.84684, yhat 4.09999, r0 2.35882 (EVENBAT `param_9[0]`), T truncated
to 26 C. At 4.20 V rest, SOC is 80.03156. After 120 s at 50 mA
discharge, SOC 78.98109 and TTE 27427 s; TTF is NaN while not set up
to charge. Doubling EVENBAT `param_9[0]` doubles reported r0
(2.35882 → 4.71764); the harness is sensitive to the real table.

**Not done.** The process core at `0x0043A698` / `0x0043A1B0` has not
been rewritten as verified C, so the source-only voltage/coulomb
estimate remains. No rebuild and no paired Renode runs (image
unchanged). Evidence:
[`g2-20261122-nrf-fuel-gauge-stock-harness.json`](../evidence/g2-20261122-nrf-fuel-gauge-stock-harness.json).


## Full forced-mismatch DFU pair on gc-fnsec — 2026-11-22 (09:05 AM CST, America/Chicago)

Item (1). Emulator only; no flash; no commit. Re-checked the already-run
8 s `opencfw-gc-fnsec-dfu-mismatch` pair against stock. The same fixture
is the completed-DFU path (controller word `00010304`); the prior
gc-fnsec note that called it "bring-up, not a completed DFU cycle" was
wrong.

**Sequence, identical on stock and gc-fnsec (922 HCI host packets):**
enter config mode; 1× FD06 `NVMEraseMain`; 857× FD03 program writes
from `0x00300000` through `0x00402000`; 4× FC4E CRC32
`[0x00300000,0x003000E0)=0xD2C17B4C`,
`[0x00300400,0x00300690)=0x6E09DDA8`,
`[0x00302000,0x00302038)=0xDA9653E5`,
`[0x00302400,0x00335BC8)=0xE498BC06`; 1× FD07 INFO erase at
`0x00402000`; 1× FD03 commit at `0x00402000` starting `00020404`
(stock 4.4.2.0 version word, replacing the mismatch fixture);
SYSRESETREQ; SBL *application* handoff (not wired-load) at VTOR
`0x00438000` SP `0x2007FB00`; advertising enable `010A200101`. At 8 s:
OTAP `0`, config mode false, `NvmMainErased` false, unsupported 0, host
monitor `0x3A`. Display frame hash still `0c5cc90b…`. Handoff/end PCs
differ only by image layout (stock `0x005E4233`/`0x44adfa`, gc
`0x0052C11D`/`0x4cbdd4`).

Verdict: PASS. Erase, CRC, commit, and post-DFU handoff match stock.
Evidence:
[`g2-20261122-gc-fnsec-dfu-complete-pair.json`](../evidence/g2-20261122-gc-fnsec-dfu-complete-pair.json).


## Apollo-main -ffunction-sections and --gc-sections adopted — 2026-11-22 (09:02 AM CST, America/Chicago)

Item (3). Official `opencfw-otap-disarm.app.bin` was not overwritten. No
flash; no commit. `source_completeness_proven` stays **false**. `-Oz`
was not applied.

**Build changes.** Added `-ffunction-sections -fdata-sections` to the 17
`g2-apollo-main-*` profiles that lacked them (26 already had both).
`link_g2_sources.py` now passes `-Wl,--gc-sections` for apollo-main too.
The linker script already KEEP'd `.isr_vector`, `kvdb_migration`, the
OTA flag page, and bond records; it now also KEEP's `.itcm_text*` and
`.ramfunc*` so region-table ramfuncs survive gc.

Function-sections made the existing strong pair
`am_hal_sysctrl_aircr_reset` (self_recovery override vs generated HAL)
visible to the compose duplicate check. Followed the existing `#if 0`
pattern on the generated HAL function so the intentional
`g2_recovery_reset_app` disarm-then-SYSRESETREQ remains the only
definition.

**Image.** `build/g2-apollo-recovery-20261122-gc-fnsec-link`: 2718/2718
compiled, 0 dups, 21 composed unresolved. **3,620,044 B** (SHA-256
`1f6078706a075e32a4bc93f51bb49a0745d0e0d867b6c8874697940c77ecebcb`),
SP `0x2007FB00`, reset PC `0x0052C11D`, end `0x007ABCCC`. Saved
**199,404 B** versus the 3,819,448 B otap-disarm image. Still +96,680
versus stock 3,523,364. Headroom to `0x007FE000`: **336,692 B**, so
`-Oz` was not required. ITCM ramfuncs kept at `0x58..0x70`; recovery
reset kept. `wrap_main_image` accepted the image.

**Paired sims (CHIPREV 0x22, same NOR fixture, stock 24-byte ITCM
overlay).** Both match the established otap-disarm 8 s baseline:

- Version-match: OTAP `0xAFD1363A` at 0.01 s, `0` at 8 s; 58 host
  packets; 0 unsupported; advertising enable `010A200101`; display
  frame hash `0c5cc90b…` (same stock-identical hash as before); OTA
  flag `nv_program` at `0x007FE000`.
- DFU-mismatch: same OTAP/host/advertising/display results; SBL
  *application* handoff (not wired-load); `ConfigurationMode` still
  false and `NvmMainErased` still false at 8 s, as in the prior
  8 s fixture (that run is bring-up, not a completed DFU cycle).

Evidence:
[`g2-20261122-apollo-main-gc-fnsec.json`](../evidence/g2-20261122-apollo-main-gc-fnsec.json).


## Slot-fit check (3.82 MB apollo-main, 246 KB EM9305) — 2026-11-22 (08:53 AM CST, America/Chicago)

Critical boot check before adopting gc. Host arithmetic only; no flash;
no commit.

**Apollo-main current image fits.** `opencfw-otap-disarm.app.bin` is
3,819,448 bytes, loaded at `0x00438000`, ending at `0x007DC7B8`
(confirmed from ELF PT_LOAD physical addresses). The hard install end
is the bootloader-owned OTA flag page at **`0x007FE000`**
(`MAIN_UPDATE_FLAG`; `wrap_main_image` / `validate_apollo_main` /
`.ld` ASSERT). Max installed app is 3,956,736 B. Headroom: **137,288
B**. Bond records at `0x007FF000` are after that page and are not
reached. SBL ROM `0x00400000–0x00410000` and the bootloader slot
`0x00410000–0x00438000` are not overlapped.

The 32-byte OTA preamble sits at file/`0x00437FE0` and is skipped by
the DFU programmer; OTA is single-slot into the same MRAM app window
(no proven rollback). The 22-bit Ambiq standard-image size field allows
up to 4,194,303 B including the header (wrapped size would be
3,819,480). The Renode HLE SBL `maxStorage` (3,964,928; default
`0x003C8000`) extends past `0x007FE000` and must not be used as the
install cap.

littlefs (`NOR 0x01400000–0x01FC0000`) and FlashDB `kvdb`/`NVdb`
(`0x01FC0000–0x02000000`) live on the 32 MiB MX25U25643G, not in MRAM,
so growing the app does not overlap them. The first 20 MiB of NOR is
uncharacterised (resources / possible staged images) and is far larger
than 3.82 MB; that download location is unverified.

The item-(b) `/tmp` gc-probe (3,671,520 B, end `0x007B85E0`) also fits,
with 285,216 B of headroom.

**EM9305 source package also fits.** 246,040 B is the host container,
not a flat load. NVM is `0x00300000–0x00380000` (512 KiB). Source
records: bootloader 1,160 B ending `0x00300488` (under the `0x00302000`
ASSERT), record 2 56 B, application 244,708 B ending **`0x0033DFE4`**,
**270,364 B** before `0x00380000`. Stock app ended at `0x00335BC8`.
Datasheet window is `0x00302400–0x00380000` with no FOTA updater record
in the stock package; the grown source app stays inside it. Region
overflow would fail the EM9305 link.

Evidence:
[`g2-20261122-slot-fit-check.json`](../evidence/g2-20261122-slot-fit-check.json).

## Item (a) outcome: real KWS weights, one algorithm still synthetic — 2026-11-22 (08:53 AM CST, America/Chicago)

Asked after the (a) extraction/verification step.

**Yes: the real KWS weights and command stream are already extracted
and are what packaging uses.** They are not a synthetic all-zero
fixture. Official `firmware_codec.bin` windows: commands
`[0x18D90, 0x1B15C)` = 9,164 B (SHA-256 `c38ed6d2…`); weights
`[0x1B15C, 0x3893C)` = 120,800 B (SHA-256
`397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf`).
Asset `g2/src/codec/npu/kws_weights_2_2_6_10.bin`; C translation
`kws_weights_source.c`. `make source-bundle` already passes
`--codec-a-weights-from-source`. Verifier
`g2/tools/verify_stock_data_assets.py` exits 0. Wake-word was not
executed in sim (no GX8002/NPU in Renode).

**Other stock tables also extracted and bit-exact:** EVENBAT
`struct battery_model` 5,632 B; 29 ROM font uint8 arrays (167,200 B);
app L8 image pixel arrays (6 arrays, bit-exact once comments are
stripped). All are present in the current openCFW image.

**Still synthetic / not extractable as data:** only the Nordic
fuel-gauge *algorithm* in `g2c_fuel_gauge_source.c` (uncalibrated
voltage/coulomb stand-in). The EVENBAT *tables* are stock; the
proprietary `nrf_fuel_gauge` body is not. The KWS weight *bytes* are
stock; the internal tensor grammar is unproven but that is not
placeholder data.

Full write-up: 8:50 AM CST section below, and
[`g2-20261122-stock-data-assets.json`](../evidence/g2-20261122-stock-data-assets.json).


## EM9305 +34,092 B attribution — 2026-11-22 (08:48 AM CST, America/Chicago)

Functionality-first item (c). Host analysis of the latest complete
source-link image (`build/g2-current-source-bundle-diagnostic-20261112T1130Z`).
No EM9305 rebuild, no official-image change, no flash, no device, no
commit. `source_completeness_proven` stays **false**. The 22 Nov recovery
NOR still packages official `firmware_ble_em9305.bin` (SHA-256
`91a38f7fc0…`), not this candidate.

Stock package is 211,948 bytes (124-byte metadata + 211,824 payload) and
has **four** records: `0x00300000` 224 B, `0x00300400` 656 B,
`0x00302000` 56 B, `0x00302400` 210,888 B (application). The 12 Nov
source-candidate package is 246,040 bytes (**+34,092**; Nov 11 quoted
+36,748 against an older/implied 248,696-byte package). It has **three**
records:

- `0x00300000` 1,160 B C NVM bootloader (roles of stock records 0 and 1,
  different layout; ends at `0x00300488`, overlapping the stock
  `0x00300400` slot; not a verbatim concatenation of those records).
- `0x00302000` 56 B record 2, same length as stock but different CRC
  fields because they are finalized from the linked application.
- `0x00302400` 244,708 B application (**+33,820** vs stock 210,888,
  +16.0%). This is almost the whole packaged gap.

**`-O` level is not the apollo-main story.** All 768 linked units are
already `-Os -fno-tree-loop-distribute-patterns` (766 on profile 1, 2
on profile 2), with no `-ffunction-sections` in the profiles. Compiler
is GNU ARC 15.2.0. The application gap is therefore GNU-vs-stock
codegen and/or unused code trapped in a merged `.text` (map: vectors
1,024 + `.text` 233,120 + `.rodata` 4,838, plus smaller contributions),
not an `-O2`/`-Oz` mix. That split was not measured.

**Unused upstream already trimmed only where named.** The final link
does not pass `--gc-sections`. `g2-em9305.ld` `/DISCARD/` already drops
1,256 B of unmodified QP/C 6.5.1 APIs stock does not link (`QTicker_*`,
`QK_schedLock`, `QHsm_isIn`, upstream `QF_init`/`QF_run`/`QF_bzero`,
`QEQueue_*`). A broader unused-function trim would need
`-ffunction-sections`; enabling gc was previously rejected because it
dropped the image too far and broke freestanding memcpy. Not repeated
here.

No official rebuild and no sim of a new EM9305 image. Bootloader
selection/reset equivalence and a physical EM9305 run remain
unverified.

Evidence:
[`g2-20261122-em9305-size-attribution.json`](../evidence/g2-20261122-em9305-size-attribution.json).


## Apollo-main +296,084 B attribution — 2026-11-22 (8:43 AM CST, America/Chicago)

Functionality-first item (b). Host analysis of the already-linked
`opencfw-otap-disarm` apollo-main image. No official rebuild, no flash,
no device, no commit. `source_completeness_proven` stays **false**.

Current `opencfw-otap-disarm.app.bin` is 3,819,448 bytes versus stock
`stock.app.bin` 3,523,364 (**+296,084**). A `/tmp` probe link of the
same composed `g2-apollo-main.o` with `-Wl,--gc-sections` (not adopted)
produced 3,671,520 bytes and therefore accounts for **147,928 B** of
the growth. **148,156 B** would still remain versus stock after that
probe. The probe image was not sim-run.

**Duplicated code: not the image-level cause.** The final ELF has no
duplicate global symbol names. Current compose is `arm-none-eabi-ld -r`
plus `defsym` aliases; `sources.json` has no `ld_flags` and does not
pass `--allow-multiple-definition`. The three names
`g2_log_transport_vformat_unbounded`, `g2_flashdb_vformat`, and
`audio_heap_formatter` are aliases of one 3,252-byte body, not
triplicate code. Repeated local `OUTLINED_FUNCTION_*` names are
compiler outlining. The 35 unique 3,600-byte `pixels_*` frames are all
present verbatim in stock.

**Unused upstream, measured lower bound 147,928 flash bytes.** Final
link explicitly omits `--gc-sections` for `g2-apollo-main`
(`tools/build/link_g2_sources.py`). Compose is also `ld -r` without
gc, so leftovers stay in the image. The composed object still has
6,850 `.text.*` function sections (985,930 B) from the 708 units built
with `-ffunction-sections`; those can be discarded at final link. The
other 1,960 units were compiled without `-ffunction-sections` and have
already been merged into a 948,952-byte `.text` that gc cannot trim at
function grain.

The probe drops 1,868 named symbols. Flash-resident examples:

- `am_hal_pin_fn_list` (7,168 B): unused Ambiq HAL pin-function table;
  not present as a byte span in stock; dropped by the probe.
- `ft_adobe_glyph_list` (55,997 B): **kept** and present in stock;
  referenced by `ft_get_adobe_glyph_index` — not extra bloat.
- LC3 PLC/HR helpers (`lc3_plc_*`, `lc3_hr_setup_decoder`, related
  synthesizers): `sources.json` already notes `lc3_plc_*` are absent
  from stock and would be dropped by a final `--gc-sections` link.
- Unused LVGL widgets and indev paths (dropdown, table, chart, menu,
  encoder/keypad).
- LZ4 compress-side (`LZ4_compress_generic_validated`, 2,248 B).

**`-O` level differences: present, not quantified.** Linked mix is
2,134 units at `-O2` and 534 at `-Oz` (default profile
`g2-apollo-main-1` is `-O2` without function-sections, 1,791 units).
Clang is `-mcpu=cortex-m55+nomve`. Stock is IAR. No `-Oz` rebuild was
run, so the share of the remaining 148,156 B that is optimizer vs
unused code trapped in merged `.text`/`.rodata` vs `+nomve`/`-fno-inline`
is not measured.

Not done: did not enable `--gc-sections` on the official apollo-main
link, did not recompile the 1,960 units with `-ffunction-sections`,
did not sim the probe image. Next: (c) EM9305.

Evidence:
[`g2-20261122-apollo-main-size-attribution.json`](../evidence/g2-20261122-apollo-main-size-attribution.json).


## Stock data assets (KWS weights and other tables) — 2026-11-22 (8:50 AM CST, America/Chicago)

Functionality-first item (a). Host verification only; no flash; no device;
no commit. Codec GX8002/NPU is not in Renode, so wake-word was not
executed in sim.

**KWS weights were already extracted (11–12 Nov 2026) and are not a
synthetic all-zero fixture in the current tree.** `make source-bundle`
already passes `--codec-a-weights-from-source`. This step re-checked the
bytes and recorded offsets/format.

- Official `firmware_codec.bin` SHA-256
  `b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0`.
- Command stream: FWPK/`firmware_codec` `[0x18D90, 0x1B15C)` = BINH A
  `[0xF804, 0x11BD0)`, 9,164 bytes, SHA-256 `c38ed6d2…`, staged to DRAM
  `0x20003304`. Field-level C emitters already reproduce this window.
- Weights: `[0x1B15C, 0x3893C)` = BINH A `[0x11BD0, 0x2F3B0)`, 120,800
  bytes, SHA-256 `397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf`,
  staged to DRAM `0x200056D0`. Asset
  `g2/src/codec/npu/kws_weights_2_2_6_10.bin`; C translation
  `kws_weights_source.c` (`g2_kws_weights_source[30200]`, section
  `.g2_kws_weights`) packs to the same bytes. Stock BINH A NPU tail is
  exactly cmd+weights (`0xF804+9164+120800=0x2F3B0`, start of BINH B).
- Format: LVP_KWS gxNPU command stream + trained weight bank. Sizes are
  firmware getters (`movi r0,9164`; `movi r0,55264` + `bseti r0,16`).
  Word0 is `0xa79bab66` (not zlib CRC of the rest). Internal tensor
  grammar remains unproven.

**Other stock data already in source, re-verified:**
- EVENBAT `struct battery_model` (5,632 B) from VA `0x646BF8`, name at
  +`0x15C0`; present in current `opencfw-otap-disarm` (different
  address).
- ROM fonts: 29 uint8 arrays, 167,200 bytes, bit-exact vs official OTA,
  all present in the current openCFW image. LVGL 9 fmt_txt.
- App L8 images: pixel arrays bit-exact vs stock (one listing has a
  comment `0x` token; first `0x190` bytes still match) and present in
  the openCFW image.

**Still a placeholder, not extractable as tables:**
`g2c_fuel_gauge_source.c` — uncalibrated source-only Nordic API stand-in.
The EVENBAT *tables* are stock; the *algorithm* is not.

Verifier: `g2/tools/verify_stock_data_assets.py` (exits 0). Sim note:
boot-time display frames were already stock-identical in the 22 Nov
paired Renode run.

No commit. Next: (b) attribute apollo-main +296 KB growth.

Evidence:
[`g2-20261122-stock-data-assets.json`](../evidence/g2-20261122-stock-data-assets.json).

## Source-completeness triage (biggest first) — 2026-11-22 (8:35 AM CST, America/Chicago)

Opened the source-completeness work after the SBL recovery tool. No
rebuild, no flash, no commit. `source_completeness_proven` stays
**false**.

The compare tool and the 12 Nov 2026 diagnostic already state the bar:
all six official components and the whole bundle still differ from the
locked 4,301,227-byte 2.2.6.10 artifact; link success is not coverage or
stock identity; G1–G6 remain `not_run`. The flag is not something to
flip from this triage.

**Biggest first.** Apollo-main. Current
`opencfw-otap-disarm.app.bin` is 3,819,448 bytes versus stock
`stock.app.bin` 3,523,364 (**+296,084**; Nov 11 was +295,664 before the
intentional-reset disarm hooks). ELF: text+rodata 3,638,133, data
181,312, BSS 3,422,620. This payload is already a strict source link
(no external binary archive, no binary fuel-gauge). The delta is
compiler/placement/data image, not a missing library. Same-offset
equality is only ~4% because layout diverges immediately (reset vector
stock `0x005E4233` vs openCFW `0x0059427D`). Sim functional bring-up
through advertising, DFU, case-reply and the new SBL recovery path is
strong; hardware boot equivalence is not.

**Then, by Nov 11 size delta:** EM9305 +36,748; bootloader +5,633;
touch −5,644 (smaller than stock — possibly missing content); case
+4,416; codec packaged size matched and KWS commands were exact, but
weights were synthetic and the component is not byte-identical.

Next closeable no-hardware step on the biggest component: attribute the
+296,084 bytes against pre-compose objects/sections, then move to
EM9305.

Evidence:
[`g2-20261122-source-completeness-triage.json`](../evidence/g2-20261122-source-completeness-triage.json).

## Host SBL recovery tool sim-verified — 2026-11-22 (8:30 AM CST, America/Chicago)

Built and sim-verified a host-side tool that would reflash official stock
2.2.6.10 over the Apollo510 wired-update protocol. Emulator-only; no
device opened; no flash; no commit.

**Dev temples in SBL?** Probably not. The current pair was bricked on
pre-arm builds, so a hang does not leave `OTAPOINTER=0xAFD1363A`. The
tool is the recovery path if a later recovery-arm image hangs before
disarm (or any temple that is actually in wired-load).

**Sim extension.** `G2Apollo510_SblWired` is an HLE of the documented
AmbiqSuite 5.2.0 `uart_wired_update` framing (HELLO / 96-byte STATUS /
OTADESC `0x7FE000` / UPDATE / DATA / RESET), entered from
`wdt.HandoffAfterSystemReset` when the recovery key is still set. It
is not the protected SBL ROM. Existing tests stay unchanged unless the
peripheral is instantiated.

**E2E against that SBL.** OpenCFW `opencfw-otap-disarm` arms at 0.01 s,
unexpected reset → wired-load (CPU halted). Host
`g2/tools/sbl-recovery` sends official
`ota_s200_firmware_ota.bin` (SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`,
3,523,396 bytes). HELLO returns STATUS (`maxStorage=3964928`); bad CRC
and early DATA are rejected; 431 UART DATA frames + RESET program the
payload at `0x00438000` (SHA-256 matches `stock.app.bin`
`19044a72…`), clear OTAP, and hand off `SP=0x2007FB00` /
`PC=0x005E4233`. Postflight still running (PC `0x42`, ITCM delay).

**Hardware hookup** (fail-closed; not executed): USB Smart Case →
YHM2510 pogo, one sacrificial temple, route reg7=5/3, baud 1 M then
115200, case DATA 997 bytes, HELLO immediately after a real wired-load
entry, require a CRC-valid STATUS before UPDATE. No STATUS: stop. See
`g2/tools/sbl-recovery/README.md`.

No commit. Next: source completeness (`source_completeness_proven=false`
and the six-component differences), biggest first.

Evidence:
[`g2-20261122-sbl-recovery-sim.json`](../evidence/g2-20261122-sbl-recovery-sim.json).

## (3) case-reply disarm + pre-ADV unexpected reset — 2026-11-22 (8:15 AM CST, America/Chicago)

Emulator-only on `opencfw-otap-disarm.app.bin` (SHA-256
`7c691d8ce955479f748554628107e977cc723ef945b6509dcd00dae1aac625dd`,
reset `0x0059427d`). No rebuild. No flash. No commit.

**(3) case-reply.** First inject used the wrong frame (`01 00 00 00 00 84`)
and/or raced ADV (~0.28 s clears OTAP). Correct recipe from boot-trace
STATUS: uart2 `24 00 01 00 A7`. To isolate the case path from ADV disarm:
boot past ADV (OTAP→0), re-arm `OTAPOINTER=0xAFD1363A` via MMIO, inject the
frame. Result: uart2 TX
`5A A5 FF 09 24 01 03 05 02 02 06 0A 03 4B` (matches prior stock/openCFW
byte-identical reply), OTAP→0, `machine Reset` → `g2.reset` **SBL
application handoff** (not wired-load).
`DEV_BoxRevcMsgProcess` → successful product-test send →
`g2_recovery_disarm_healthy` is live in Renode.

**Unexpected reset before advertising.** `opencfw-early-reset-armed.resc`:
arm at 0.01 s (`OTAP=0xAFD1363A`, host packets 0), then `machine Reset`.
`g2.reset: SBL wired-load (OTAPOINTER=0xAFD1363A); application not entered`,
CPU halted, PC 0. **This is the intended recovery** for an app-dead /
watchdog-class reset while still armed — same signature as the post-DFU
trap before the intentional-reset disarm fix. Recovery still needs a host
on the pogo/SBL wired-load path.

**Remaining risk.** Pogo/SBL reachability and probe-bridge HELLO on real
silicon are unproven. Both dev-pair temples are already bricked on pre-arm
builds (cannot arm retroactively). Crash-loop gate still unwired. Sim still
does not reproduce the hardware early hang.

**Next.** No further high-value no-hardware item for this recovery campaign:
NVM/FD01/FD07/FC4E, mismatch DFU, intentional-reset disarm, ADV disarm,
case-reply disarm, and pre-ADV reset→wired-load are covered. Needs a
sacrificial/healthy temple flash — see hardware-test-plan §2026-11-22.

Evidence:
[`g2-20261122-case-reply-and-early-reset.json`](../evidence/g2-20261122-case-reply-and-early-reset.json).

## Disarm early OTAP before intentional software reset — 2026-11-22 (7:58 AM CST, America/Chicago)

Fixed the openCFW post-DFU OTAP/SBL trap. Emulator-only; no flash; no
commit. (3) not in this step.

**Stock also SYSRESETREQs.** After the INFO commit both stock and
openCFW logs show `nvic: Resetting platform with SYSRESETREQ`. Stock
then gets `g2.reset: SBL application handoff` because `OTAPOINTER=0`.
openCFW kept `OTAPOINTER=0xAFD1363A` from `g2_recovery_arm_early` and
landed in `SBL wired-load; application not entered` — no advertising.
That is the same signature as an app-dead temple: early arm, then any
reset before advertising/case-reply disarm, with no host on the wired
path.

**Audit.** Intentional apollo-main software resets:
`am_hal_sysctrl_aircr_reset` / `audio_ble_radio_ready_44b0ae` (post-DFU
reconfigure and many callers), `g2_log_fatal_idle` (AIRCR), and
`audio_ble_ota_reset_event` (RSTGEN SWPOR/SWPOI). Touch/case/bootloader
resets are other binaries. A reset meant to enter SBL must leave the
key armed and skip these helpers.

**Fix.** `g2_recovery_reset_app()` disarms + clears the crash-loop
streak, then AIRCR. Strong overrides of `am_hal_sysctrl_aircr_reset` and
`audio_ble_radio_ready_44b0ae` call it. `g2_log_fatal_idle` and
`audio_ble_ota_reset_event` disarm first. Relinked image
`build/g2-apollo-recovery-20261122-otap-disarm-link/.../g2-apollo-main.bin`
(reset `0x0059427d`).

**Verify.** Version-match 8 s: arm at 0.01 s (`0xAFD1363A`), disarm by
8 s (`0`), advertising `010A200101`, unsupported 0, end PC `0x543528`.
Mismatch DFU 8 s: 1× erase, 4× CRC, INFO `0xFD07`, SYSRESETREQ →
**application handoff** PC `0x0059427D` (not wired-load), OTAP=0,
advertising yes, unsupported 0. Matches stock post-DFU bring-up.

No commit. Next: (3).
Evidence:
[`g2-20261122-otap-disarm-before-reset.json`](../evidence/g2-20261122-otap-disarm-before-reset.json).

## Mismatch pair through completed DFU — 2026-11-22 (7:39 AM CST, America/Chicago)

Ran stock 2.2.6.10 and openCFW ITCM-VMA recovery on the mismatch
controller through a completed DFU and compared. Emulator-only; no
flash; no commit. (3) not in this step.

**Model fixes required for completion.** After `0xFC4E`, stock still
looped DFU because `commit_52eefa` reads `0x402000` after `NVMEraseMain`
and our FD01 treated erased holes as missing (`0x0C`). FD01 now returns
`0xFF` for unmapped main NVM `<0x00F00000`. FD07 was also wrong (LE32
address); stock `EMSMM_NVMErasePage` / `erase_info_52e948` use plen 2
`{bank_sel,page}` with INFO page 1 at `0x00402000`. Transport tests: 7
passed (55.59 s).

**DFU HCI (both).** One `NVMEraseMain`, 856 image `0xFD03` writes
covering the four CRC windows with zero gaps, four `0xFC4E` CRC32
results identical on both sides
(`0xD2C17B4C`, `0x6E09DDA8`, `0xDA9653E5`, `0xE498BC06`), one INFO
`0xFD07` erase at `0x402000`, one commit `0xFD03` write at `0x402000`,
unsupported 0, unmodeled none.

**Post-DFU divergence.** Stock continues to advertising `010A200101`,
end PC `0x44adfa`, `OTAPOINTER=0`. openCFW issues `SYSRESETREQ` right
after the INFO commit; `g2.reset` sees sticky `OTAPOINTER=0xAFD1363A`
and stays in SBL wired-load (application not entered) — no advertising,
end PC `0`. DFU image path completed; openCFW bring-up after DFU did not.

No commit. Next: (3) case-reply disarm. Follow-on gap: openCFW
post-DFU reset / OTAP SBL trap.
Evidence:
[`g2-20261122-em9305-dfu-mismatch-pair.json`](../evidence/g2-20261122-em9305-dfu-mismatch-pair.json).

## EM9305 HCI 0xFC4E CRC32 — 2026-11-22 (7:25 AM CST, America/Chicago)

Modeled vendor CRC in `~/Repo/g2-firmware-emulator` (local changes only,
no commit). No hardware flash. The mismatch DFU pair and (3) are not in
this step.

**Evidence.** `audio_ble_radio_crc_remote_52e6ac` sends `014EFC08` plus
start/end LE32 and requires Command Complete `response[6]==0` with CRC32
LE32 at `[7..10]`. Local twin `audio_ble_radio_crc_local_4d34f8` and
`nvm_bootloader.c` `crc32_nvm` use reflected poly `0xedb88320`. The prior
NVM mismatch log showed two unmodeled `014EFC0800003000E0003000` calls
(`[0x00300000, 0x003000e0)`).

**Model.** `ProcessVendorCrcCommand` for `0xFC4E`: CM required (`0x2F`
outside); `plen==8` and `end>=start` else `0x12`; CRC over `[start,end)`
from `memoryFixtures`, missing bytes as erased `0xFF`; returns status 0
plus CRC LE32.

**Verification.** Three new FC4E transport tests plus prior FD06/FD03
tests: 6 passed in 23.13 s (CM gate, written-payload CRC match
`0x55b401a7` for `aabbccdd`, erased-FF gap CRC).

No commit. Next: stock + openCFW mismatch through a completed DFU,
then (3).
Evidence:
[`g2-20261122-em9305-fc4e-crc.json`](../evidence/g2-20261122-em9305-fc4e-crc.json).

## EM9305 NVM program/erase (0xFD06 first) — 2026-11-22 (7:21 AM CST, America/Chicago)

Implemented controller NVM erase/program in
`~/Repo/g2-firmware-emulator` (local changes only, no commit). No
hardware flash. A completed DFU and (3) are not in this step.

**Evidence.** `audio_ble_radio_update_erase_52e9b4` sends `0106FD00`
and requires Command Complete `response[6]==0`.
`EMSMM_NVMEraseMain` allows the command only when the CM magic is
`0x53535353`/`0xa9a9a9a9` and `plen==0` (else `0x2f`/`0x12`).
`WriteAtAddress`/`WriteContinue` are `0xFD03`/`0xFD04`. The model maps
CM magic to the existing `configurationMode` flag from the GPIO15
`recover_stop` clock.

**Model.** `0xFD06`/`0xFD05` clear `memoryFixtures` below `0x00F00000`
(keeps RF `0x00F0xxxx`), set `NvmMainErased`. `0xFD03`/`0xFD04` write
into fixtures under CM. `0xFD07` clears a functional 4 KiB page window
(not a measured page size). `0xFD01` boot reads are unchanged.
Synthetic fixtures for prepare registers `0xF0040C`/`0xF0041C` were
added to `controller-peripherals.resc`.

**Verification.** Three transport tests passed (21.67 s): erase
outside CM returns `0x2F`; erase in CM clears the version fixture and
keeps trim; `0xFD03` write then `0xFD01` readback. An 8 s openCFW
mismatch run (`opencfw-itcm-vma.app.bin`) logged two
`NVMEraseMain` successes (`NvmMainErased=True`, `ConfigurationMode=True`),
then 1714 `0xFD03` write packets (1778 host packets total). No missing
fixtures. The remaining unmodeled opcode is `0xFC4E`
(`014EFC0800003000E0003000`) from
`audio_ble_radio_crc_remote_52e6ac` — CRC32 for
`update_current`/`update_check`. Unsupported count 2. Advertising
`010A200101` still issued; end PC `0x5432f8`. Erase+program ran; DFU
is not complete without `0xFC4E`.

No commit. Next: model `0xFC4E` CRC (and remaining finalize), re-run
the mismatch pair through a completed DFU, then (3).
Evidence:
[`g2-20261122-em9305-nvm-erase-write.json`](../evidence/g2-20261122-em9305-nvm-erase-write.json).

## ITCM VMA for .itcm_text / .ramfunc — 2026-11-22 (7:11 AM CST, America/Chicago)

Audited stock vs openCFW ITCM/ramfunc placement and fixed
`g2-apollo-main.ld` so Ambiq `.itcm_text` (and any `.ramfunc`) get an
ITCM VMA with an MRAM LMA, copied at startup. Rebuilt apollo-main and
re-ran both sims. No hardware flash. NVM is not in this step.

**Stock.** ITCM is 256 KB at `0x00000000`. The only startup copy into
ITCM is the LZ77 row at `0x75D3E0`, which installs the 24-byte
delay/memcpy helper at `0x40..0x58`. IAR `.textrw` is documented as
VMA ITCM / LMA MRAM. Stock `am_hal_delay_us` at `0x4807a0` (MRAM)
`bl`s `0x40`. `nv_program_main2` is bootrom; `am_hal_mram_*` callers
stay in MRAM and call into bootrom. The spotmgr WFI helper (when
present) copies a six-instruction WFI sequence onto the stack, not
into ITCM.

**OpenCFW before.** `g2-apollo-main.ld` merged `*(.itcm_text)` into
MRAM `.text`. The only linked contributor was `am_hal_utils.c`
(`br_util_delay_cycles`, `internal_hal_read_word`,
`internal_hal_read_words`, 0x18 B). Upstream
`am_hal_spotmgr_wfi_wait` is `.itcm_text` but the generated boot
`pcm2_2` object the build links does not contain it. No `.ramfunc`
sections appear under clang. Leaving those helpers in MRAM is a
structural risk for any path that must run while MRAM is busy or
powered down, and it was the GPIO15 delay-loop bug.

**Fix.** ITCM MEMORY at ORIGIN `0x58` (leaves `0x40..0x58` for the
stock overlay). New `.itcm_text` output section:
`*(.itcm_text*) *(.ramfunc*) > ITCM AT > MRAM`, with
`__itcm_text_{start,end}` and `__itcm_text_load_start`. Region table
gains a `g2c_copy_init3` row after the overlay copy. Restored
local-label 16-bit `bne` loops in `br_util_delay_cycles` and
`internal_hal_read_words` (GNU assembled global-symbol `BNE` as
`bne.w`). Linked image
`build/g2-apollo-recovery-20261122-itcm-vma-link/g2-apollo-main/g2-apollo-main.bin`,
3,818,888 B, SHA-256 `0bdd25a853051788b598c526465a1a770c219b1f87c5b9cf96409d9fe665a232`, SP `0x2007FB00`,
reset PC `0x0059404d`. `br_util_delay_cycles` is now VMA `0x58` / LMA
`0x007a6cd8` (`subs; bne.n; bx lr`). `am_hal_delay_us` stays in MRAM
and calls into ITCM (stock pattern). Overlay at `0x40` unchanged.

**Sim.** Version-match 8 s CHIPREV=`0x22`: 56 HCI packets, identical to
the advertising-disarm baseline, including `010A200101`; frames hash
`0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`;
OTAP arm then disarm; end PC `0x5432f8`. Mismatch 8 s: configuration
mode False→True, two enter-CM logs, `0106FD00`, 61 host packets,
advertising, end PC `0x5432f8`.

No commit. Next: NVM program/erase starting with `0xFD06`, then the
mismatch pair through a completed DFU, then (3).
Evidence:
[`g2-20261122-itcm-vma-ramfunc.json`](../evidence/g2-20261122-itcm-vma-ramfunc.json).

## GPIO15 wait_pulse delay: stock vs openCFW, ITCM loop — 2026-11-22 (7:03 AM CST, America/Chicago)

Compared the stock and openCFW `wait_pulse` / `delay_us` paths
statically, then made openCFW run the same delay spin from ITCM as
stock. Rebuilt apollo-main (incremental `am_hal_utils` + relink) and
re-ran the version-match and mismatch sims. No hardware flash. NVM is
not in this step. The SoC is Apollo510 (Ambiq MRAM/ITCM; the request
said Apollo4).

**Instruction sequence and iteration count match; the spin location
did not.** Stock `wait_pulse` at `0x52e854` and openCFW at
`0x0046ad80` both issue `(duration*1000)/33` pulses (1212 for
duration 40) of GPIO15=0, `delay_us(16)`, GPIO15=1, `delay_us(16)`.
OpenCFW uses a `umull` magic `/33` and returns early if
`duration*1000 < 33`, which is not taken here. The wrapper
`0x491102` / `g2_norflash_delay_us_491102` still delegates to
`am_hal_delay_us`. Calibration is the same in both images: read
`0x40021000` bits `[4:3]` (stock `ubfx` cmp 2, openCFW `and #24` cmp
16 — equivalent); if not high-performance, `count = us*32` and
overhead 15; if HP 250 MHz, `count = us*32*250/96` and overhead 24.
Those constants are 32.0 / 250.0 / 96.0. The 3-cycle-per-iteration
assumption is the HAL comment and `32*3 = 96` cycles/µs at 96 MHz.

**Where it executes.** Stock `am_hal_delay_us` at `0x4807a0` (MRAM)
ends in `bl 0x40`. The 24-byte ITCM helper there is
`subs r0,#1; bne; bx lr` plus a word-copy, bytes
`0138fdd17047704750f8043b41f8043b013af9d170477047` (SHA-256
`0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83`).
The Nov 11 openCFW overlay in `g2c_gnu_init.c` is byte-identical and
is copied to `0x40` by the region table, so the overlay *covers* the
stock delay loop. But openCFW `am_hal_delay_us` called
`br_util_delay_cycles` at `0x00600744` in **MRAM**:
`g2-apollo-main.ld` places `.itcm_text` in the MRAM `.text` output
section, and `BNE br_util_delay_cycles` against the global symbol
assembles as a 32-bit `bne.w`, not the overlay's 16-bit `bne`.

**Period estimate.** For `delay_us(16)` in 96 MHz LP mode, both
images request 497 iterations: stock ITCM at 3 cycles is 15.53 µs of
spin (prologue cancelled by the 15-iter overhead). In 250 MHz HP
mode, 1309 iterations, 15.71 µs. A pulse is two of those plus two
GPIO writes, nominally ~32 µs plus HAL. If openCFW's old MRAM
`bne.w` loop hit I-cache, one extra cycle would stretch each
half-pulse by about 33%. If I-cache missed or was off, uncached MRAM
wait states on a 6-byte loop would make the pulse longer, not
shorter; a 2–3× stretch is a plausible order of magnitude, not a
measured datasheet wait-state number. Renode is not cycle-accurate
for MRAM vs ITCM, so the sims below cannot prove silicon periods.

**Fix.** `br_util_delay_cycles` now tail-calls `itcm_countdown_loop`,
defined in `g2-apollo-main.ld` as `0x00000041` (Thumb entry of the
overlay countdown). The linked image is `b.w 0x40` at `0x00600744`;
calibration is unchanged. Image
`build/g2-apollo-recovery-20261122-itcm-delay-link/g2-apollo-main/g2-apollo-main.bin`,
3,818,872 B (8 B smaller than the 22 Nov recovery image), SHA-256
`8ed8fdebe3020154e7a599cfa0b46b6b72138e9d6a9291ba3e2215c78eb8921c`,
SP `0x2007FB00`, reset PC `0x0059404d`.

**Sim.** Version-match 8 s, CHIPREV=`0x22`: 56 HCI packets, byte-
identical to the 6:08 AM CST advertising-disarm openCFW run,
including `010A200101`; two display frames with hash
`0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`;
OTAP `0` → `0xAFD1363A` at 0.01 s → `0` at 8 s; end PC `0x5432f8`.
Mismatch 8 s: configuration mode False then True, two enter-CM logs,
then `0106FD00`, 61 host packets, advertising, end PC `0x5432f8`.
`recover_stop` still completes; `0xFD06` is still unmodeled.

The evidenced openCFW-vs-stock GPIO15 spin-loop difference is closed
in the image. Whether that difference (or remaining GPIO HAL /
prologue differences) caused the app-dead temples remains a
hypothesis: official 2.2.6.10 came up, and there is still no factory
trim dump or GPIO15 trace.

No commit. Next: NVM program/erase starting with `0xFD06`, then the
mismatch pair through a completed DFU, then (3) the case-reply
disarm with a pogo product-test frame.
Evidence:
[`g2-20261122-gpio15-delay-itcm.json`](../evidence/g2-20261122-gpio15-delay-itcm.json).

## recover_stop completable in the EM9305 model — 2026-11-22 (6:49 AM CST, America/Chicago)

Made `audio_ble_radio_recover_stop_52e8be` completable in
`~/Repo/g2-firmware-emulator` (local changes only, no commit). No
hardware flash. NVM program/erase is not in this step.

**What was missing.** `0x40010410` bit `0x00200000` is already GPIO
InputRead3 bit 21 — GPIO117, the EM9305 Ready line — so the status
wait did not need a GPIO-model change. `context_check` already
succeeds because the model emits vendor event `04 FF 01 01` on RESET
deassert. `recover_stop` uses the same RESET line, then pulses GPIO15
and waits with no timeout for a *different* event, `04 FF 01 03`.
GPIO15 was not wired to the controller, and the model never emitted
`03`, so the mismatch path hung in that untimed loop until the
watchdog.

**What was added.** GPIO15 is now `em9305@2`, the configuration clock
cited by `display_ble_hci_radio_recover_pulse.c` /
`recover_stop.c` and by `g2/docs/reference/findings-cross-cutting.md`.
The wiring is inferred from that protocol, not from a measured
schematic net name. `wait_pulse(40)` issues `(40*1000)/33 ≈ 1212`
high/low pairs with the microsecond delay wrapper
`audio_ble_hci_boot_delay_491102(16)`; the finding's "40 pulses" is
the duration argument, not the edge count. After eight rising edges
on GPIO15 following RESET release (a functional threshold, not a
measured silicon count) the model enters configuration mode and
enqueues `04 FF 01 03`. If the normal `04 FF 01 01` startup event is
still unconsumed, it is replaced so `recover_stop` does not first
memcmp-fail it. RESET without the clock is unchanged (`04 FF 01 01`).

**Verification.** Six transport tests passed in 29.79 s, including the
original RESET-ready `04 FF 01 01` case, enter-CM during and after
startup, and a seven-edge negative. An 8 s stock 2.2.6.10 mismatch
run (`stock-recover-stop.resc`, controller word `00010304`) logged
`EM9305 entered configuration mode after 8 GPIO15 rising edges`
twice, then left the previous two-`0xFD01` hang. Next HCI was
`0106FD00` (`0xFD06`, `audio_ble_radio_update_erase_52e9b4` /
`EMSMM_NVMEraseMain`), which is still unmodeled, plus a missing
fixture read at `0x00F0040C`. `ConfigurationMode` was False then
True; host packets 61; unsupported 3; no WDT. After the failed erase
the stack still issued `010A200101` and ended at `PC=0x44adfa`, the
same end PC as the version-match stock 8 s run. That is not a
completed DFU.

**App-dead / GPIO15 timing.** The untimed `recover_stop` wait could
explain the app-dead temples, but only on paths that enter
`recover_stop`, and only as a hypothesis. Official 2.2.6.10 came up
on the later-bricked pair, so on that silicon `recover_stop` either
was not entered or it completed under official timing. The realistic
post-official MAIN-only path is version-match: with the trim-7
fixture and a successful `context_check`, acquire skips
`recover_stop`, and that path still does not reproduce app-dead in
sim. `recover_stop` *is* entered if `context_check` returns 5, if
factory trim bits `[12:7]` are not 7, or later from
`audio_ble_radio_attempt_52edf0` (mismatch DFU). If (a) or (b) is
true on the real board, every boot including official would enter
`recover_stop`. Official came up, so the EM9305 did emit
`04 FF 01 03` for stock's GPIO15 pulse train. OpenCFW uses the same
`wait_pulse` source, but delays run from MRAM (`am_hal_delay_us` /
`g2_norflash_delay_us_491102`) rather than stock's ITCM-resident
delay. If that changes pulse width or period enough that the EM9305
never enters CM, `recover_stop` never sees `04 FF 01 03` and hangs
until the watchdog — no advertising, no case frame, matching the
brick. That is residual (iii). It is not proven: there is no factory
trim dump and no GPIO15 trace, and the sim trim-7 fixture hides the
trim-mismatch acquire path. Do not treat this as the established
brick cause.

No commit. Next: implement NVM program/erase (starting with
`0xFD06`), then re-run the mismatch pair through a completed DFU,
then (3) the case-reply disarm with a pogo product-test frame.
Evidence:
[`g2-20261122-recover-stop-completable.json`](../evidence/g2-20261122-recover-stop-completable.json).

## g2.reset macro, sticky MCUCTRL, and the 0xF04B88 loop — 2026-11-22 (6:38 AM CST, America/Chicago)

Registered a proper machine reset macro in
`~/Repo/g2-firmware-emulator` (local changes only, no commit) and
traced why the mismatch path kept re-issuing the `0xF04B88` read. No
hardware flash. The EM9305 NVM program/erase model is not in this
step.

**What stock expects from `0xF04B88`.** The first mismatch HCI packet
`0101FD05884BF00008` is `audio_ble_radio_recover_read_52f094`
(`display_ble_hci_radio_recover_commands.c`), called from
`audio_ble_radio_context_recover_52f0f8` during
`audio_ble_hci_radio_acquire_52dd94` (before the `0x00402000` version
read). It fetches eight bytes from controller address `0x00F04B88`
(`REG_RF_XO_SEQ_DIG`). From the first little-endian word `R`, stock
computes `old = ((R>>8)&0x1F)<<1 | ((R>>7)&1)` — that is bits
`[12:7]` — and compares it to the requested value `7`. The existing
fixture `synthetic-rf-trim-7` (`8003000000000000`, word `0x00000380`)
already has bits `[12:7] = 7`, so the compare matches and
`context_recover` returns without calling `recover_stop`. This read
does not loop because the fixture is wrong.

**Why the read repeated in the 60 s mismatch run.** After the matching
trim read and the version read, the mismatch path later enters
`audio_ble_radio_attempt_52edf0`, which calls
`audio_ble_radio_recover_stop_52e8be`. That routine resets the radio
on GPIO `0x5D`, pulses GPIO15, and waits with no timeout for GPIO
`0x40010410` bit `0x00200000` plus vendor event `04 FF 01 03`. The
EM9305 model never emits that event, so the wait runs until the
watchdog fires. The previous incomplete reset (no `g2.reset` macro)
then restarted the application, and acquire issued the same two
`0xFD01` reads again. The repeat is a WDT restart, not a trim retry.
Closing `recover_stop` (vendor event plus the GPIO bit) is the next
model gap before NVM erase/write can run.

**g2.reset and sticky MCUCTRL.** `G2Apollo510_AudioMcuControl.Reset()`
now preserves `CHIPREV` (`0x4002000C`) and `OTAPOINTER` (`0x40020264`):
the first is a silicon identity, the second is the SBL recovery latch.
`renode/g2-reset.resc` registers the current machine's `reset` macro
and calls `wdt HandoffAfterSystemReset`. After peripherals reset, an
unarmed `OTAPOINTER` reloads VTOR/SP/PC from the application vector at
`0x00438000`; if `OTAPOINTER` is still `0xAFD1363A`, the CPU is halted
and the application is not entered. The image is not reloaded. The
macro is included from `renode/boot.resc` and from both temples in
`renode/paired.resc`. Tests that previously required the "macro is not
registered" warning were updated:
`test_renode_boot_health.py`, `test_firmware_ble_reconnect.py`,
`test_paired_scenarios.py`.

**Verification** (`build/em9305-nor-20261122/g2-reset-handoff.resc`):
an unarmed `machine Reset` kept `CHIPREV=0x22` and
`OTAPOINTER=0x11111111`, re-entered `PC=0x5e4232` / `SP=0x2007fb00`,
and logged `g2.reset: SBL application handoff`. An armed reset kept
`OTAPOINTER=0xAFD1363A`, halted the CPU (`IsHalted=True`, `PC=0x0`),
and logged `g2.reset: SBL wired-load`. The missing-macro warning did
not appear. No commit. Next: emit the `recover_stop` vendor event and
implement NVM program/erase, then re-run the mismatch pair through a
completed DFU.
Evidence:
[`g2-20261122-g2-reset-and-f04b88.json`](../evidence/g2-20261122-g2-reset-and-f04b88.json).

## Version-mismatch paired sim, 60 virtual seconds — 2026-11-22 (6:28 AM CST, America/Chicago)

Extended the 5:55 AM CST version-mismatch Renode pair from 8 to 60
virtual seconds, with PC peeks at 0, 8, 30, and 60 s. Same inputs: stock
2.2.6.10 and the 12 Nov 2026 diagnostic openCFW main
(`opencfw.app.bin`, reset PC `0x00594005`), NOR
`69efc6d023779beec9dada757ec9fe852f9454b4b84bae6fe8421c703f35c9d1` with
official `firmware/ble_em9305.bin`, controller word forced to
`00 01 03 04` (4.3.1.0). No source or emulator change. No hardware flash.

**HCI stayed the same two `0xFD01` reads, repeated after watchdog
resets.** Stock and openCFW each emitted 10 host packets, byte-identical,
all either `0101FD05884BF00008` (read `0x00F04B88` length 8) or
`0101FD050020400004` (read `0x00402000` length 4). No new opcodes, no
unmodeled EM9305 command, no advertising enable `010A200101`, and no
program/erase HCI. The 8 s peek matched the earlier mismatch: stock
`0x42` (ITCM `am_hal_delay_us`), openCFW `0x6006f6` (inside
`br_util_delay_cycles` at `0x006006f4`). At 30 s both were still in
those same delay sites.

**Watchdog resets start after the 8 s window.** Each image took four
WDT resets in 60 virtual seconds (`wdt: Watchog reset triggered`). The
emulator then logs `No action for reset - macro g2.reset is not
registered` and only reloads the scripted CPU PC/SP, which is not a
full SoC or SBL reset. After every such restart both images repeat the
same two version-check reads and fall back into the delay. At 60 s
stock was at `0x4807be`, inside its MRAM `am_hal_delay_us` (function
starts at `0x4807a0`; the `movs r1, #15` path that `bl 0x40` into the
ITCM overlay). OpenCFW was at `0x6006f4`, the start of
`br_util_delay_cycles`. Those are equivalent mid-delay states, not an
openCFW-only hang. End-PC difference is layout plus where the 60 s
slice landed after the fourth incomplete WDT restart.

This still does not reproduce the version-match app-dead failure, and
it does not show a completed DFU. The next no-hardware item remains
implementing EM9305 NVM program/erase and the recover/reconfigure/
finalize HCI in the Renode model, then re-running this mismatch pair.
Evidence:
[`g2-20261122-em9305-mismatch-60s-renode.json`](../evidence/g2-20261122-em9305-mismatch-60s-renode.json),
working files under `build/em9305-nor-20261122/`.

## Early recovery arm: advertising-enable disarm — 2026-11-22 (6:08 AM CST, America/Chicago)

Made the early SBL recovery arm safer to ship, with evidence only. The
stronger-evidenced choice was to **keep the unconditional early arm** and
**also disarm at BLE advertising enable**. The crash-loop gate
(`g2_self_recovery_boot_check`) stays unwired: the bricked temples' reset
signature was never captured, and an early hang may never produce a
watchdog streak; replacing the early arm with that gate would drop
recovery for such a hang. The 2 Nov 2026 diagnosis and hook comments
already recommended an advertising disarm so an out-of-case temple is
not left armed. Upstream Cordio `HciLeSetAdvEnableCmd` was not edited.

`g2_recovery_disarm_on_advertising()` was added in
`system/self-recovery/self_recovery.c` (calls `g2_recovery_disarm_healthy()`
then `g2_self_recovery_mark_healthy()`). It is invoked immediately after
`HciLeSetAdvEnableCmd(1)` in the two first-party enable=1 sites:
`audio_ble_dm_adv_start_4b9e88` and `audio_ble_dm_adv_start_directed`.
The existing charging-case product-test disarm in `box_uart_mgr.c` is
unchanged. A comment in `iar_cmain.c` and
`g2/docs/reference/self-recovery-arming.md` were updated to match.

Apollo-main was rebuilt from a fresh out dir (`sources.py --payload
g2-apollo-main --jobs 4`: 2718/2718 compiled, 0 known failures) and
relinked to `build/g2-apollo-recovery-20261122-link/g2-apollo-main/`
(3,818,880 bytes, SHA-256
`9d7bcc5edf64a893c47dc49fb0f124fceea4598bf39aaaaca750df9ce4e3cac2`,
SP `0x2007FB00`, reset PC `0x0059404d`). That is 80 bytes larger than
the 12 Nov 2026 diagnostic image; the reset PC moved `0x48` from
`0x00594005`.

**Paired version-match NOR sim, CHIPREV=0x22 fixture.** The modeled
MCUCTRL `Reset()` zeroes CHIPREV, so the default sim skips the arm
(`(rev & 0xff) < 0x22`). Both stock 2.2.6.10 and the new openCFW image
ran 8 virtual seconds on the unchanged NOR
(`69efc6d023779beec9dada757ec9fe852f9454b4b84bae6fe8421c703f35c9d1`,
controller 4.4.2.0, official `firmware/ble_em9305.bin` present), with
`sysbus WriteDoubleWord 0x4002000C 0x22` after `cpu Reset`. Stock and
openCFW emitted the same 56 HCI host packets (byte-for-byte), including
advertising enable `010A200101`, and both latched two display frames with
hash `0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`.
Those HCI and frames are also identical to the 5:55 AM CST CHIPREV=0
version-match baseline (the CHIPREV fixture did not change the observed
boot path). End PCs: stock `0x44adfa` (unchanged), openCFW `0x5432f8`
(layout only; `+0x48` from the prior `0x5432b0`).

**Arm and disarm.** OpenCFW `MCUCTRL.OTAPOINTER` (`0x40020264`) was `0`
before run, `0xAFD1363A` (the recovery key) after 0.01 virtual seconds,
and `0` again after 8 seconds. CHIPREV stayed `0x22`. Stock OTAPOINTER
stayed `0` at all three peeks. Scripted CPU/watchpoint hooks failed to
log (Python names `sysbus`/`machine` are not in the hook namespace) and
were logging-only; two error pairs nevertheless coincide with the early
arm window and with the approach to `010A200101`. The peeks are the
authoritative evidence. The case-reply disarm path was not the path
exercised in this run.

No hardware was flashed. The hang is still unreproduced. Wired SBL
recovery remains unproven on hardware. Residuals (ii) real months-old
littlefs/FlashDB content and (iii) silicon GPIO15/I2C timing are
unchanged and still need user/hardware data (listed in the step return).
Evidence:
[`g2-20261122-recovery-advertising-disarm-renode.json`](../evidence/g2-20261122-recovery-advertising-disarm-renode.json),
working files under `build/em9305-nor-20261122/` and
`build/g2-apollo-recovery-20261122-link/`.

## EM9305 NOR paired-sim experiment — 2026-11-22 (5:55 AM CST, America/Chicago)

Put the official packed `firmware/ble_em9305.bin` on the modeled NOR and
ran stock 2.2.6.10 against the current source-linked openCFW main. No
hardware was flashed, and no Apollo source was changed.

The 211,948-byte official payload already has the 16-byte stock header
(`version=0x04040200`, `total_length=0x33b70`, `record_count=4`,
`erase_pages_size=29`). Stock 2.2.6.10 was booted 12 virtual seconds on a
blank MX25U25643G (56 HCI packets, advertising enable `010A200101`, ended
at `0x44adfa`) and formatted littlefs at `0x1400000` (4096-byte blocks,
3008 blocks). A host injector built from the pinned littlefs 2.10.1
sources wrote the official image to `firmware/ble_em9305.bin`; a read-back
from that filesystem matched the official bytes. NOR with the file:
SHA-256 `69efc6d023779beec9dada757ec9fe852f9454b4b84bae6fe8421c703f35c9d1`.

**Version match (the realistic post-official-2.2.6.10 MAIN-only case).**
The controller fixture stayed at bundled 4.4.2.0 (`0x00402000` =
`00 02 04 04`), equal to the file header. Stock and openCFW each ran 8
virtual seconds on that NOR, with controller and display peripherals.
Both emitted the same 56 HCI host packets (byte-for-byte), including
advertising enable `010A200101`, and both latched two display frames with
hash `0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`.
End PCs differ only by image layout (`0x44adfa` stock, `0x5432b0`
openCFW). This path does not hang and does not explain the dev-pair
app-dead failure.

**Version mismatch (forced DFU).** The controller word was set to
`00 01 03 04` (`0x04030100`) so the stock byte-wise compare would request
an update. Both images sent the same two HCI packets — vendor `0xFD01`
reads, the second being command `0x00402000` length 4 — and neither
reached advertising in 8 virtual seconds. Stock ended at `0x42` (the
ITCM `am_hal_delay_us` busy loop). OpenCFW ended at `0x6006f6`, inside
`br_util_delay_cycles` at `0x6006f4`, which is the OpenCFW tail-call of
the same delay. These are equivalent mid-delay states, not an openCFW-
only hang. The EM9305 model does not implement controller NVM
program/erase, so this campaign cannot show whether a completed update
would later diverge.

**Early-arm recovery hook (review only).** `g2_recovery_arm_early()` is
still called from `low_level_init_5e4228` in `iar_cmain.c`, and
`g2_recovery_disarm_healthy()` is still called only after a charging-case
product-test reply in `box_uart_mgr.c`. The 2 Nov 2026 diagnosis already
recorded that this arms unconditionally and would leave an out-of-case
temple armed. The safer crash-loop gate (`g2_self_recovery_boot_check`,
five consecutive watchdog resets, plus `g2_self_recovery_mark_healthy`)
is present and still intentionally unwired, because the bricked temples'
reset signature was never captured. This hook was not changed here: any
boot-path edit needs its own Apollo rebuild and paired-sim check, and
this experiment did not require a firmware fix. It is not safe to ship
as-is. Recommended next edit, when that rebuild is planned: unwire the
unconditional early arm, or also disarm at BLE advertising enable, and
keep the crash-loop gate unwired until a reset signature exists.

**FLAGS.** No source fix. Hardware boot remains unverified. Residuals
(ii) real months-old littlefs/FlashDB content and (iii) silicon
GPIO15/I2C timing are unchanged. Evidence:
[`g2-20261122-em9305-nor-paired-renode.json`](../evidence/g2-20261122-em9305-nor-paired-renode.json),
working files under `build/em9305-nor-20261122/`.

## Boot-readiness assessment — 2026-11-22 (5:19 AM CST, America/Chicago)

Tree check on Kalanis MacBook Pro (`a5e5f44e-b1aa-42a0-b2ae-84d3adf8f1fe`).
The 22 Nov 2026 request arrived from the iPhone, which does not hold the
working copy. `sources.json` SHA-256 is still
`2642826fc64847042e1eb46f4f6c6312e3f8646a3c71db34d466df14a716e37f`, the
manifest hashed by the 12 Nov 2026 current-source diagnostic. Dirty
`g2/src` mtimes are earlier than that diagnostic, so the uncommitted G2
source changes were already compiled and linked. This session did not
touch `r1/`, and it did not start another full build.

The October wave-28 leftover blocks are already C. `stock_residual_code.c`
(30 Oct 2026 bulk lift) contains `bsp_LinkLayerTimeEventCallback`
(`opencfw_em9305_stock_315658`), `EMSystem_TransmitCM`
(`opencfw_em9305_stock_305ab4`), and `QF_poolInit`
(`opencfw_em9305_stock_3111a8`). The last of those is a typed wrapper
that forwards to upstream QP/C 6.5.1 `QF_poolInit` in
`qpc-port/qf_dyn_unit.c`. Remaining EM9305 assembly is the QK SWI
context switch in `application/qk_port_swi.c` (architectural; a compiler
ISR prologue cannot express the SWI0/SWI1 frame hand-over). The manifest
still has one disabled, unlinked upstream assembler unit
(`cy_syslib_gcc.S`). The historical 17-row Apollo residual-ownership
list was closed on 11 Nov 2026.

**Compile and link (12 Nov 2026 diagnostic, still current for this
manifest).** 4,879 registered units, 4,874 enabled C units, all compiled;
strict seven-payload source link with no external binary archive and no
binary fuel-gauge library. `source_completeness_proven` is false.
Apollo-main is 3,818,800 bytes (OTA package 3,818,832). The
six-component source candidate is 4,639,776 bytes against the locked
4,301,227-byte bundle; every component and the whole bundle differ from
stock. Evidence:
[`g2-20261112-current-source-diagnostic-review-index.json`](../evidence/g2-20261112-current-source-diagnostic-review-index.json),
`build/g2-current-source-bundle-diagnostic-20261112T1130Z/link-report.json`.

**Simulator.** The 10 Nov 2026 Renode run of the then-current
source-linked Apollo-main image emitted 56 HCI host packets, including
advertising enable `010A200101`, and paused at `0x542c80`. The 2 Nov 2026
paired campaign against stock 2.2.6.10 found no reconstruction-vs-stock
divergence at any modeled interface through BLE advertising, including
fixture perturbations (EM9305 version mismatch, low battery, in-case
boot, touch/IMU bursts, and a pogo product-test frame). Littlefs on the
emulator's real MX25 model was largely excluded: the reconstruction
boots to BLE on a stock-written array. The simulator does not reproduce
the hardware hang. Recipes and exclusions:
`g2/docs/reference/boot-hang-diagnosis.md`,
`build/boot-trace/STATUS.md`,
`build/boot-trace/g2-current-20261110-renode.log`.

**Hardware is not boot-ready.** Official 2.2.6.10 was installed and
came up; openCFW main (MAIN-only containers from 31 Oct and 1 Nov 2026)
left both dev-pair temples present but application-dead: no advertising,
no case-bridge frame. RAM-init Fix 43 was necessary and is not
sufficient. Do not flash the primary pair. Present software mitigations
in the tree: Fix 43 (DTCM gap zero), Fix 51 (bounded HWID ADC poll), and
the 11 Nov 2026 ITCM `0x40..0x58` overlay copy. The early-arm SBL
recovery hook is in the tree but must not ship as-is: it arms
unconditionally and only disarms after a pogo reply, so an out-of-case
temple would stay armed. The fuel-gauge provider is a source-only
uncalibrated voltage/flow estimate, not Nordic's proprietary model.

**FLAGS.** No physical boot proof. Images are not byte-identical to
stock. The hang lives in device responses or timing the simulator does
not produce. Residuals that still cannot be closed from existing sim
evidence: (i) the EM9305 firmware-update branch, which is live on
hardware NOR (`firmware/ble_em9305.bin`) and has never been run in
Renode because the modeled filesystem lacks that file; (ii) months of
real littlefs/FlashDB content (an internal assert; low probability);
(iii) silicon-level GPIO15 pulse and I2C-settle timing under
MRAM-executed delays. Closing (i) would be a paired-sim experiment, not
another flash. Observation from a bricked temple (debug UART or SWD)
is still the only way to prove a hardware fix. This assessment does
not mark any image hardware-ready.

## Apollo boot vector candidates narrowed — 2026-11-12

An independent review checked all 15 vector-like bootloader candidates
against the locked bytes and startup references. One primary vector is
supported, 13 candidate starts are rejected, and raw `0x5304` remains
unresolved because its proposed stack address lacks a verified writable map.
The byte roles of the rejected low-stack matches and whole-boot discovery
remain open. Evidence:
[`g2-20261112-p1-apollo-boot-vector-candidates-index.json`](../evidence/g2-20261112-p1-apollo-boot-vector-candidates-index.json).
Reviewed noncanonical discovery revision 017 carries this narrowed vector
item without closing the bootloader's broader pointer and writer routes:
[`g2-20261112-p1-discovery-v17-index.json`](../evidence/g2-20261112-p1-discovery-v17-index.json).
A later review rejects raw `0x5304` as a vector start: both words are
directly loaded as literals, one is a callback pointer, and the proposed
stack address lies in a region the [Apollo510 datasheet](https://contentportal.ambiq.com/documents/20123/2877485/Apollo510-SoC-Datasheet.pdf)
marks Reserved/X rather than documented writable stack. Boot-specific
remapping and the nearby uncensused routine remain open. Evidence:
[`g2-20261112-p1-apollo-boot-vector-5304-resolution-index.json`](../evidence/g2-20261112-p1-apollo-boot-vector-5304-resolution-index.json).

## Touch flash-row copy source bounded — 2026-11-12

The 128-byte copy at touch runtime `0x8D74` takes its source from the second
argument to `Cy_Flash_WriteRow`. One local caller supplies a zeroed stack
buffer; another forwards and advances its own caller-supplied pointer. The
upstream origin of that pointer and indirect caller routes remain open, so
this does not exclude executable data from other paths. Evidence:
[`g2-20261112-p1-touch-flash-copy-origin-index.json`](../evidence/g2-20261112-p1-touch-flash-copy-origin-index.json).

A corrected and independently reviewed caller uptrace verifies the `0x4811`
callback installed from the `0x48A8` literal and two indirect EEPROM write
routes. Its 15 checked Thumb call edges lead to RAM or stack staging, with
some paths merging existing EEPROM rows. The caller-supplied `param_2`
source remains unknown, and no fixed firmware-flash source interval is
established. Evidence:
[`g2-20261112-p1-touch-flash-copy-uptrace-index.json`](../evidence/g2-20261112-p1-touch-flash-copy-uptrace-index.json).
Reviewed noncanonical discovery revision 018 carries the corrected route
description and retains seven open items:
[`g2-20261112-p1-discovery-v18-index.json`](../evidence/g2-20261112-p1-discovery-v18-index.json).
A further independently reviewed trace identifies the callback source as a
RAM EEPROM record at `0x200009D0` for both direct write callers. Startup
loads the record through the true read adapter; defaults, baseline changes,
and hold changes are staged in RAM before write. The producer of a separate
input buffer at `0x200009A1` remains unresolved. Evidence:
[`g2-20261112-p1-touch-param2-origin-index.json`](../evidence/g2-20261112-p1-touch-param2-origin-index.json).
Reviewed noncanonical discovery revision 020 incorporates this RAM-source
finding and the bounded boot vector rejection while retaining seven open
items and the boot remap caveat:
[`g2-20261112-p1-discovery-v20-index.json`](../evidence/g2-20261112-p1-discovery-v20-index.json).
An independently reviewed instruction trace identifies the separate
`0x200009A1` hold input as payload in the configured I2C receive buffer.
Command 7 dispatches through a nine-entry table to the hold setter. No
physical sender was observed, and other writers and indirect aliases remain
open. Evidence:
[`g2-20261112-p1-touch-i2c-input-producer-index.json`](../evidence/g2-20261112-p1-touch-i2c-input-producer-index.json).
Reviewed noncanonical discovery revision 021 carries the configured receive
route and keeps the unobserved sender, aliases, other writers and unrelated
copy paths open:
[`g2-20261112-p1-discovery-v21-index.json`](../evidence/g2-20261112-p1-discovery-v21-index.json).

## Apollo main function overlap classified — 2026-11-12

An independently reviewed whole-census byte audit checked all 7,449
historical Apollo main function rows. Their exact AddressSet ranges do not
overlap and cover 1,394,848 bytes; 7,448 contiguous body-envelope hashes
match locked bytes, while one oversized envelope has no exporter hash.
The 2,128,548-byte full-OTA complement remains unclassified. An envelope
hash is not a code-unit or entry-closure proof. Evidence:
[`g2-20261112-p1-apollo-main-census-byte-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-census-byte-coverage-index.json).
An attempted bulk `code` classification passed range arithmetic but failed
independent semantic review because the census lacks an instruction/code-unit
map. The reviewed coverage revision 014 remains current; those historical
function ranges retain their previous ledger classifications.
The rejection and unchanged gate status are pinned in
[`g2-20261112-p1-apollo-main-census-coverage-rejection-index.json`](../evidence/g2-20261112-p1-apollo-main-census-coverage-rejection-index.json).
The original Ghidra 12.1.2 project and listing export are absent. A reviewed
tooling investigation specifies a fresh, private Ghidra import and code-unit
export for the 7,758 historical ranges, with explicit reconciliation before
any bulk code classification. That investigation preceded the fresh export
described below. Evidence:
[`g2-20261112-p1-apollo-main-codeunit-map-investigation-index.json`](../evidence/g2-20261112-p1-apollo-main-codeunit-map-investigation-index.json).
A fresh Ghidra 12.1.4 import then exported Listing CodeUnits for all 7,758
historical ranges. Independent review reconciled 1,394,848 bytes: 1,260,803
bytes are instructions in that new listing, 134,045 are undefined, and none
are defined data. The new analysis associates 715 historical entries with no
matching current function. It is not the missing Ghidra 12.1.2 project, and
no bulk code coverage was admitted. Evidence:
[`g2-20261112-p1-apollo-main-fresh-codeunit-export-index.json`](../evidence/g2-20261112-p1-apollo-main-fresh-codeunit-export-index.json).
A conservative filter over whole instruction units with matching fresh and
historical function ownership yields 1,251,072 candidate bytes across 6,734
functions. It has no data overlap with current coverage, but instruction
encodings have not been independently verified. The candidate is indexed
without adding code rows to the ledger:
[`g2-20261112-p1-apollo-main-code-candidate-index.json`](../evidence/g2-20261112-p1-apollo-main-code-candidate-index.json).
GNU objdump independently agrees on the start and width of all 473,945
selected Thumb units across 2,465 isolated runs. This is decoder agreement,
not proof that every byte is semantically code; the candidate remains
unadmitted. Evidence:
[`g2-20261112-p1-apollo-main-code-candidate-objdump-index.json`](../evidence/g2-20261112-p1-apollo-main-code-candidate-objdump-index.json).

An independent review verifies the separate 72-byte Apollo main scatter table
at runtime `[0x75D3C8,0x75D410)`, its four callback entries, five destination
contracts and three contiguous compressed source spans. The table bytes are
data in reviewed noncanonical coverage revision 012: 107 rows across 40
scopes, 4,176,969 unknown payload bytes. The replay traces have a script-pin
drift caveat; direct locked bytes and static references support the table
classification. Physical execution and G1 remain open. Evidence:
[`g2-20261112-p1-apollo-main-scatter-index.json`](../evidence/g2-20261112-p1-apollo-main-scatter-index.json),
[`g2-20261112-p1-apollo-main-scatter-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-scatter-coverage-index.json).

Reviewed noncanonical discovery revision 014 corrects the Apollo main scope
wording: the three literal words and static scatter dispatcher route are
verified; the two adjacent raw gaps, runtime reachability, and whole-image
discovery remain open. Its six payload rows retain 33 image IDs and seven
unresolved discovery items. Evidence:
[`g2-20261112-p1-discovery-v14-index.json`](../evidence/g2-20261112-p1-discovery-v14-index.json).

A subsequent independently reviewed audit verified eight directly loaded
string-pointer words at main post-preamble raw `[143616,143648)` (full OTA
`[143648,143680)`). The 32-byte span is data in noncanonical coverage
revision 013, which has 109 rows across 40 scopes and 4,176,937 unknown
payload bytes. Discovery revision 015 removes that span from its open item;
the preceding two-byte zero halfword, full residual sweep and runtime route
reachability remain open. It retains six payload rows, 33 image IDs and seven
unresolved items. Evidence:
[`g2-20261112-p1-apollo-main-postpreamble-refs-index.json`](../evidence/g2-20261112-p1-apollo-main-postpreamble-refs-index.json),
[`g2-20261112-p1-apollo-main-postpreamble-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-postpreamble-coverage-index.json),
[`g2-20261112-p1-discovery-v15-index.json`](../evidence/g2-20261112-p1-discovery-v15-index.json).

The immediately following 44-byte main region at post-preamble raw
`[143648,143692)` contains nine string pointers and two Thumb function
pointers, with 29 direct literal loads checked at instruction boundaries.
Noncanonical coverage revision 014 classifies that exact region as data in
both views: 111 rows, 40 scopes and 4,176,893 unknown payload bytes.
Discovery revision 016 retains the same seven open items. Evidence:
[`g2-20261112-p1-apollo-main-next-pointer-cluster-index.json`](../evidence/g2-20261112-p1-apollo-main-next-pointer-cluster-index.json),
[`g2-20261112-p1-apollo-main-next-pointer-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-next-pointer-coverage-index.json),
[`g2-20261112-p1-discovery-v16-index.json`](../evidence/g2-20261112-p1-discovery-v16-index.json).

An independent review verified the locked stock function `FUN_0045adf4` by
hashing its full 766-byte body. The noncanonical P1 ledger now marks its
66-byte overlap at full OTA offsets `[143568,143634)` as code, with the same
bytes at post-preamble image offsets `[143536,143602)`. Revision 008 left
the following 14 bytes unknown. A subsequent independently reviewed audit
identified 12 of them as three directly referenced literal words at full
OTA `[143636,143648)`, leaving the `0x0000` halfword at
`[143634,143636)` unknown. Reviewed noncanonical coverage revision 011
classifies those 12 bytes in each view; it has 103 rows, 40 scopes and
4,177,041 unknown payload bytes. Main image discovery and G1 remain open.
Evidence:
[`g2-20261112-p1-apollo-main-offset-code-index.json`](../evidence/g2-20261112-p1-apollo-main-offset-code-index.json),
[`g2-20261112-p1-apollo-main-code-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-code-coverage-index.json),
[`g2-20261112-p1-apollo-main-tail-literals-index.json`](../evidence/g2-20261112-p1-apollo-main-tail-literals-index.json),
[`g2-20261112-p1-apollo-main-tail-coverage-index.json`](../evidence/g2-20261112-p1-apollo-main-tail-coverage-index.json).

Revision 011's immutable index uses an earlier filename for its four-byte
case-tail predecessor. The predecessor now has its distinct filename, and the
older 48-byte literal-pool index is restored byte-for-byte at its original
path. The historical path mismatch and corrected relationship are recorded in
[`g2-20261112-p1-coverage-path-correction-index.json`](../evidence/g2-20261112-p1-coverage-path-correction-index.json).

## Codec conditional load routes checked — 2026-11-12

An independent review verified the locked codec's static A/B reader spans,
transfer formulas, entries, and guards. A marker at `0x20033FFC` selects an
alternate transfer; B's loader also checks boot mode `2`. The actual marker
and mode values, physical XIP mapping, and an alternate destination alias are
still unverified, so the conditional inventory remains open. Evidence:
[`g2-20261112-p1-codec-conditional-route-index.json`](../evidence/g2-20261112-p1-codec-conditional-route-index.json).
A separate review confirms that the alternate A-loader plan copies B
stage-two bytes to `0x20003000` but targets entry `0x10003100`; the normal
B plan loads the same bytes to `0x10003000`. The required executable alias,
runtime guard values, and physical XIP mapping remain unproven. Evidence:
[`g2-20261112-p1-codec-alternate-destination-index.json`](../evidence/g2-20261112-p1-codec-alternate-destination-index.json).
Reviewed noncanonical discovery revision 022 carries those static route and
accelerator findings while retaining two codec and seven total open items:
[`g2-20261112-p1-discovery-v22-index.json`](../evidence/g2-20261112-p1-discovery-v22-index.json).

## Case tail data spans reviewed — 2026-11-12

The bounded whole-case residual scan reproduced all 435 historical function
body hashes and the 12,680-byte complement in 296 intervals. Exact known
executable-header signatures had no hits. A second vector-shaped pair at raw
`0x6A18` resolves to a task/thread literal pool; 95 aligned flash-looking
numbers remain candidates, including 54 that target exact census entries.
These checks do not close markerless content, the reference graph, or G1.
Evidence:
[`g2-20261112-p1-case-whole-residual-index.json`](../evidence/g2-20261112-p1-case-whole-residual-index.json).

The separate bounded descriptor audit now identifies case raw
`[0xD26C,0xD406)` as RTOS timer/task/event/reset records and consumed lookup
maps, and `[0xD93C,0xD95C)` as two startup transform records. The six raw
bytes before `0xD26C` remain unknown. The shift map is evidenced only through
`0xD406`; its following two zeros are outside that table audit. This adds
442 reviewed data bytes per case view. The noncanonical ledger revision 009
has 97 rows across 40 scopes and 4,177,057 unknown payload bytes. Evidence:
[`g2-20261112-p1-case-descriptor-tail-index.json`](../evidence/g2-20261112-p1-case-descriptor-tail-index.json),
[`g2-20261112-p1-case-descriptor-coverage-index.json`](../evidence/g2-20261112-p1-case-descriptor-coverage-index.json).

A follow-on instruction and literal audit verified raw `[0xD268,0xD26C)` as
the `0x20000090` RAM pointer loaded by `case_copy_head8_to_tail8`. Raw
`[0xD266,0xD268)` remains unknown despite fitting an alignment gap. The
reviewed noncanonical ledger revision 010 classifies only those four bytes as
data, leaving 4,177,053 unknown payload bytes across 99 rows and 40 scopes.
Reviewed discovery revision 012 narrows the case tail open item to the two
unknown bytes while retaining seven open items overall. Evidence:
[`g2-20261112-p1-case-tail-literal-index.json`](../evidence/g2-20261112-p1-case-tail-literal-index.json),
[`g2-20261112-p1-case-tail-literal-coverage-index.json`](../evidence/g2-20261112-p1-case-tail-literal-coverage-index.json),
[`g2-20261112-p1-discovery-v12-index.json`](../evidence/g2-20261112-p1-discovery-v12-index.json).

A bounded follow-up checked the two-byte case raw gap `[0xD266,0xD268)`.
The preceding function returns immediately before it, and the next word is
its directly loaded RAM-pointer literal. No direct branch to the gap appeared
in the pinned function census, but the zero halfword can encode a Thumb
instruction, so its classification remains unknown. Evidence:
[`g2-20261112-p1-case-d266-halfword-index.json`](../evidence/g2-20261112-p1-case-d266-halfword-index.json).

The earlier noncanonical P1 coverage draft revision 007 classified case raw `[0xD406,0xD93C)`
as a string-bearing region with NUL and alignment bytes, and
`[0xD95C,0xD9C4)` as the reviewed startup transform source. Descriptor and
table candidates around them, plus the final four `FF` bytes, remain unknown.
With those exact spans, revision 007 had 91 rows across 40 scopes and 4,177,565
unknown payload bytes. G1 remains `not_run`. Evidence:
[`g2-20261112-p1-case-tail-coverage-index.json`](../evidence/g2-20261112-p1-case-tail-coverage-index.json).

## Apollo startup table provenance corrected — 2026-11-12

An independent review traced bootloader raw `[143580,143600)` to runtime
`[0x4330DC,0x4330F0)` and bootloader raw `[143600,143648)` to
`[0x4330F0,0x433120)`. `0x4330F0` is both the second descriptor start and
the startup callback's return cursor. The earlier main discovery review
imported these bootloader descriptors as main evidence. In **main
post-preamble raw** coordinates, `[143580,143602)` is verified stock
function code, including the entire alleged 20-byte zero table; raw
`[143602,143648)` remains unresolved. The documented main scatter table at
`0x75D3C8` is separate. Reviewed noncanonical discovery revision 012 carries
this correction across all six payload rows and retains seven open discovery
items. This does not close main discovery or G1. Evidence:
[`g2-20261112-p1-apollo-table-provenance-index-v2.json`](../evidence/g2-20261112-p1-apollo-table-provenance-index-v2.json),
[`g2-20261112-p1-discovery-v12-index.json`](../evidence/g2-20261112-p1-discovery-v12-index.json).

## Apollo main residual marker sweep reviewed — 2026-11-12

A bounded scan of the locked Apollo main image found two `FWPK` literals that
fail the known touch and codec layouts, plus 375 zlib-like prefixes with no
complete stream under the tested decoder. It did not establish another image.
It also exposed a table claim that was subsequently traced to the bootloader.
The separate main scatter table at `0x75D3C8` remains a distinct route.
Evidence:
[`g2-20261112-p1-apollo-main-residual-index.json`](../evidence/g2-20261112-p1-apollo-main-residual-index.json).

## EM9305 residual record sweep corrected and reviewed — 2026-11-12

The current-campaign bounded ARC sweep verifies all four record bytes and
correctly places record 3 at loaded `[0x302400,0x335BC8)`. Its reviewed
936-byte INI table begins at `0x335820`; the table extent follows the
descriptor walk to the record end, not the marker alone. Linear branch and
address-word matches remain candidates because disassembly can include data.
External NVM record selection and a complete reference sweep remain open.
Evidence:
[`g2-20261112-p1-em9305-residual-index.json`](../evidence/g2-20261112-p1-em9305-residual-index.json).

## Case historical function-range complement measured — 2026-11-12

The independently reproduced historical case census covers 43,072 of 55,752
raw bytes through its listed function AddressSet ranges. Its 12,680-byte
complement spans 296 intervals and includes the known 48-byte literal pool.
The complement remains unclassified; this count is a discovery worklist, not
a claim that all listed bytes are code or that all other bytes are data.
Evidence:
[`g2-20261112-p1-case-range-partition-index.json`](../evidence/g2-20261112-p1-case-range-partition-index.json).

## Codec GXNPU structural partition reproduced — 2026-11-12

A bounded current-campaign audit verified the 9,164-byte GXNPU command span
as 212 contiguous structural records and the following 120,800-byte weight
span in the locked codec payload. The conditional BINH A/B runtime routes,
opaque-region executable content, and command semantics remain unresolved.
The audit passed independent review within that scope; G1 remains `not_run`.
Evidence:
[`g2-20261112-p1-codec-residual-index.json`](../evidence/g2-20261112-p1-codec-residual-index.json).
A later independent review round-tripped all 212 records as typed
accelerator operation commands and confirmed the adjacent weight buffer.
Vendor task structures distinguish command and weight buffers, but the
available comparator model differs from the locked artifact. The slot-6
weight binding, full operation semantics, and weight internals remain open;
the command and weight spans were not blanket-classified as passive data.
Evidence:
[`g2-20261112-p1-gxnpu-command-semantics-index.json`](../evidence/g2-20261112-p1-gxnpu-command-semantics-index.json).

## Apollo boot and touch byte classifications reviewed — 2026-11-12

The noncanonical P1 coverage draft now marks the Apollo bootloader's decoded
24-byte ITCM helper as code and its 4 KiB zero-fill output as data. It also
marks the exact 56-byte touch pin-function word array at runtime `0xB4C4` as
data in both the FWPK payload and flash-image views. Both changes passed
independent review. That revision had 83 rows across 40 scopes and left
4,179,003 payload bytes unknown; the case-tail revision above supersedes
those totals. Evidence:
[`g2-20261112-p1-apollo-touch-coverage-index.json`](../evidence/g2-20261112-p1-apollo-touch-coverage-index.json).

## Apollo boot startup output interiors triaged — 2026-11-12

An independent bounded scan reproduced the three startup output hashes. The
24-byte ITCM output linear-decodes as ten Thumb instructions; the 1,371-byte
DTCM output contains structured initialized data and opaque words; the 4 KiB
SSRAM output is all zero. Four DTCM words point into that SSRAM region, but
their consumers remain unproven. This narrows the decoded-image inventory
without closing its interior references or the full bootloader sweep. Evidence:
[`g2-20261112-p1-apollo-boot-interior-index.json`](../evidence/g2-20261112-p1-apollo-boot-interior-index.json).

## Current source snapshot compiles and links, bundle differs — 2026-11-12

The current G2 manifest registers 4,879 units; 4,874 enabled C units compile
across all seven payload groups. Every relocatable composition and the strict
seven-image final link succeeds with no duplicate strong symbols or external
binary archive. Codec KWS weights enter as a C-compiled data unit. A
six-component source candidate assembled from these images is 4,639,776 bytes
versus the locked 4,301,227-byte bundle. All six component candidates and the
whole bundle differ from stock. This diagnostic does not qualify source
coverage, all-C semantics, byte identity, or hardware boot. Evidence:
[`g2-20261112-current-source-diagnostic-review-index.json`](../evidence/g2-20261112-current-source-diagnostic-review-index.json).

## Touch and Apollo bootloader discovery drafts narrowed — 2026-11-12

Within the locked touch payload, the primary vector table is copied from flash
to SRAM at reset, and the startup descriptor copies 964 bytes of initialized
data. Four other aligned vector-like pairs are callback or context data.
Thirteen non-reset calls to the byte-copy helper now have bounded local
argument traces. One stages 56 bytes of pin-function configuration words from
`0xB4C4`; inherited caller state and later use remain unresolved. A bounded
Apollo bootloader sweep reproduced 731 in-range pointer-pattern windows and
15 vector-heuristic candidates without establishing a new nested image; those
leads and the full flash/reference sweep remain open. Independent reviews
accepted the bounded evidence and the noncanonical six-payload discovery draft
revision 010, which still lists seven unresolved discovery items. The three
Apollo boot startup outputs have separately reviewed bounded replays; their
interior references remain open. G1 remains `not_run`. Evidence:
[`g2-20261112-p1-discovery-v10-index.json`](../evidence/g2-20261112-p1-discovery-v10-index.json).

## Case historical function census reproduced — 2026-11-12

The current campaign independently verified all 435 historical case function
body hashes against the locked case payload, using the Ghidra exporter's
contiguous first-to-last byte hash rule. Each recorded AddressSet range total
also matches its `body_bytes`. A listed-range Thumb scan returned 119
candidate functions with indirect transfers or selected startup behavior.
These are leads, not a complete call, writer, or nested-image census. The
case whole-image reference sweep and G1 remain open. Evidence:
[`g2-20261112-p1-case-whole-reference-index.json`](../evidence/g2-20261112-p1-case-whole-reference-index.json).

## Case residual scan and literal pool reviewed — 2026-11-12

A bounded scan of the locked case image found no additional exact `EVEN`,
`FWPK`, `BINH`, ELF, `MZ`, or `FWMH` markers. An aligned vector heuristic
found the primary vector at raw offset 0 and a second vector-like pair at
`0x6A18`. The latter is part of a twelve-word PC-relative literal pool:
the apparent stack pointer and reset address are loaded as ordinary data.
The reviewer checked the wrapper checksum and both Thumb load instructions.
The full nested-image/reference sweep remains open.

All 22 listed Thumb load sites for that 48-byte pool now match the locked
instructions and word values. The noncanonical coverage draft classifies
raw case `[0x6A10,0x6A40)` and wrapped payload `[0x6A30,0x6A60)` as `data`.
It has 79 rows across 40 scopes and 4,179,059 unknown payload bytes; G1
remains `not_run`. The discovery and coverage evidence are indexed in
[`g2-20261112-p1-case-discovery-ledger-index.json`](../evidence/g2-20261112-p1-case-discovery-ledger-index.json)
and
[`g2-20261112-p1-case-literal-coverage-index.json`](../evidence/g2-20261112-p1-case-literal-coverage-index.json).

## EM9305 NVM bootloader metadata checked — 2026-11-12

The second small EM9305 NVM record ends in a 12-byte `INI\x02` table at
package offsets `[992,1004)` (loaded `[0x300684,0x300690)`). It contains
only a zero terminator and creates no RAM child image. Bounded ARC
disassembly also shows the record-0 entry calling code in record 1. An
independent review checked the exact bytes and coordinates; its first
coverage review miscounted child-image bytes as payload bytes, and the
corrected review uses payload scopes only.

The current noncanonical coverage draft classifies those 12 payload bytes
as container, leaving 4,179,107 unknown payload bytes across 75 rows and
40 scopes. The discovery draft still has seven open items, including full
EM9305 code/data and reference sweeps. A separate full linear disassembly
census of the two small records found 72 printed direct control references:
seven from record 0 to record 1, eleven in the reverse direction, and one
external target. Raw GNU disassembly emitted `.word` for four record-1
instructions, and one register jump needs target analysis. The census does
not close the sweep or admit G1.
Evidence and corrected review hashes are indexed in
[`g2-20261112-p1-em9305-small-record-index.json`](../evidence/g2-20261112-p1-em9305-small-record-index.json).
The disassembly census and its bounded review are indexed in
[`g2-20261112-p1-em9305-small-record-census-index.json`](../evidence/g2-20261112-p1-em9305-small-record-census-index.json).
A pinned reproduction script and independent rerun of both full record
disassemblies are indexed in
[`g2-20261112-p1-em9305-small-record-census-repro-index.json`](../evidence/g2-20261112-p1-em9305-small-record-census-repro-index.json).
A further independent review places three of the four undecoded record-1
words immediately after decoded delayed branches and the fourth at a target
of two decoded branches. They remain executable candidates with unknown ARC
instruction semantics, distinct from the `INI` metadata tail. External NVM
selection and G1 remain open. Evidence:
[`g2-20261112-p1-em9305-small-word-flow-index.json`](../evidence/g2-20261112-p1-em9305-small-word-flow-index.json).
An earlier reviewed index incorrectly assigned three LOG2 mnemonics and left
the fourth unnamed. Its audit applied an opcode-unmangling path disabled in
the pinned Binutils build. Preserve its raw bytes and offsets, but its
per-word mnemonic assignments are superseded. Historical evidence:
[`g2-20261112-p1-em9305-arc-extension-words-index.json`](../evidence/g2-20261112-p1-em9305-arc-extension-words-index.json).
A new independent review checked the locked words against exhaustive GNU ARC
assembler operand matrices, the vendor APEX declarations, and the vendor
`COMMON_hw_crc32` ELF. The four words are `crc32b r3,r3,r12` at `0x30041C`,
`crc32 r3,r3,r2` at `0x30042E`, `crc32b r3,r3,r2` at `0x30043C`, and
`bswp32 r1,r3` at `0x300440`. The first three bytes sequences match the
vendor ELF; its 72-byte function differs from stock at only two byte
offsets. Exact hardware effects, external NVM selection, whole-record
coverage and G1 remain open. Correction evidence:
[`g2-20261112-p1-em9305-apex-encoding-correction-index.json`](../evidence/g2-20261112-p1-em9305-apex-encoding-correction-index.json).
An independent address-aligned comparison with the vendor DI04 ELF found
14 function symbol ranges in its 620-byte `.text` section. Five function
slices match the locked record byte for byte. The vendor section layout
diverges at `0x30066C`: stock linear instructions continue through
`0x300682`, while the vendor ELF uses `.initdat` starting there. Vendor
boundaries for differing stock code are therefore only leads. The stock
empty `INI` table begins at `0x300684`; external NVM selection and G1 remain
open. Evidence:
[`g2-20261112-p1-em9305-vendor-elf-boundary-index.json`](../evidence/g2-20261112-p1-em9305-vendor-elf-boundary-index.json).
The five byte-identical function slices also pass a separate stock
instruction check: 178 bytes are gap-free instructions with no data directives
or padding in the pinned linear disassembly. Reviewed noncanonical coverage
draft 016 classifies those bytes as code in both the EM9305 payload and
record-1 image ledgers. It retains 40 complete ledger scopes and 127 rows;
4,176,715 payload bytes and 5,671,365 image-view bytes remain `unknown`.
This is bounded classification, with no canonical admission or G1 pass.
Evidence:
[`g2-20261112-p1-em9305-exact-code-coverage-index.json`](../evidence/g2-20261112-p1-em9305-exact-code-coverage-index.json).
An independently rerun ARC object with the vendor CRC and byte-swap
extension declarations now decodes the entire 644-byte record-1 pre-`INI`
span into 249 contiguous, byte-matching instruction units. It closes the
earlier four decoder gaps in this bounded linear listing. The temporary
`.incbin` wrapper is analysis-only; linear decoding does not prove every byte
is executable or reachable. Evidence:
[`g2-20261112-p1-em9305-record1-extmap-index.json`](../evidence/g2-20261112-p1-em9305-record1-extmap-index.json).
The current campaign independently rechecked the locked `FHDR` execution
field at payload offset `1004+30`: it points to `0x302028`. The 10-byte
record-2 entry sets SP to `0x80F978` and branches directly to `0x30ED80`,
which lies in record 3 and begins with a decoded `enter_s`. Record 0 contains
a bounded call path through `getMainFunction` and `jumpToFunction`; actual
boot-ROM selection and device-state header choice remain unverified. This
supersedes the earlier `not_qualified` entry-decode status for this static
route only. Evidence:
[`g2-20261112-p1-em9305-header-execution-route-index.json`](../evidence/g2-20261112-p1-em9305-header-execution-route-index.json).
Reviewed noncanonical discovery revision 023 incorporates these EM9305
findings while retaining seven unresolved items across the six payloads.
It does not claim runtime selection of this route or exhaustive image
discovery. Evidence:
[`g2-20261112-p1-discovery-v23-index.json`](../evidence/g2-20261112-p1-discovery-v23-index.json).

## EM9305 entry and startup table checked — 2026-11-12

The locked 10-byte ARC NVM entry sets SP and branches to the application
boot loop. Stock ARC disassembly then identifies the `INI` table at
`0x335820..0x335BC8`: three positive copy rows match all three current
RAM child byte slices, one negative row describes 19,840 generated zero
bytes, and a zero sentinel ends at the application record's EOF. The first
copy and zero row depend on a runtime input; physical execution was not
observed. An independent review checked the coordinates, instruction path,
copy routine, hashes and branch conditions.

The EM9305 discovery item now names the remaining sweep of records 0 and 1
and application bytes outside that table. The six-payload draft still has
seven open items and no canonical G1 admission. Evidence and review hashes
are indexed in
[`g2-20261112-p1-em9305-startup-index.json`](../evidence/g2-20261112-p1-em9305-startup-index.json).

## Apollo zero-fill startup selection reviewed — 2026-11-12

The locked Apollo main and bootloader reset vectors enter image-local stack
setup, then startup code that calls a guard returning 1 and selects the
scatter-table runner. Each first table callback resolves by signed displacement
to its stock zero-fill handler. The two records per image match the previously
reviewed generated RAM zero spans. An independent review checked the reset
chain, table bounds, callback targets and zero-span accounting.

The current six-payload discovery draft now has seven explicit open items,
down from nine. Both Apollo residual flash/reference sweeps remain open, and
the draft is still noncanonical. This static path does not establish physical
boot, G1 admission or complete pseudocode. The report, review, draft and
hashes are indexed in
[`g2-20261112-p1-apollo-zero-startup-index.json`](../evidence/g2-20261112-p1-apollo-zero-startup-index.json).

## KWS command handoff checked in stock instructions — 2026-11-12

The locked BINH-A XIP loader selects the exact 9,164-byte command span at
type2-local offset `0xF804`. Stock C-SKY instructions pass its destination
through the saved task at `0x2002E85C`; a later SRAM caller carries task
word `+0x14` into the SNPU descriptor at `+0x40`. The indirect flash-read
callback's successful execution and the engine's downstream behavior were
not observed. An independent review checked the offsets and byte slices.

The command span remains `unknown` in the P1 coverage draft because its full
accelerator instruction extent and semantics are not established. This is
bounded inventory evidence, not G1 admission or pseudocode completion. The
report, corrected review and exact input hashes are indexed in
[`g2-20261112-p1-kws-command-execution-index.json`](../evidence/g2-20261112-p1-kws-command-execution-index.json).

## Six-payload discovery draft and codec weight classification — 2026-11-12

A new-campaign discovery draft lists all 33 current image IDs across the six
locked payloads and binds current wrapper, record, signature and replay
evidence. That revision carried nine explicit discovery open items. Independent bounded
reviews confirmed the EM9305 record/child coordinates, the touch wrapper's
two CRC-32C checks, rejection of two Apollo-main `FWPK` byte-pattern hits
under the known formats, and the four Apollo zero-init table records. The
zero-fill spans are generated RAM state, not encoded firmware images.

The codec coverage candidate now classifies the exact 120,800-byte trained
KWS weight span as data. The 9,164-byte GXNPU command span remains `unknown`
in this ledger: its 212 record boundaries and bytes are established; a separate
stock-instruction review confirms its task handoff, while full accelerator
instruction extent and control semantics remain unresolved.
The candidate has 72 rows across 40 scopes and 4,179,119 unknown payload
bytes, down by 120,800 from the prior draft. The discovery and coverage
reviews are bounded; neither draft is canonically admitted, and G1–G6 remain
`not_run`. Evidence and exact hashes are indexed in
[`g2-20261112-p1-discovery-and-codec-ledger-index.json`](../evidence/g2-20261112-p1-discovery-and-codec-ledger-index.json).

## GXNPU command structure checked for the P1 analysis plan — 2026-11-12

The local gxDNN decoder walks the locked codec's 9,164-byte KWS command
stream as 212 contiguous typed records, without a raw fallback, and
re-encodes the exact stock bytes. An independent raw-header walk reproduces
the boundaries and per-command hashes; 26 focused decoder/source tests pass.
One record has an explicit link and 83 headers preserve bits with unresolved
meaning. Geometry/control semantics, weight interpretation, execution effects
and the full C-SKY decoder sweep remain open.

A revised six-payload architecture-plan candidate now describes this local
structural decoder and the bounded C-SKY disassembly/manual-recovery route.
Its independent review accepts the plan only within that scope. Neither the
decoder evidence nor the plan is canonical G1 admission. Receipts, the 212-row
boundary ledger and review hashes are indexed in
[`g2-20261112-p1-gxnpu-structural-decoder-index.json`](../evidence/g2-20261112-p1-gxnpu-structural-decoder-index.json).

## Current-campaign image and coverage record drafts reviewed within bounded scope — 2026-11-12

A 33-row image draft now points to the current-campaign byte materializations.
It explicitly marks inherited architecture, mapping, container, entry and
transform interpretations as unreviewed; historical decoded-transform
receipts are provenance only. A separate 70-row coverage draft partitions
the package, six payloads and 33 image scopes. Independent bounded reviews
verified the draft image bytes and lineage, all 40 interval partitions,
140 evidence file hashes and the 4,299,919 unknown *payload* bytes.

Additional bounded reviews checked codec FWPK record CRCs and its 13 nested
image byte lineages, plus touch/case wrappers and startup copies. The codec
NPU command stream still needs accelerator instruction classification, and
none of these checks proves exhaustive image discovery or all runtime load
mappings. The schema-v2 inventory validator passes 40 local adversarial tests,
but the active campaign lacks canonical reviewed inventory records and its
trusted review registry. These drafts have no admission or G1 gate effect.
Artifacts and exact review hashes are indexed in
[`g2-20261112-p1-inventory-draft-review-index.json`](../evidence/g2-20261112-p1-inventory-draft-review-index.json).

## All 33 historical image outputs materialized in current campaign — 2026-11-12

The new campaign now has byte-exact local outputs for all 33 image IDs in the
historical P1 inventory: 19 other identity slices, seven EM9305 identity
slices, and seven freshly replayed decoded images. The 19 other identity
slices were independently checked against locked payloads and recursive
parent spans. The aggregate index verifies every output size and hash against
the historical row and rejects missing or duplicate IDs.

These checks establish bounded byte lineage, not discovery completeness,
all runtime load mappings, code/data classification, or canonical inventory
admission. G1–G6 remain `not_run`. The output paths and review pins are in
[`g2-20261112-p1-all-image-materializations-index.json`](../evidence/g2-20261112-p1-all-image-materializations-index.json).

## EM9305 stock record package and image bytes checked — 2026-11-12

The active campaign parsed the locked 211,948-byte EM9305 payload directly.
Its four contiguous file records, 124-byte metadata block, 29 erase-sector
IDs, sparse target addresses, and package EOF closure agree with the current
record parser and a byte-exact package rebuild. The 40-byte FHDR fields and
both CRCs reproduce from the stock bytes. Its firmware CRC covers a 10-byte
entry, six erased bytes within record 2, a 968-byte inter-record erased gap,
and the 210,888-byte application record.

Four record images and three nested initialized-RAM byte slices were
materialized under the new campaign. Their source slices and hashes passed a
corrected independent bounded review. The RAM destination mappings remain
historical candidates, and the ARC entry instruction semantics and discovery
completeness are not established by this review. These are image candidates,
not canonically admitted inventory records. G1–G6 remain `not_run`. Evidence,
review and materialization hashes are indexed in
[`g2-20261112-p1-em9305-record-index.json`](../evidence/g2-20261112-p1-em9305-record-index.json).

## All seven historical decoded image outputs replay in the new campaign — 2026-11-12

Fresh stock-handler executions against the locked case, Apollo bootloader,
and Apollo main payloads reproduce all seven historical decoded-image hashes.
The case replay yields 420 initialized RAM bytes and a 10,980-byte zero-fill
region with the same source-read and destination-write observations. The
bootloader replay reproduces its 24-, 1,371-, and 4,096-byte images under both
zero and `0xA5` RAM prestates. Apollo main reproduces its 24-, 17,752-, and
769,646-byte outputs, with observed complete source-load sets and destination
writes for the two large RAM transforms. Four corrected independent reviews
accept these as bounded replay evidence.

The executions inherit some historical descriptor and parameter selection and
use Unicorn rather than device execution. Their outputs are still candidates,
not newly admitted canonical image records. G1–G6 remain `not_run`. The
current-campaign receipts, exact source/output hashes, review decisions and
limits are indexed in
[`g2-20261112-p1-decoded-image-replay-index.json`](../evidence/g2-20261112-p1-decoded-image-replay-index.json).

## Current P1 bounded reviews narrow the G1 work — 2026-11-12

The historical G1 registry still hashes all 125 reviews, but 23 have 40
changed input references; the other 102 have current matching input files.
The current ARM, ARC and C-SKY objdump binaries match their historical hashes
and versions. Static comparison finds the selected outer EVENOTA validator
functions unchanged, while the parser file as a whole changed. Installed
Ghidra 12.1.4 has a C-SKY processor module but its CK804EF semantics remain
unqualified. A corrected architecture-plan candidate records that distinction.

Independent bounded reviews checked four root images and 18 historical
coverage intervals against the locked bytes and current references. The
primary image spans, mappings and vector facts remain supported; the case
alternate-bank alias is generic and target-specific placement in that bank
remains unproven. The 18 interval classifications remain supported, with no
claim about the unknown payload contents. The architecture-plan correction
passed its narrow review, but the full plan and new-campaign review registry
still need canonical validation. G1–G6 remain `not_run`. Evidence and exact
review hashes:
[`g2-20261112-p1-bounded-review-integration.json`](../evidence/g2-20261112-p1-bounded-review-integration.json).

## Historical P1 image and coverage records are byte-checked for reuse — 2026-11-12

The active campaign independently checked all 33 historical image records
against the locked payload bytes and their parent-image slices. All 26 identity
transforms match exactly. Seven decoded outputs and their saved receipt
source/output pins match; the decode executions have not been replayed. Four
image evidence references to `g2/docs/reference/memory-map.md` are stale.
The 70 historical coverage intervals partition the bundle, six payloads, and
33 images without gaps or overlaps, and their 140 evidence file hashes still
match. The ledger classifies 4,299,919 of 4,300,283 payload bytes as unknown.
These are reuse candidates, with no canonical admission or G1 gate effect.
The current full P1 validator stops on the old campaign because its
outer-container receipt pins an earlier `open_cfw.py` hash; it has not passed
the later checks against that historical record. The bounded new-campaign
revalidation attempt is saved under
`g2/build/pseudocode-first/20261112T092142Z/receipts/historical-g1-revalidation.json`.
The new campaign still needs reviewed mapping, discovery, analysis-plan, and
classification records. Evidence:
[`g2-20261112-historical-image-reuse-audit.json`](../evidence/g2-20261112-historical-image-reuse-audit.json),
[`g2-20261112-historical-coverage-reuse-audit.json`](../evidence/g2-20261112-historical-coverage-reuse-audit.json).

All six old discovery records still enumerate the same 33 image IDs, and
their evidence file hashes match. Six old architecture plans also match the
locked target and payload set, but 18 of their source-document evidence
references are stale across `memory-map.md`, `firmware-formats.md`, and
`docs/tooling.md`. Their content and reviews need a fresh campaign decision.
Evidence:
[`g2-20261112-historical-plan-reuse-audit.json`](../evidence/g2-20261112-historical-plan-reuse-audit.json).

The old G1 review registry still hashes all 125 review records. Across 979
input references, 102 reviews have no stale inputs.
Twenty-three reviews have 40 stale inputs: one architecture-plan review,
18 coverage reviews, and four root-image reviews. The changed inputs are
`docs/tooling.md`, `firmware-formats.md`, `memory-map.md`, and
`g2/tools/open_cfw.py`. Historical reviewer identities and pass decisions do
not establish new-campaign independent review. Evidence:
[`g2-20261112-historical-g1-review-reuse-audit.json`](../evidence/g2-20261112-historical-g1-review-reuse-audit.json).

## New G2 campaign authenticates its target, P1 remains open — 2026-11-12

Campaign `20261112T092142Z` now has a fresh identity and outer-container
preflight: the locked 4,301,227-byte bundle, six payloads, six TOC entries,
headers, CRCs and exact EOF closure revalidate with the current parser. The
current package verifier reproduces the locked hash. A later tracked change to
the provenance document's licensing footer explains why that document no
longer matches its historical target-lock pin; the firmware hashes within it
are unchanged. The target lock itself was not changed. This preflight does not
pass G1: nested-image accounting, byte classifications and independent reviews
still need new-campaign validation. Evidence:
[`g2-20261112-campaign-identity-preflight.json`](../evidence/g2-20261112-campaign-identity-preflight.json).

## Touch reset P2 evidence revalidated, corpus gate remains open — 2026-11-12

The interrupted campaign's independent review of the touch reset body
`0x4674..0x46dc` remains hash-consistent: all 20 cited input files match their
recorded hashes, and its 47 contiguous instruction records reproduce the 104
bytes at the corresponding offsets in the locked touch payload. This is a
bounded reusable pseudocode candidate; it has not been promoted into a new
canonical corpus. The G1 ledger still classifies 4,299,919 of 4,300,283
payload bytes as unknown and no payload bytes as reviewed code. G2–G6 remain
unrun. Evidence:
[`touch-reset-p2-reuse-audit-20261112.json`](../evidence/touch-reset-p2-reuse-audit-20261112.json).

The case `0x080002d6` P2 candidate also still matches its 58 stock bytes and
all 39 candidate artifact pins. Three source-document input hashes have since
changed, and its historical review is explicitly scoped and unadmitted. It
needs a new scoped review before reuse in a new corpus. Evidence:
[`case-02d6-p2-reuse-audit-20261112.json`](../evidence/case-02d6-p2-reuse-audit-20261112.json).

## EM9305 scan, auxiliary field and cycle callbacks have single owners — 2026-11-12

The native `0x31ec40` scan callback and `0x323bac` auxiliary-field encoder now
use their standalone C bodies; duplicate controller bodies were removed. The
retained scan callback preserves the stock channel and mask load order, and
the encoder calls the stock current-channel getter. Native `0x32b618` is a
branch to `0x32b9a4`, but the stock setup registers both addresses. The C
registration now uses the tail stub and one retained callback body as distinct
functions. An unlinked alternate `0x31e4a0` state-machine body was also
removed, leaving its existing linked implementation.

The full G2 build compiled 4,874 enabled units in all seven payload groups
without failures or duplicate strong symbols. The source bundle link used no
external binary archive and emitted a 4,639,776-byte candidate, SHA-256
`ae32d5125ede926d22f5a221558340d18a236c91220c307bc9064530d8a5e086`.
It differs from the 4,301,227-byte locked OTA. The focused EM9305 build
compiled 768 of 768 units and linked a 246,040-byte candidate package, 520
bytes smaller than the prior focused candidate and different from the
211,948-byte official image. Four three-variant exact-body probes compiled but
selected no new stock-exact regions; some lacked native symbol anchors or
isolated bindings. The manifest still marks five units `build:false` and 121
units `link:false`, including alternate candidates and probes. Whole-firmware
source completeness and hardware behavior remain unproven. Evidence:
[`em9305-scan-aux-cycle-single-owners-20261112.json`](../evidence/em9305-scan-aux-cycle-single-owners-20261112.json).

## EM9305 event, allocator and PHY guard have single owners — 2026-11-12

The duplicate `0x30e858` LL event, `0x316c58` connection allocator, and
`0x332f80` PHY capability guard now have one source body each. The retained
allocator follows the stock 912-byte halfword multiply and final base reload.
The retained event body uses explicit volatile stores for the stock event
layout and store order.

The full G2 build compiled 4,876 enabled units across all seven payload groups
without failures or duplicate strong symbols. Its source-only OTA candidate is
4,640,700 bytes, SHA-256
`c3de8d22e77ea9cca8ab78e192e11ab542ad0f9cb6e34db45b7b8726254c3eef`,
which differs from the 4,301,227-byte locked artifact. The EM9305 package is
246,964 bytes, 960 bytes smaller than the prior candidate. The event is still not
stock-exact: three compiler variants yielded a 34-byte body against the
32-byte stock span. A controller qualification pass found 11 exact regions,
all already in the main source plan. The official EM9305 image remains
211,948 bytes; complete source ownership and hardware behavior remain
unproven. Evidence:
[`em9305-phy-event-allocator-single-owners-20261112.json`](../evidence/em9305-phy-event-allocator-single-owners-20261112.json).

## EM9305 queue and scan paths gain single source owners — 2026-11-12

Seven further EM9305 stock addresses now have one C source owner. The
procedure-pending check at `0x307434` uses the source-owned stock table; the
`0x307cb8` state getter, three queue helpers, and the `0x322884` event release
path no longer have duplicate bodies. The retained `0x325740` scan cleanup
advances its second queue pointer by 48 on each iteration, matching the stock
disassembly; the removed copy repeatedly used the same queue.

The full G2 source build compiled 4,878 enabled units across seven payload
groups with no failures or duplicate strong symbols. The source bundle target
linked all seven groups and emitted a 4,641,660-byte OTA candidate, SHA-256
`97a369da6e4ee510580fd3cf863d97cf5ed66cf1edcf91ff72c1175b888ad216`.
It differs from the 4,301,227-byte locked OTA. The EM9305 component package
is 247,924 bytes, 340 bytes smaller than the prior source candidate, and
differs from the 211,948-byte official image. Full source ownership, hardware
behavior, and G2 gates G2–G6 remain unproven. Evidence:
[`em9305-queue-scan-single-owners-20261112.json`](../evidence/em9305-queue-scan-single-owners-20261112.json).

## Four EM9305 native addresses have single source owners — 2026-11-12

Four EM9305 native addresses had duplicate C implementations. The unused
`0x317498` buffer-clear function and `0x3245ec` callback wrapper were removed;
their referenced implementations remain. All callers of the `0x3027f4`
64-bit logical shift now use one `(low, high, count)` function declaration and
source body, matching the stock register argument order. The duplicate
`0x310230` signed power clamp was also removed, and all its callers use the
retained one-argument body.

The full G2 build after the first removal compiled 4,880 enabled units and
composed all seven payload groups without failures or duplicate strong symbols.
The final focused EM9305 build compiled 774 units without failures or duplicate
strong symbols, and its strict source link produced a 248,264-byte candidate
package with no external binary archive. That package is 172 bytes smaller
than the previous source candidate but is not identical to the 211,948-byte
official EM9305 image. Source completeness, hardware boot, and G2 gates G2–G6
remain unproven. Evidence:
[`em9305-single-source-owners-20261112.json`](../evidence/em9305-single-source-owners-20261112.json).

## Codec optimization and EM9305 ARC calls qualify — 2026-11-12

An optimization sweep over the 88 UART stage-2 C units found six additional
stock-exact codec functions: five compiled with `-Os` and one with `-Og`.
They add 200 source-built bytes. `-Oz` is unsupported by the pinned C-SKY GCC
6.3 compiler and did not produce candidate objects. The hybrid now sources
1,216 codec bytes and retains 201,756 codec bytes as binary pull-through.
Evidence: [`codec-uart-stage2-optimization-exact-c-20261112.json`](../evidence/codec-uart-stage2-optimization-exact-c-20261112.json).

ARC qualification now compiles EM9305 C with individual function sections and
links relocation-bearing functions only to inventoried stock targets. All 775
candidate units compiled; 13 new callers and function pointers matched their
complete stock bodies, adding 64 source-built bytes. The hybrid now sources
182 EM9305 bytes and retains 211,586 bytes as binary pull-through. The locked
OTA hash still depends on that pull-through. The G2 workflow's whole-firmware
pseudocode and source-completeness gates remain unrun. Evidence:
[`em9305-arc-relocation-exact-c-20261112.json`](../evidence/em9305-arc-relocation-exact-c-20261112.json).

## Codec UART stage 2 resolves exact C-SKY calls — 2026-11-12

The qualifier now links isolated C-SKY functions with call relocations only
when each source symbol's four-digit address suffix is also listed as a callee
in the authenticated stock caller corpus. Six existing C functions from five
UART stage-2 units match their complete stock bodies after that link, adding
134 source-built bytes. The hybrid now sources 1,016 codec bytes and retains
201,956 codec bytes as binary pull-through. Its OTA hash matches the locked
artifact through that pull-through.

The selected callers still bind to stock callee addresses. Their dependency
closure, the complete source-only codec, and hardware boot are not verified.
Full passes over the 27 stage-1 and 88 stage-2 UART C units compiled every
unit and found no additional exact regions under the current anchors and
compiler settings.
Evidence: [`codec-uart-stage2-relocation-exact-c-20261112.json`](../evidence/codec-uart-stage2-relocation-exact-c-20261112.json).

## Codec UART stage 2 gains exact C-SKY regions — 2026-11-12

The UART stage-2 C units use four-digit virtual-address suffixes, which the
qualifier previously missed. The stage-specific selector now expands those
suffixes under the `0x10000000` UART base and still requires an authenticated
corpus body hash, exact function size, no relocations, and full compiled-byte
equality at the stored offset. Seven functions from five existing C units
qualified, adding 174 source-built bytes. The hybrid now sources 882 codec
bytes and retains 202,090 codec bytes as binary pull-through.

The rebuilt hybrid has the locked OTA hash through that pull-through. The
source-only OTA, remaining stage-2 functions, and hardware behavior remain
unverified or nonidentical. Evidence:
[`codec-uart-stage2-short-suffix-exact-c-20261112.json`](../evidence/codec-uart-stage2-short-suffix-exact-c-20261112.json).

## Codec KWS weights now come from compiled C — 2026-11-12

The authenticated 120,800-byte non-executable KWS weight asset is represented
as a C `uint32_t` data unit under `g2/src/codec/npu/`. The G2 source manifest
compiles it with C-SKY GCC but keeps its section separate from the codec
executable image. `make source-bundle` extracts the named immutable section
from that verified object and checks its full SHA-256 against the existing
stock-derived provenance. The original binary remains a verification
reference, not an input to this source-bundle path.

The full G2 build compiled 4,881 enabled units with no failures or duplicate
strong symbols, and all seven strict source groups linked. The C-weight BINH A
and complete source-candidate OTA are byte-identical to a reference build
using the authenticated binary weight asset. The source candidate remains
4,642,172 bytes, SHA-256
`6ab074068ce35fc4bcd83c1aae89fc4f25140edf8c8f8203d83361c1c05ec9dc`,
which differs from the locked 4,301,227-byte OTA. Model training provenance,
recognition behavior, whole-firmware source completeness and hardware boot
remain unproven. Evidence:
[`codec-kws-weights-compiled-c-20261112.json`](../evidence/codec-kws-weights-compiled-c-20261112.json).

## Codec A stage 1 gains exact C-SKY regions — 2026-11-11

The BINH A stage-1 inventory offsets were independently checked against the
locked FWPK bytes. Three relocation-free functions from two existing C units
match their complete stock spans: `__reg_set_val`,
`__module_get_div.isra.1`, and the bus-wait helper. They add 62 source-built
bytes. The rebuilt hybrid now sources 708 codec bytes and retains 202,264
codec bytes as binary pull-through. Its locked OTA hash still depends on that
pull-through.

Most stage-1 code, relocation-bearing functions, model weights, full source
ownership, and hardware boot remain unproven. Evidence:
[`codec-a-stage1-exact-csky-c-20261111.json`](../evidence/codec-a-stage1-exact-csky-c-20261111.json).

## Codec UART stage 1 gains exact C-SKY regions — 2026-11-11

The UART boot-stage corpora were mapped to their separate stored spans in the
authenticated codec FWPK. A full pass compiled 115 existing UART C units.
Seven stage-1 functions from three units then qualified by exact inventory
name, full stock-body size, relocation-free compiler output and complete byte
equality at their anchored offsets. They add 186 source-built bytes. The
hybrid now sources 646 codec bytes and retains 202,326 codec bytes as binary
pull-through; the locked OTA hash still depends on that pull-through.

No UART stage-2 function qualified in this pass. C-SKY instruction/data
classification, relocation-bearing functions, model weights, full source
ownership and hardware boot remain unproven. Evidence:
[`codec-uart-stage1-first-exact-csky-c-20261111.json`](../evidence/codec-uart-stage1-first-exact-csky-c-20261111.json).

## Codec A gains exact C-SKY XIP regions — 2026-11-11

The image-A XIP and SRAM Ghidra function inventories were mapped to the
authenticated codec FWPK and checked against their full stored-body hashes.
Qualification of the current C-SKY manifest units selected 33 new
relocation-free XIP functions from 17 existing C units, totaling 356 bytes.
The eight image-B functions selected earlier were rediscovered but not
duplicated. The rebuilt hybrid now sources 460 codec bytes and retains
202,512 codec bytes as binary pull-through; the locked OTA hash still depends
on that pull-through.

No image-A SRAM function qualified in this pass. C-SKY instruction/data
classification, relocation-bearing functions, codec stage 1, model weights,
full source ownership and hardware boot remain unresolved. Evidence:
[`codec-a-first-exact-csky-c-20261111.json`](../evidence/codec-a-first-exact-csky-c-20261111.json).

## EM9305 gains exact ARC source regions — 2026-11-11

The qualifier now reads little-endian ARC ELF32 function symbols and maps
inventoried record-3 entries to stored offsets in the locked EM9305 image.
Fourteen relocation-free functions from seven existing C units match their
complete stock spans, totaling 118 bytes. The six-payload hybrid now sources
bytes from every payload, including 118 EM9305 bytes; the EM9305 image still
has 211,650 binary pull-through bytes. The locked OTA hash is retained through
that pull-through, while source completeness remains unproven.

ARC sections do not have the ARM mapping symbols used for instruction/data
classification, so strict coverage conservatively calls the 118 bytes
compiled but unclassified. Relocation-bearing ARC functions remain outside
this exact-byte qualifier. Evidence:
[`em9305-first-exact-arc-c-20261111.json`](../evidence/em9305-first-exact-arc-c-20261111.json).

## Codec B gains exact C-SKY source regions — 2026-11-11

The qualifier now reads little-endian C-SKY ELF32 function symbols and maps
image-B SRAM entries to their stored offsets in the locked codec FWPK. Eight
relocation-free functions from seven existing C units match the complete
stock function spans, totaling 104 bytes. The hybrid builder now accepts the
fingerprinted open C-SKY GCC and sources those bytes. Its codec pull-through
falls to 202,868 bytes while the full OTA retains the locked hash.

The raw Ghidra corpus supplies candidate boundaries; exact size and complete
byte equality are the selection gates. C-SKY sections lack the ARM mapping
symbols used for instruction/data classification, so strict coverage counts
the 104 bytes as compiled but unclassified. `sources-check` passed. The
source-only OTA is still nonidentical, and relocation-bearing C-SKY functions
remain outside this qualifier. Evidence:
[`codec-b-first-exact-csky-c-20261111.json`](../evidence/codec-b-first-exact-csky-c-20261111.json).

## Four ARM payloads gain exact C regions — 2026-11-11

The source qualifier now accepts a payload filter, allowing a full scan of
Apollo main, case and bootloader C units under their recorded profiles. It
selected 93 additional nonoverlapping stock regions totaling 612 bytes:
86 Apollo-main functions (544 bytes), one case boot context switch (34 bytes)
and six bootloader functions (34 bytes). Only qualifier-generated selections
entered `tools/build/source-plan.json`; production-profile variants remain
separate when an older qualified unit used different compiler flags.

The current hybrid has 654 source-built Apollo-main bytes, 58 case bytes,
34 bootloader bytes and 7,090 touch bytes. Its locked OTA hash is preserved
through pull-through. The unchanged source manifest has a previous passing
4,880-unit full C compile and seven strict links; `sources-check` and the new
hybrid build passed. The source-only OTA is still nonidentical, and the codec
and EM9305 payloads have no qualified C executable bytes in this hybrid
accounting. Evidence:
[`g2-arm-four-payload-exact-c-20261111.json`](../evidence/g2-arm-four-payload-exact-c-20261111.json).

## Touch clock, power-management and SysTick exact C — 2026-11-11

The production GCC 14.2 profile qualified eleven additional named touch
functions from the existing Infineon C units: four clock functions, four
power-management functions and three SysTick functions. Their 1,168-byte
combined stock ranges have no overlap with prior selections, and each passed
anchored full linked byte equality. Only the qualifier's generated regions
were added to `tools/build/source-plan.json`.

The hybrid touch payload now sources 7,090 bytes, including 6,398 C executable
bytes and 692 compiled data bytes. The full OTA hybrid retains the locked
4,301,227-byte hash through binary pull-through. `sources-check` passed, the
focused touch build compiled 105/105 units with no duplicate strong symbols,
and its strict link produced a 33,384-byte image. The source manifest is
unchanged from the previous full 4,880-unit passing compile. Full source
completeness and standalone OTA byte equality remain unproven. Evidence:
[`touch-clock-pm-systick-exact-c-20261111.json`](../evidence/touch-clock-pm-systick-exact-c-20261111.json).

## Apollo exact cached-TTE helper — 2026-11-11

The locked six-byte helper at `0x58EABC..0x58EAC2` loads a float from model
state offset `0x84` and returns it. A typed C state view and accessor now
compile to those exact six bytes under the production Apollo profile. The
source qualifier selected this bounded region, and the hybrid build now
sources 110 Apollo bytes, up from 104. The hybrid OTA retains the locked hash
because all other Apollo bytes are pulled through from the authenticated
artifact; this is not a complete source build.

`sources-check` passed. The full source build compiled 4,880/4,880 enabled C
units with zero failures or duplicate strong symbols, and all seven strict
source links passed without an external executable archive. The standalone
4,642,172-byte source OTA candidate, SHA-256
`6ab074068ce35fc4bcd83c1aae89fc4f25140edf8c8f8203d83361c1c05ec9dc`,
differs from the locked 4,301,227-byte OTA. The broader fuel-gauge model and
whole-firmware source completeness remain unproven. Evidence:
[`apollo-fuel-gauge-tte-exact-c-helper-20261111.json`](../evidence/apollo-fuel-gauge-tte-exact-c-helper-20261111.json).

## Apollo fuel-gauge time getters — 2026-11-11

The locked TTE getter at `0x55F994` returns a cached model float. The source
candidate now caches its approximate TTE value when processing a sample and
returns that field directly. The locked TTF wrapper at `0x55F9A0` permits
charge states CC, CC_VBUS_LIMITED and CV only when the stored termination
current is not NaN; the source candidate now applies that gate before its
approximate estimator. Twelve getter assertions and the previous nine
current-selection assertions passed with warnings treated as errors.

`sources-check` passed. The full build compiled 4,879/4,879 enabled C units
with no failures or duplicate strong symbols, and all seven strict source
links passed without an external binary archive. Apollo main is 3,818,800
bytes. The 4,642,172-byte source OTA candidate, SHA-256
`c57946b80438bcadc87db96a473d6c4d15404433e776368abb2af9530c5e364d`,
still differs from the locked artifact. The proprietary battery estimator,
including its 424-byte TTF helper, remains unrecovered; numeric time estimates
and hardware behavior are unverified. Evidence:
[`apollo-fuel-gauge-time-getters-20261111.json`](../evidence/apollo-fuel-gauge-time-getters-20261111.json).

## Apollo fuel-gauge process current selection — 2026-11-11

The locked `nrf_fuel_gauge_process` wrapper at `0x55F848..0x55F974` selects
its charging path from the current's sign bit or VBUS state. In CC charge
state it uses a non-NaN stored charge limit directly; otherwise it applies
the charge factor. The discharging path applies the discharge factor. The
existing source-only C provider now follows those observed branches instead
of choosing a factor from the current sign alone. A host harness passed nine
branch assertions with warnings treated as errors.

`sources-check` passed. The full build compiled 4,879/4,879 enabled C units
with no failures or duplicate strong symbols, and all seven strict source
links passed without an external binary archive. The resulting Apollo-main
image is 3,818,768 bytes. The 4,642,140-byte source OTA candidate, SHA-256
`397db410b45e5479c857c15c3cb99463c5b06960c96032407368303c58f6983d`,
still differs from the locked OTA. The larger Nordic estimator and its
calibration remain unrecovered; the C process model is not byte-identical or
hardware-qualified. Evidence:
[`apollo-fuel-gauge-process-current-contract-20261111.json`](../evidence/apollo-fuel-gauge-process-current-contract-20261111.json).

## Apollo pad-configuration source cells — 2026-11-11

The radio power and NOR clock selectors now index their source-owned pad
configuration words directly instead of translating stock RAM addresses in
C. A comparison against the preceding sources preserved all 48 radio
pin-to-cell mappings and 30 NOR clock mappings. The 87 initialized words match
the captured stock RAM initialization span exactly. The radio selector's
`setting` parameter now agrees with its 32-bit call-site declaration.

`sources-check` passed. The full build compiled 4,879/4,879 enabled C units
without failures or duplicate strong symbols; all seven strict source links
passed without an external binary archive. The 4,642,076-byte source OTA
candidate has SHA-256
`fd52e4a5a711db0144cef23707b78cf1ca2e2eba10c7496a65fa91f2c6d82640`.
It differs from the locked OTA, and the six zero-initialized radio pad cells
still lack a recovered runtime writer. This change does not establish whole
firmware source completeness or hardware behavior. Evidence:
[`apollo-pad-config-source-20261111.json`](../evidence/apollo-pad-config-source-20261111.json).

## Touch zero-table RAM and clock symbols — 2026-11-11

The locked flash clock backup/restore code passes `0x20000F04` to SROM.
Source C now owns the bounded 24-byte backup buffer there. The reset-copied
DeepSleep descriptor now relocates to an 8-byte parameter object at
`0x20000CCC`, and the three EEPROM write/erase paths share a source-owned
512-byte scratch object at `0x20000CD4`. The linked descriptor parameter
pointer equals the locked reset-copy value. Application delay code also uses
the existing source-owned clock globals instead of fixed RAM literals. The
focused 105-unit touch compile and strict link passed; the touch image is
33,384 bytes. Its object relocations and all seven relevant RAM placements
are recorded in
[`touch-zero-table-ram-source-20261111.json`](../evidence/touch-zero-table-ram-source-20261111.json).
The full G2 gate compiled 4,879/4,879 enabled C units without failures or
duplicate strong symbols and linked all seven payloads without an external
binary archive. Its 4,642,076-byte source candidate OTA, SHA-256
`5c44e67944365899484b4f79959f24895f49c59b03360413d2f63bec5cdb4380`,
differs from the locked artifact. Physical SROM effects, whole-firmware source
completeness, byte equality and hardware behavior remain unverified.

## Touch widget and EEPROM provider RAM — 2026-11-11

The locked EEPROM initializer passes a 48-byte provider table at
`0x20000ED4`. That table is now a source-owned BSS object with an exact linker
placement assertion. The widget configuration table also held 12 literal RAM
pointers for runtime contexts, sensor contexts, position history, filter
history and debounce state. Its fields now relocate to the corresponding C
objects, including one bounded 24-byte zeroed processing block at
`0x200009E4`. All 12 linked pointer values match the locked table. The focused
105-unit touch compile and strict link passed, and the 33,288-byte touch image
is byte-for-byte unchanged from the preceding candidate. This closes the
layout references. The full G2 gate compiled 4,879/4,879 enabled C units
without failures or duplicate strong symbols and linked all seven payloads
without an external binary archive. Its 4,641,980-byte source candidate OTA,
SHA-256 `2b6faec5bd61caaa1bf16437021e2672a400cf94daeadedf17258dd610cdf78b`,
still differs from the locked artifact. The scratch block's internal behavior,
whole-firmware source completeness, and hardware behavior remain unverified.
Evidence:
[`touch-widget-and-provider-ram-source-20261111.json`](../evidence/touch-widget-and-provider-ram-source-20261111.json).

## Touch application RAM source ownership — 2026-11-11

The stock zero table covers `0x200008A8..0x20000F58`, but the touch
application still reached its EEPROM, I²C, gesture, report, and saved-record
state through fixed RAM literals. Added 15 source-owned objects for those
cells and exact linker-placement assertions. The existing source-owned
CapSense root context at `0x200004EC` now has a shared C type and symbolic
references from the application, report, I²C callback and interrupt paths.
All 16 symbols have their expected addresses and sizes in the focused ELF;
the calibration object has relocations to the named state rather than fixed
addresses. The focused 105-unit touch compile and strict link passed. Its
touch image is 33,288 bytes, compared with 33,148 before this change. The
hybrid build still has 5,922 source-built and 28,510 binary pull-through
touch bytes. The full G2 gate compiled 4,879/4,879 enabled C units without
failures or duplicate strong symbols and linked all seven payloads without
an external binary archive. Its 4,641,980-byte source candidate OTA, SHA-256
`2b6faec5bd61caaa1bf16437021e2672a400cf94daeadedf17258dd610cdf78b`,
differs from the locked artifact. Whole-image source completeness and hardware
behavior remain unverified. Evidence:
[`touch-application-ram-source-20261111.json`](../evidence/touch-application-ram-source-20261111.json).

## Touch active-shield source paths — 2026-11-11

The locked common configuration has two shield pins and mode `1`, which the
pinned CapSense headers define as active shield. The C configuration had
disabled shield compilation even though the reset-copy source owns the two
shield pin records. Enabled the active-shield vendor paths. The focused
104-unit touch compile and strict link passed, retaining
`Cy_CapSense_SetShieldPinsInDesiredState`; the linked touch image grew from
32,904 to 33,148 bytes. The source qualifier found no new shield-specific
byte-identical function, so the source plan is unchanged. The hybrid build
still has 5,922 source-built and 28,510 binary pull-through touch bytes.
The full G2 gate compiled 4,878/4,878 enabled C units without failures or
duplicate strong symbols and linked all seven payloads without an external
binary archive. Its 4,641,840-byte source candidate OTA, SHA-256
`e1e8f3c9b94bfabe5dd1e0f5741e9f5ddd92854783e960264a1297644a5bd98b`,
differs from the locked artifact. Source completeness and hardware behavior
remain unverified. Evidence:
[`touch-active-shield-source-20261111.json`](../evidence/touch-active-shield-source-20261111.json).

## Touch automatic CapDAC source paths — 2026-11-11

The locked widget CDAC settings are `0x1AA`, `0x1A1` and `0x115`. The first
two request automatic reference, fine, compensation and/or divider calibration,
but the generated-config stand-in left the vendor C feature switches undefined,
which removed those branches at preprocessing. Enabled the corresponding CSD
and aggregate switches. The focused 104-unit touch compile and strict link
passed, and the source-linked touch image grew from 30,576 to 32,904 bytes.
The previously absent reference, fine, compensation, divider and verification
functions are now retained from the pinned Infineon C source. Eight stock
calibration functions have semantic source owners; their byte identity is not
claimed. The production qualifier separately selected three complete stock
functions, adding 300 exact source-built bytes. The hybrid touch breakdown is
5,922 source-built bytes and 28,510 binary pull-through bytes. The full G2
gate compiled 4,878/4,878 enabled C units with no failures or duplicate
strong symbols and linked all seven source payloads without an external
binary archive. Its 4,641,596-byte source candidate OTA, SHA-256
`07d47cec2e89b63a2bf0133fe3a97ca0244832aab512d5332641aff1ba9946e7`,
differs from the locked artifact. Source completeness and hardware behavior
remain unverified. Evidence:
[`touch-cdac-auto-source-20261111.json`](../evidence/touch-cdac-auto-source-20261111.json).

## Locked touch cardinalities and exact widget providers — 2026-11-11

The CapSense generated-config stand-in used five widgets, eight sensors,
eight pins and eight active slots. The authenticated common/widget records
instead specify three widgets, nine sensors, five pins, and five active plus
four low-power slots. Updated the compile-time cardinalities, including two
shield pins and a four-sensor maximum per widget. The corrected vendor C
matches the locked 50-byte `Cy_CapSense_IsWidgetActive` and 38-byte
`Cy_CapSense_IsWidgetEnabled` functions exactly. The report and main loop now
call the vendor widget-activity provider, and the duplicate local function
is removed. Both exact bodies are in the source plan. The focused 104-unit
touch compile and strict link passed; the hybrid build accepted all existing
and new selections, yielding 5,622 source-built touch bytes and 28,810 bytes
of binary pull-through. The full G2 gate compiled 4,878/4,878 enabled C units
without failures or duplicate strong symbols and linked all seven payloads
without an external binary archive. Its 4,639,268-byte source candidate OTA,
SHA-256 `5f7c7acf6099ece67cab0f8b9b9013abcb72cd9dd28ce003dce619552aca6603`,
differs from the locked artifact. Other feature flags, whole-image source
completeness, and hardware behavior remain unverified. Evidence:
[`touch-capsense-cardinalities-and-widget-provider-20261111.json`](../evidence/touch-capsense-cardinalities-and-widget-provider-20261111.json).

## Source-owned touch bootstrap log strings — 2026-11-11

Nine strings passed to the Touch bootstrap/save logger were still represented
by fixed addresses in the locked flash image. The C candidate now defines
their exact text and uses source symbol relocations at each call site. All
nine linked NUL-terminated strings match their locked bytes. The stock logger
itself returns zero, so this closes its data references without claiming
working logging. The focused touch image is 30,592 bytes and has no aligned
pointer words into the stock flash tail beyond the image, apart from two
linker end-value words. This scan does not cover indirect or unaligned values.
The focused 104-unit compile and strict link passed. The full G2 gate then
compiled 4,878/4,878 enabled C units with no failures or duplicate strong
symbols and linked all seven source payloads without an external binary
archive. The 4,639,284-byte source candidate OTA has SHA-256
`334027612a05760dc400d7c262270f65095f24a0a2d79217815bef7cca909148`
and differs from the locked artifact. Evidence:
[`touch-log-strings-source-20261111.json`](../evidence/touch-log-strings-source-20261111.json).

## Touch scan callback and electrode data relocation — 2026-11-11

The scan-preparation C candidate previously stored the stock Thumb address
`0x6781` into the interrupt callback slot. It now stores the source-owned
`touch_scan_isr` function pointer, and the unused second-stage binding helper
has been removed. The object has an ARM relocation to the ISR; the current
strict link discards both scan-preparation and ISR functions, so this is a
compiled candidate dependency rather than a live-image call.

The retained widget configuration table also pointed at three stock flash
addresses for electrode records. Those fields now point to groups 0, 4 and 8
of the existing C electrode array. The strict link retains all 72 electrode
bytes and resolves the table fields to `0xA30C`, `0xA32C` and `0xA34C` in the
30,200-byte touch image. The focused 104-unit touch compile and strict link
passed. The full G2 gate compiled 4,878/4,878 enabled C units without failures
or duplicate strong symbols and linked all seven payloads without an external
binary archive. Its source candidate OTA is 4,638,892 bytes, SHA-256
`1c2b3858bfc58812b60940e1d002ee6fcf83e8355f07d6548565d6c70c2efd57`,
which differs from the locked artifact. Source completeness and hardware
operation remain unverified. Evidence:
[`touch-scan-and-electrode-source-relocation-20261111.json`](../evidence/touch-scan-and-electrode-source-relocation-20261111.json).

## Touch CapSense source identities and exact low-power query — 2026-11-11

Four previously unverified stock touch functions now have named providers in
the pinned Infineon CapSense C units: the reference/fine CDAC frame writer
`0x5E64`, compensation CDAC writer `0x5ECC`, low-power activity query
`0x7CF8`, and configuration integrity check `0x7D92`. Their stock pseudocode
matches the source control flow and data offsets, and all four symbols appear
in the current source-linked touch ELF. The production Arm GNU 14.2 qualifier
matched both structure functions byte for byte. The 76-byte integrity check
was already selected; the 12-byte low-power query is newly selected into
`tools/build/source-plan.json`. The hybrid touch coverage is now 5,534
source-built bytes and 28,898 binary pull-through bytes. The authenticated
hybrid bundle still matches stock, but that equality depends on pull-through;
source completeness and hardware behavior remain unproven. Evidence:
[`touch-capsense-source-owner-20261111.json`](../evidence/touch-capsense-source-owner-20261111.json).

## Live touch report gesture source closure — 2026-11-11

The touch calibration/report C candidate called the stock Thumb address
`0x4071` for its 874-byte gesture machine. The independently reconstructed
`touch_gesture_step` and `touch_gesture_speed` were already in the G2 manifest
but not linked into the report path. The report now calls the C function.
The focused 104-unit touch build passed without failures or duplicate strong
symbols. Its strict source link contains both gesture providers, and the
linked report function's `bl` reaches `touch_gesture_step` at `0x8BD0`. The
touch image grew from 29,024 to 30,128 bytes. The current gesture and speed
source differs from the previously differential-validated source by comments
only, so its bounded behavioral evidence still applies. The full G2 gate then
compiled 4,878/4,878 enabled C units with no failures or duplicate strong
symbols; all seven strict source links passed without an external binary
archive. The other six payload binaries are unchanged. The source candidate
bundle is 4,638,820 bytes, SHA-256
`1055de9e5469ec48322f51b25f3aca61b2a633d9dc18723358a9c10fd2f9485b`,
and differs from the locked 4,301,227-byte OTA. Analog acquisition,
physical timing, whole-touch source completeness and stock byte identity
remain unverified. Evidence:
[`touch-report-gesture-source-closure-20261111.json`](../evidence/touch-report-gesture-source-closure-20261111.json).

## LVGL null-output callback exact-source selection — 2026-11-11

The locked Apollo image's callback word at `0x48400C` is `0x00483031`,
pointing to the Thumb function at `0x483030`. That function is the two-byte
`bx lr` used as LVGL's null-output callback. The linked upstream LVGL
`_out_null` has the same two bytes. Named the stock function in the Apollo
symbol census, then ran the production Clang qualifier against
`lv_sprintf_builtin.c`; it selected the exact body into
`tools/build/source-plan.json`. The authenticated hybrid builder accepted the
selection and reproduced the locked OTA hash. Its Apollo-main coverage now
includes 104 source-built bytes and 2,869,422 binary pull-through bytes. This
selection adds exact source for one function; the hybrid's equality does not
prove complete source coverage. Evidence:
[`apollo-lvgl-null-output-exact-source-20261111.json`](../evidence/apollo-lvgl-null-output-exact-source-20261111.json).

## Apollo historical residual source-owner closure — 2026-11-11

Audited the 17 functions (1,150 stock bytes) in the wave 27 residual list
against the current G2 manifest and strict source-linked Apollo ELF. All 17
have identifiable C source owners and linked symbols. Fifteen are upstream or
local-vendor source units; the existing first-party oscillator wait helpers
account for the other two. Added stock-address anchors to those two C
functions and source-owner rows to the coverage map. The 8-byte word-reader
wrapper is `am_hal_read_words`; the 2-byte no-op callback is LVGL's
`_out_null`. The linked `_out_null` body matches the stock two-byte SHA-256;
the Ambiq word-reader wrapper is a four-byte tail call against the stock
eight-byte call/return. This resolves that historical source-ownership list
only. Whole-bundle byte identity, current whole-image census coverage and
hardware behavior remain open. `make sources-check` passed, and the full G2
`make sources` gate compiled 4,878/4,878 enabled C units with zero failures or
duplicate strong symbols across seven payloads. The strict source link then
produced all seven images with no external binary archive; its report still
sets `source_completeness_proven=false`. The Apollo-main image remains
3,818,704 bytes, SHA-256
`ed06d9ac0927b68d4d3ee4d7656bb5ed5e6a02d672f96e83c4d07e6e216535b4`.
Evidence:
[`apollo-historical-residual-source-owners-batch-20261111.json`](../evidence/apollo-historical-residual-source-owners-batch-20261111.json).

## Apollo startup comparator exact source qualification — 2026-11-11

The locked Apollo image contains two prioritized initialization functions
missing from the 8,844-row historical symbol census: the eight-byte comparator
at `0x5BF0B4` and the 72-byte runner at `0x5BF0BC`. Their authenticated
boundaries and hashes are now in `g2/symbols/apollo_main.tsv`. The comparator's
existing C body now constrains its two field loads to the stock `r0`, `r1`
order. Production Clang emits the exact stock eight bytes, so
`qualify_sources.py` selected that region into `tools/build/source-plan.json`.
The runner still fails exact relocation-pattern qualification and remains a C
candidate.

`make sources-check` passes. Full `make sources` compiled 4,878/4,878 enabled
C units with no failures or duplicate strong symbols, and all seven strict
source links passed without an external binary archive. The linked comparator
at `0x593520` matches the locked function hash. Apollo-main remains
3,818,704 bytes; only two bytes differ from the preceding source candidate,
both in the comparator instruction order. Its new SHA-256 is
`ed06d9ac0927b68d4d3ee4d7656bb5ed5e6a02d672f96e83c4d07e6e216535b4`.
The other six payload binaries are unchanged. The two new census rows and one
exact source region do not establish whole-image completeness, bundle byte
identity, or hardware boot. `make source-bundle` assembled the six-component
candidate with the authenticated KWS weight data. It is 4,637,716 bytes,
SHA-256 `465eca238c463156aa131a9933d51862f82ee7f88e2c23a4fbc753e646a3f039`;
14 bytes differ from the preceding candidate after the two instruction-byte
changes and wrapper checksum updates. It still differs from the locked
4,301,227-byte OTA. Evidence:
[`apollo-init-table-stock-census-20261111.json`](../evidence/apollo-init-table-stock-census-20261111.json).

## Apollo initialization-table callback C contract — 2026-11-11

The 23-entry prioritized startup table declared its callbacks as returning
`void`, while the linked C providers return a status word. The table and runner
now use `int32_t (*)(void)` consistently, and the TLSF pool initializer's
source declaration returns `int32_t` like the other providers. The runner
still ignores each status. The RTC, product logger, and onboarding-news
entries already resolve to their C implementations through manifest aliases;
the old source comment calling them missing was stale.

`make sources-check` passes. The full G2 build compiled 4,878/4,878 enabled C
units with no failures or duplicate strong symbols; all seven strict source
links passed with no final undefined symbols or external binary archive. All
seven payload binary hashes match the preceding full build, including the
Apollo-main binary at SHA-256
`0c66b1e174fe7a8a0369f52f194df0ace9cd6f52e9784dacfa430472cd682f1f`.
This C contract correction does not establish source completeness, stock byte
identity, or hardware boot. Evidence:
[`apollo-init-table-callback-types-20261111.json`](../evidence/apollo-init-table-callback-types-20261111.json).

## Nordic fuel-gauge external-state contract — 2026-11-11

The locked `nrf_fuel_gauge_ext_state_update` body at `0x0055F74C..0x0055F842`
has an authenticated 246-byte hash. Its C source candidate had diverged in
observable cases: it rejected updates before initialization, cleared the
charge state on VBUS disconnect, rejected positive infinity as a correction
factor, and stored charge limits with the wrong sign. The existing C provider
now follows the stock case dispatch, first-byte charge-state read, IEEE-754
NaN/sign/zero checks, and negative-absolute limit storage. A focused host
harness passed 21 assertions covering these branches. The full G2 build
compiled 4,878/4,878 enabled C units with no failures or duplicate strong
symbols; all seven strict source links passed with no undefined symbols or
external binary archive. Only Apollo-main changed from the preceding source
bundle. Its image is 3,818,704 bytes, SHA-256
`0c66b1e174fe7a8a0369f52f194df0ace9cd6f52e9784dacfa430472cd682f1f`.
The six-component source OTA candidate is 4,637,716 bytes, SHA-256
`cfb4d1c9b56f464dca01b9280eb5d95474bf1d0bd44e6bf8ec414904612e599c`;
it still differs from the locked OTA. The Nordic SOC and time-prediction
model remains an uncalibrated source-only candidate. Evidence:
[`apollo-fuel-gauge-external-state-stock-contract-20261111.json`](../evidence/apollo-fuel-gauge-external-state-stock-contract-20261111.json).

## Apollo I2C/UART initialized data ownership — 2026-11-11

The `g2_stock_ram_20000c20` array represented a 24-byte MPU record plus
248 bytes already defined as I2C configuration, bus rows, UART configuration,
receive queues, and the start of channel state in other C units. The extra
copy carried three literal pointers to the stock I2C config at `0x20000C0C`
and four to stock UART buffers at `0x200B9C20..0x200BA820`. Current source
references use this array only as an MPU record at its base. Its C definition
now contains just the six MPU words. The six linked words are unchanged,
including both pointers relocated to the source-owned 8 KiB IOM buffer. The
MPU symbol shrank from 272 to 24 bytes, while the separately linked I2C and
UART owner symbols remain present. The Apollo-main image is 248 bytes shorter.

The full G2 build compiled 4,878/4,878 enabled C units with no failures or
duplicate strong symbols, and all seven strict source links passed with no
undefined symbols or external binary archive. The six-component source OTA
candidate is 4,637,812 bytes, SHA-256
`70e4b00b8baa54f5af30e3d47f4a589d489e7f828c594d764ade95fbb4a48de2`.
It differs from the locked 4,301,227-byte OTA. The presence of the named
owners does not establish exact contents of every I2C/UART record or physical
behavior. Evidence:
[`apollo-i2c-uart-initialized-data-ownership-20261111.json`](../evidence/apollo-i2c-uart-initialized-data-ownership-20261111.json).

## Apollo NemaVG table RAM relocation — 2026-11-11

The locked table at `0x005232D0` starts with the RAM address `0x20074EFC`,
the Nema context cell. Its C reconstruction still embedded that stock address,
while the source linker placed the named context cell at `0x200A25D8`. The
table now takes the address of the C object. In the focused Apollo-main link,
the first word is `0x200A25D8`; the other twelve words still match stock.
Only three bytes of the 3,819,048-byte linked Apollo image changed.
All 2,717 Apollo-main C units compiled, with no failures or duplicate strong
symbols, and its strict link passed. The later full G2 build retains the
relocated table pointer; its final Apollo-main image is 3,818,800 bytes,
SHA-256 `28f904cb79cd6cd00ce820aeab0f5b0f72f7aef636b475d667aa490ec758b262`.
This resolves one relocated data pointer. A lexical scan of 2,525 Apollo C
and header files records 212 remaining address-looking tokens across 29
files; packed descriptors, bit masks and stock-offset indices are included,
so these tokens require semantic review before any is called a dangling
pointer. Evidence:
[`apollo-nema-arc-context-relocation-20261111.json`](../evidence/apollo-nema-arc-context-relocation-20261111.json),
[`apollo-ram-literal-source-audit-20261111.json`](../evidence/apollo-ram-literal-source-audit-20261111.json).

## CASE interfunction frontier classified — 2026-11-11

The locked CASE interfunction gap frontier now has 349 classified rows
covering 2,184 bytes, with no unsupported rows. All row hashes match the
locked `firmware_box.raw.bin` and the rows do not overlap. The classifications
are 1,608 PC-relative literal bytes, 260 zero/alignment bytes, 28 bytes of
source-semantic data, and 288 bytes attributed to source-backed executable
functions. This is closure of the existing *interfunction frontier*, not a
proof that all CASE instructions and data have been inventoried.

The audit decoded Thumb PC-relative literal loads against the locked bytes
and checked function ownership in the Ghidra corpus. It resolved complete,
partial, and unaligned literal spans, then reviewed residual scheduler and
callback code, terminal tails, short strings, and zero alignment halfwords.
The six remaining instruction entries were written as separate C functions
in `startup_vector_candidate.c`. Five compile to self-branches and one to
`BX LR`; a retained linker section keeps their exact 12 instruction bytes
in the source-linked CASE image. Their linked addresses differ from stock,
and reachability of the isolated `BX LR` remains unproved. The CASE CRT now
calls separate C word-copy and zero helpers matching the stock loop contracts.

The full G2 build compiled 4,878/4,878 enabled C units with no failures or
duplicate strong symbols. All seven strict source links passed with no
undefined symbols or external binary archive. The source-linked CASE image
is 60,184 bytes, SHA-256
`8b764c6315d429cf06051f87fa9c010ca3adba4e25c5350ec8904d95fe01846d`.
The six-component source-candidate OTA is 4,638,060 bytes, SHA-256
`c9eee6a709de8ca80262347c521e7cc01e9153e2daa575a851acd26361706a30`;
it differs from the locked 4,301,227-byte OTA. Physical behavior, complete
code/data coverage, and stock equivalence remain unverified.
Evidence: `g2/evidence/case-pc-literal-coverage-{complete,partial,unaligned}-20261111.json`,
`case-residual-executable-coverage-20261111.json`,
`case-scheduler-residual-coverage-20261111.json`,
`case-zero-alignment-coverage-20261111.json`,
`case-tail-string-coverage-20261111.json`, and
`case-retained-entry-c-coverage-20261111.json`. Final build receipts and
payload hashes are in `case-frontier-final-source-build-20261111.json`.

## CASE ADC startup branch correction — 2026-11-11

The locked CASE routine at `0x080007A8` returns zero when the controller
is already enabled. Its source-linked C provider omitted this guard, so it
could write configuration during an active controller state. The guard is
now present. The three adjacent ADC startup providers also reload the
controller pointer at the stock post-helper, wait and timeout access sites.
Five focused hosted scenarios passed, covering pointer changes, the early
return and both timeout paths. The harness adapts only address-based memory
access for a host array; it does not run the stock image or validate hardware.
`sources-check`, all 4,878 enabled C compilations and seven strict payload
links passed, with no compile failures or duplicate strong symbols. The
source-linked CASE image is 60,180 bytes, SHA-256
`e88ec496541b037de81faa2807cef9dced0df2ea929edcddd772f325ad48b2c9`.
The source-only OTA is 4,638,056 bytes, SHA-256
`1828ea5e6b9267b4132a7e8cf3eca0a9db6a77fcc43d72bb053fdf5f2698166c`;
it differs from the locked target. Evidence:
[`case-adc-startup-branches-20261111.json`](../evidence/case-adc-startup-branches-20261111.json).

## Case PC-relative literal coverage batch — 2026-11-11

Eight more full case frontier spans, totaling 40 bytes, are now classified
as PC-relative literal data. Each word is loaded by a Thumb instruction
inside an inventoried function: the literals include RAM state pointers,
one peripheral address, and the constant `0x7FFFFFE8`. All frontier row
hashes match the locked case image and the rows remain nonoverlapping.
Unsupported case frontier rows fall from 194 to 186; 64 bytes are now
explicitly classified as literals across this and the startup review.
Other candidate literals still need review, and source completeness remains
open. Evidence:
[`case-pc-literal-coverage-batch-20261111.json`](../evidence/case-pc-literal-coverage-batch-20261111.json).

## Case startup literal-pool coverage — 2026-11-11

Four spans in the locked case startup image that the coverage frontier had
left as unknown code or data are now resolved. PC-relative literal loads
at `0x080000C4..CC` and `0x08000158..60` fetch the Thumb application entry,
early hook, startup entry, and MSP top. The literals at `0x080000F0..F4`
and `0x08000140..44` both hold the scheduler context pointer `0x20000128`.
The halfword at `0x080000EE..F0` is zero alignment before a literal.
All new row hashes match the authenticated case image. The frontier now
classifies 24 more literal bytes and two alignment bytes, reducing
unsupported rows from 198 to 194. This closes only those spans; remaining
case gaps and overall firmware source completeness are still open. Evidence:
[`case-startup-literal-coverage-20261111.json`](../evidence/case-startup-literal-coverage-20261111.json).

## Apollo font-chain success count — 2026-11-11

The locked font manager's node-add helper at `0x46d158` writes the new list
head but never increments the list count. Its constructor at `0x46cae0`
compares the head before and after each addition, counts successes locally,
and writes that count to list offset `+8` only when returning a valid chain.
The C helper previously incremented the list count on each addition. It now
leaves that field alone; the constructor checks head changes and publishes
the final count after linking the fonts. Linked Apollo instructions have
only the zero initialization and final count store at offset `+8`.
`sources-check`, all 4,878 enabled C compilations, and all seven strict
source links passed without failures or duplicate strong symbols. Only
Apollo-main changed versus the preceding source bundle. The source-only OTA
is 4,638,060 bytes, SHA-256
`37c3f73290aea91d7f84d1a5c08d1e7eb37d51c38d0d38145af0562cadfb507c`.
Physical font behavior and whole-firmware source completeness remain
unverified. Evidence:
[`apollo-font-chain-count-20261111.json`](../evidence/apollo-font-chain-count-20261111.json).

## Apollo tracepoint CRC ownership and EFS state span — 2026-11-11

The locked TPS1 state writer and reader both call `0x47ddfe`, which computes
the CRC of the first 12 bytes through the table routine at `0x4d34c4`.
Their C copies instead called the TPF1 packet CRC helper. Both now call the
existing state wrapper. The two C CRC implementations agreed on 4,096
generated TPS1 records, and the final linked writer and reader both call
the state wrapper.

The EFS transfer-state C array was 0x76 bytes even though its typed object
and seven stock reset sites use 0x78 bytes. In the preceding linked image,
the next one-byte state cell began exactly at the end of the 0x76-byte EFS
symbol, so a reset could clear that cell. The array is now 0x78 bytes; the
new linked EFS symbol ends exactly where the next symbol begins.
`sources-check`, all 4,878 enabled C compilations, and seven strict source
links pass without failures or duplicate strong symbols. The source-only
OTA is 4,638,060 bytes, SHA-256
`11b10a0af91729cc51e7be43ffa6e82488374d6bd42c8f55dddf0bb1b908cb52`.
Only the Apollo-main payload changed versus the preceding source bundle.
Physical behavior and overall source completeness remain unverified. Evidence:
[`apollo-tracepoint-crc-efs-state-20261111.json`](../evidence/apollo-tracepoint-crc-efs-state-20261111.json).

## EM9305 timer probe zero-count argument — 2026-11-11

The locked EM9305 timer probes at `0x31398c` and `0x3139cc` load an unsigned
halfword count. When it is zero they skip the ARC LP delay and pass zero in
`r0` to ROM probes `0x104ca4` and `0x104cb4`. The C helper previously
substituted `UINT32_MAX` for zero. It now passes the measured count for both
ROM paths, including zero. The ARCv2 `EXTH` instruction in the stock
nonzero path is unsigned, so `EXTH(count - 1) + 1` equals the original
halfword across its full range. In the linked-source object the prior
`mov.eq r0,0xffffffff` is gone; `exth.f`, the zero branch, the LP loop and
both ROM probe relocations remain. An exhaustive 65,536-count arithmetic
check passed. `sources-check`, all 4,878 enabled C compilations, and seven
strict links passed without compile failures or duplicate strong symbols.
Only the EM9305 payload binary changed versus the preceding source build.
The source-only OTA is 4,638,060 bytes, SHA-256
`30e5bc9aca683ad3707e63d5ae976fae3304dc176e388d76a2b74f034c364c4a`.
Physical timer calibration and overall source completeness remain unverified.
Evidence: [`em9305-timer-probe-zero-20261111.json`](../evidence/em9305-timer-probe-zero-20261111.json).

## Apollo-main ITCM overlay startup copy — 2026-11-11

The locked Apollo region table has an LZ77 record at `0x75d3e0` targeting
ITCM `0x40`. The GNU-linked source previously initialized no bytes there;
Renode preloaded the overlay and hid that startup gap. The Apollo source now
emits the 24-byte countdown/word-copy overlay from a naked C function and
copies it to `0x40..0x58` as the first startup record. The linked source
overlay at `0x61003c` matches the recovered locked 24 bytes exactly, and the
linker asserts its size. The record at `0x7a6c28` resolves to copy handler
`0x507471`, source `0x61003c`, destination `0x40`, end `0x58`.
`sources-check`, all 4,878 enabled C compilations, and seven strict links
passed with no compile failures or duplicate strong symbols. The source-only
OTA is 4,638,068 bytes, SHA-256
`9dfdf5c39116e35b3ad6be66306063102e5e74c73c7427a0855a48c6cb9904ed`.
In an isolated Renode run without its usual ITCM preload, address `0x40`
started at zero and all six words matched the locked overlay after startup.
The same no-preload image ran for two virtual seconds, emitted 56 HCI host
packets including advertising enable, and reported no simulator errors or
unhandled exceptions. No physical boot was attempted; source completeness
and hardware behavior remain unproven. Evidence:
[`apollo-itcm-overlay-startup-20261111.json`](../evidence/apollo-itcm-overlay-startup-20261111.json).

## Codec A BINH stage-1 clock trim success — 2026-11-11

The locked BINH A clock initializer calls a distinct wrapper at `0x10000f34`.
It enables the 32 kHz oscillator only when trim at `0x10000860` succeeds. The
C initializer previously called trim directly and discarded its result, so
this hardware clock transition was absent. It now calls an explicit C wrapper
placed at the stock address. Its 18 instruction bytes match stock at 14
positions; the four differences are relocated call offsets. The linker pins
the wrapper in the 20-byte interval before read-only data and asserts its
18-byte instruction size. The 79 internal direct-call sites in the locked
stage-1 block reach 31 targets; this wrapper and the three pinned SDK clock
helpers account for the formerly unnamed targets. The focused 367-unit codec
A build and strict link passed. The full source gate compiled 4,878 enabled
C units without failures or duplicate strong symbols, and all seven strict
links passed. The stage-1 load remains 4,756 bytes within the 12,260-byte
limit. All seven primary payload binaries are unchanged; only the packaged
codec component changed. The 4,638,028-byte source-only OTA SHA-256 is
`82a71f7ca865789b59e2f746ce87ac31329131b21617dc4ec71d875040ab6db7`.
Physical oscillator startup and overall source completeness remain unverified.
Evidence: [`codec-a-stage1-clock-trim-20261111.json`](../evidence/codec-a-stage1-clock-trim-20261111.json).

## Codec B BINH stage-1 direct-call ownership — 2026-11-11

The locked BINH B stage-1 block has 61 direct `bsr` sites to 22 distinct
targets. Twenty-one targets now have address-named C providers; the remaining
`0x10000138` is the pinned NationalChip `__module_get_info` C helper, also
present as a local symbol in the linked source ELF. The stock
`0x10001310` trim-success wrapper was previously folded into the C clock
initializer. It now has its own C function and a live call from that
initializer. Its 20-byte linked body follows the stock trim-call, failure
return, and 32 kHz enable sequence. The two indirect loader calls resolve
statically to the stage-2 and stage-1 reset entries already named in C.
A focused 332-unit codec B build and strict link passed. The full source
gate compiled 4,878 enabled C units with no failures or duplicate strong
symbols, and all seven strict links passed. Only the codec B payload and
codec component changed; the source-only OTA is 4,638,028 bytes, SHA-256
`ecddb449ef72ce49927a078fb88f886acf0ca124333f952e947c3509e39c74d1`.
Direct-call ownership does not prove instruction coverage, physical boot,
or full source completeness. Evidence:
[`codec-b-stage1-direct-call-closure-20261111.json`](../evidence/codec-b-stage1-direct-call-closure-20261111.json).

## Codec B BINH stage-1 JEDEC quad policy — 2026-11-11

The BINH B NOR initializer's C candidate grouped ESMT `0x1c3812/13` with
PUYA parts and attempted a combined status write. The locked initializer
branches around all QE status transactions for those ESMT IDs, as does the
pinned NationalChip SPL. The C initializer now returns after caching either
ESMT ID; PUYA `0x854012` and `0x856013/14` retain the two-byte write, and
other IDs retain the status-2-only path. Linked C-SKY disassembly confirms
the three dispatch routes. A focused codec B build compiled 332/332 units and
linked strictly. The stage-1 load remains 6,764 bytes within the locked
12,288-byte block. The full `make sources` gate compiled 4,878/4,878 enabled
C units without failures or duplicate strong symbols, and all seven strict
links passed. Six payload binaries are unchanged; the codec B image and
codec package changed. The 4,638,028-byte source-only OTA now has SHA-256
`063cb1a33bb2e439a6031ae12607fe53016210d6e3e170c49fd6e5ff3bf9226d`.
Full initializer behavior and physical flash transactions remain unverified;
source completeness is unproven. Evidence:
[`codec-b-stage1-jedec-quad-policy-20261111.json`](../evidence/codec-b-stage1-jedec-quad-policy-20261111.json).

## Codec A BINH stage-1 JEDEC quad policy — 2026-11-11

The BINH A NOR reader's C candidate wrongly grouped ESMT `0x1c3812` and
`0x1c3813` with PUYA parts and attempted a combined status write. The locked
reader and pinned NationalChip SPL both leave those two ESMT IDs alone. The C
branch now skips their status writes and proceeds to XIP setup; PUYA IDs
`0x854012`, `0x856013`, `0x856014` retain the combined write path and other
IDs retain the status-2-only path. A focused codec A build compiled 367/367
units, and the strict link passed. The BINH A stage-1 source load remains
4,756 bytes within the locked 12,260-byte limit; its image changed as
expected, while the separate UART codec A image stayed unchanged. The full
`make sources` gate compiled 4,878/4,878 enabled C units without failures or
duplicate strong symbols, and all seven strict links passed. Only the codec
component changed in the source-only OTA; its new 4,638,028-byte SHA-256 is
`02668eeebe7e3ea87bec6f72c88c9e62ee2de729248cd486a869ebccbceb57cb`.
Full reader behavior and hardware flash transactions remain unverified. Evidence:
[`codec-a-stage1-jedec-quad-policy-20261111.json`](../evidence/codec-a-stage1-jedec-quad-policy-20261111.json).

## Codec A BINH stage-1 clock switch table — 2026-11-11

The locked and C-linked 224-byte clock-frequency switch tables agree at 203
same-offset bytes. The other 19 words are branch targets into moved blocks;
disassembly shows the same zero-result, common-lookup and module 16/22/10/19
selection actions at each mapped target. Normalizing those addresses makes
all 224 bytes identical. The codec A stage-1 linker now checks the normalized
table hash and 19 mapped words on each source link. The focused codec A link
passed with both the UART and BINH A stage-1 images unchanged. This checks the
table and branch destinations, not the full clock-frequency function or
hardware startup. Evidence: [`codec-a-stage1-clock-switch-table-20261111.json`](../evidence/codec-a-stage1-clock-switch-table-20261111.json).

## Live CASE command routing — 2026-11-11

The linked legacy command entry at stock `0x08000928` matched 708/708
no-action opcode cases and 72/72 `0xAF`, `0xD1`, `0xDD` and `0xDF` state
cases under controlled logging. The linked nonlocal binary forwarding route
matched 288/288 cases across both framing modes, including event masks and
copied bytes. Four local binary commands (`0x50`, `0x5C`, `0x5D`, `0x68`)
matched 240/240 cases at their send, ACK and GPIO boundaries. The `0x3E`
aging-state route matched 144/144 event and state cases; `0x14` matched
523/523 sensor-reply cases, including signed scaling with edge inputs.
The `0x3D` aging-exit forwarding route matched 192/192 cases and `0x56`
OTA-state changes matched 144/144 cases at their lower-call boundaries. A narrower
offline forwarder duplicated the nonlocal stock route but
was discarded by the strict linker; its C, README and manifest unit were
removed. The manifest now has 4,883 units; 359/359 CASE units compile and
the strict CASE link is unchanged at 60,184 bytes, SHA-256
`f7135f3a8254111949f55deb2bd092ff9b7ec2e61fada299c0fe2f0916676a84`.
All 4,878 enabled G2 C units compiled and all seven payloads linked strictly;
all seven binary hashes are unchanged. The source-only OTA remains 4,638,028
bytes, SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
Other active commands, physical effects and overall source completeness
remain unverified. Evidence: [`case-command-routing-live-20261111.json`](../evidence/case-command-routing-live-20261111.json).

## Live CASE frame dispatcher — 2026-11-11

The worker's linked frame dispatcher at stock `0x0800085C` matched the locked
firmware in 12 directed and 1,024 seeded controlled-child cases. These cover
raw legacy frames, ASCII hex decoding, both binary formats, malformed frames
and retry-state updates. The old offline dispatcher was a duplicate whose
sections the strict linker discarded; its C, private header, README and
manifest unit were removed. The CASE image and all seven payload binaries
are unchanged. The manifest now has 4,884 units; 4,879 enabled C units
compiled, and all seven payloads linked strictly without duplicate strong
symbols. The source-only OTA remains 4,638,028 bytes with SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
The controlled comparison does not establish command-side or physical UART
effects. Evidence: [`case-frame-dispatch-live-20261111.json`](../evidence/case-frame-dispatch-live-20261111.json).

## CASE UART frame capacity guard — 2026-11-11

The linked CASE callback at stock `0x08006544` now checks the 16-bit `0xCF`
payload length before passing it to blocking receive. The frame buffer is
1,200 bytes at `0x20000974` and the UART handle begins immediately afterward
at `0x20000E24`. A five-byte header and trailing byte leave at most 1,194
payload bytes. The new C path rejects 1,195 and 65,535 before receiving;
stock forwards those lengths, so this is an intentional safety difference.
Controlled stock/source emulation matched 452 bounded valid callback cases,
seven blocking receive cases and ten UART wait cases against the final linked
CASE image. All 4,880 enabled G2 C units compiled and all seven payloads
linked strictly, without duplicate strong symbols. The source-only OTA is
4,638,028 bytes with SHA-256
`4ded84cd623fd0dafd0633e71481cab92ac2845f8a64dbb3bde7eea8ddf29990`.
Physical UART behavior and source completeness remain unverified. Evidence:
[`case-uart-frame-capacity-20261111.json`](../evidence/case-uart-frame-capacity-20261111.json).

## Live CASE UART receive graph — 2026-11-11

The CASE link map exposed five compiled UART receive/frame units that the
strict linker discarded. Their stock-address functions already have live
startup providers. The superseded C, its private headers and offline READMEs
were removed from `g2/src/sources.json` and the source tree, leaving one
implementation per stock receive, bind, ISR and frame-parser function. Vector
slot 43 still points to the linked UART IRQ wrapper; the live map contains
the bind core, RX callbacks, frame parser and blocking receive helper. The
CASE image and all seven payload binaries are byte-for-byte unchanged. The
manifest now has 4,885 units, 4,880 enabled C units compiled, and seven
strict links with no duplicate strong symbols. The source-only OTA remains
4,638,024 bytes with SHA-256
`c1187eee3fa765619ad3f99a10bf2011300fc43ecb9d49a1d1399f74ee971f54`.
Physical UART behavior and overall source completeness remain unverified.
Evidence: [`case-uart-live-source-consolidation-20261111.json`](../evidence/case-uart-live-source-consolidation-20261111.json).

## CASE output setter return contract — 2026-11-11

The linked CASE output setter at stock `0x080099E8` now returns the cache
byte on a hit, zero after a failed lower write, and the possibly mutated
stack byte after a successful write and cache update. Previously its C
provider was `void` while the `0x3f` enable wrapper returned its result.
The alias and caller declarations now agree. A three-branch register-backed
host harness and the linked ARM disassembly checked the return paths. The
CASE tree compiled 366/366 units; all 4,885 enabled G2 C units compiled and
all seven payloads linked strictly, without duplicate strong symbols. The
source-only OTA is 4,638,024 bytes with SHA-256
`c1187eee3fa765619ad3f99a10bf2011300fc43ecb9d49a1d1399f74ee971f54`.
Physical output-bus behavior and source completeness remain unverified.
Evidence: [`case-sensor-setter-return-20261111.json`](../evidence/case-sensor-setter-return-20261111.json).

## CASE RAM-to-flash interrupt restoration — 2026-11-11

The linked CASE copy helper at stock `0x08003F38` now saves `PRIMASK` before
disabling interrupts and restores that exact value after its 64-word copy and
flash-busy wait. The previous C read `CONTROL` and could conditionally enable
interrupts, losing the caller's state. Stock and freshly linked source
disassembly show the same `mrs PRIMASK` / `cpsid i` / `msr PRIMASK` ordering.
The CASE tree compiled 366/366 units; all 4,885 enabled G2 C units compiled,
and all seven payloads linked strictly, without duplicate strong symbols.
The source-only OTA is 4,638,016 bytes with SHA-256
`26fe401230373641c1e280bc77a22ab37ab7551b7d652ff1f68ccd4432e361a9`.
Physical flash behavior and overall source completeness remain unverified.
Evidence: [`case-flash-primask-source-20261111.json`](../evidence/case-flash-primask-source-20261111.json).

## CASE flash controller status returns — 2026-11-11

The linked CASE C helpers for flash unlock and lock now return the status
observed in the locked firmware. Unlock checks the controller lock bit after
writing its keys; the lock helpers read back their control bits. The legacy
serial-number write at stock `0x08003664` returns the final lock status, so
its source path no longer relies on a `uint32_t` alias of a `void` provider.
Caller declarations now agree with the provider. The CASE tree compiled
366/366 units and linked strictly; all 4,885 enabled G2 C units compiled and
all seven payloads linked strictly, without duplicate strong symbols. A
register-backed host harness passed the available return and write cases.
The source-only OTA is 4,638,044 bytes with SHA-256
`edea0f8ddad60b7864ae368cbe98ca3b5fa7b2bfb2a216bd23194ce31c8013b0`;
source completeness and physical flash behavior remain unverified. Evidence:
[`case-flash-status-source-20261111.json`](../evidence/case-flash-status-source-20261111.json).

## One touch SysLib delay body — 2026-11-11

The source touch image had two implementations of stock
`Cy_SysLib_DelayCycles`: a PDL-facing loop over the unscaled requested count
and an application-facing loop with repeated stack accesses. PDL and
application callers now use one C body. Its linked loop follows stock's
`(cycles + 2) >> 2` count and add/subtract branch sequence, with one extra
post-loop instruction; physical cycle timing remains unmeasured. The duplicate
symbol is absent from the linked ELF. The focused touch build, all 4,885
enabled C units, all seven strict payload links, authenticated hybrid build,
manifest check, and 16 verifier tests passed. The source-only OTA is
4,638,012 bytes with SHA-256
`0b0c80e436802a68d1e64a7472b5d526e320f2727ba9ff8b6c92bb2baf3ddad0`.
Evidence: [`touch-syslib-delay-unified-20261111.json`](../evidence/touch-syslib-delay-unified-20261111.json).

## Seven more CAPSENSE units with Arm GNU 14.2 — 2026-11-11

Seven additional linked touch CAPSENSE units now compile with the pinned Arm
GNU 14.2 toolchain. Fresh qualification found 16 new, nonoverlapping
stock-exact C functions totaling 844 bytes; each symbol appears in the
focused source-linked touch map. The source plan now selects 87 touch regions
(5,522 bytes) and 105 G2 regions (5,640 bytes). The focused touch build and
link, all 4,885 enabled C units, seven strict payload links, authenticated
hybrid build, and 16 verifier tests passed. The source-only OTA is 4,638,064
bytes with SHA-256
`1076b59448131b3f5940221a3cc779201028a62f4d66beda82cecddb40dba6dc`.
Other code in those units and physical touch behavior remain unverified.
Evidence: [`touch-capsense-seven-gcc14-units-20261111.json`](../evidence/touch-capsense-seven-gcc14-units-20261111.json).

## Exact C CAPSENSE functions with Arm GNU 14.2 — 2026-11-11

The linked touch CAPSENSE sensing unit now uses the pinned Arm GNU 14.2
compiler. Its `Cy_CapSense_ConfigureMsclpTimer` body matches all 70 stock bytes
after its call relocation is bound to the inventoried timer helper. Fresh
qualification of that unit found 16 new, nonoverlapping exact CAPSENSE
functions totaling 1,012 bytes. The source plan now selects 71 touch regions
(4,678 bytes) and 89 G2 regions (4,796 bytes). The focused touch build,
4,885-unit full manifest build, all seven strict source links, authenticated
hybrid build, and 16 verifier tests passed. The source-only OTA is 4,638,116
bytes with SHA-256
`0d3e1caf0b298ea70950a8284d30acb809f4163b0798c856db5e49e44f8d562f`;
source completeness and hardware behavior remain unverified. Evidence:
[`touch-capsense-gcc14-exact-source-20261111.json`](../evidence/touch-capsense-gcc14-exact-source-20261111.json).

## Current source image versus stock in Renode — 2026-11-11

The freshly linked Apollo-main C image and the authenticated stock image
sent the same 56 HCI host packets in matched two-second Renode runs, ending
with advertising enable. In matched paired hub runs, Secure Connections
pairing completed, all 18 phone steps produced the same per-step notification
counts, and five touch checks matched. Both produced 16 notifications and had
zero CFSR/HFSR. Three settings notifications carried battery field 12 as 38
in the source image versus 31 in stock. At two seconds, the source and stock
telemetry both read 3.798 V, 0 mA and 25.00 °C, while their SOC words were
38 and 31. The source-only Nordic fuel-gauge provider remains an uncalibrated
estimate; the battery path is a concrete divergence to investigate. The emulator
models the other chips and does not
establish their firmware behavior or physical boot. Evidence:
[`g2-source-current-paired-simulator-20261111.json`](../evidence/g2-source-current-paired-simulator-20261111.json).

## Additional exact touch C bodies — 2026-11-11

A fresh sweep compiled all 81 enabled touch Clang source units and found seven
previously unselected, nonoverlapping stock-exact bodies: four configuration
leaf/fault functions, `_exit_halt`, and both critical-section helpers. All
seven were already linked in the source image. The source plan now covers 55
touch regions/3,666 bytes and 73 G2 regions/3,784 bytes. The authenticated
hybrid build passes with 3,666 touch bytes from C; the source-only OTA remains
nonidentical. Evidence:
[`touch-clang-exact-sweep-20261111.json`](../evidence/touch-clang-exact-sweep-20261111.json).

## Exact C touch CRT hooks — 2026-11-11

The touch image now links the GCC 14.2 CRT clone-table registration and
constructor/destructor paths from C instead of two empty hooks. The compiled
and stock-linked 32-, 40-, 44-, and 36-byte bodies match the locked touch
image exactly. The empty TM table and 25 bytes of CRT state occupy their
stock RAM addresses. The source plan covers 48 touch regions/3,640 bytes and
66 G2 regions/3,758 bytes. The full manifest compiled 4,885/4,885 enabled
C units with no failures or duplicate strong symbols; all seven strict links,
the authenticated hybrid build, and 16 verifier tests passed. The source-only
OTA is 4,638,336 bytes with SHA-256
`b7f00ac20ebf27524e55819d5124b5f6dc6eb85c396d5e493e9ede0fb627fd86`,
so it is still not the 4,301,227-byte locked artifact. Evidence:
[`touch-crt-exact-source-20261111.json`](../evidence/touch-crt-exact-source-20261111.json).

## Exact C touch lite exit — 2026-11-11

The linked touch exit path now compiles from C with the weak cleanup hook left
undefined, as in stock. The exact-source matcher records that linker state
separately from an absolute zero binding. Fresh qualification matched the
complete 40-byte exit function at stock `0xA9AC..0xA9D4`; the older symbol
inventory's 54-byte extent overlaps the following `memset`. The source plan
now covers 44 touch regions/3,488 bytes and 62 G2 regions/3,606 bytes. The
full manifest compiled 4,884/4,884 enabled C units with no failures or
duplicate strong symbols; all seven strict links and the hybrid build passed.
The source-only OTA remains nonidentical. Evidence:
[`touch-libc-exit-exact-source-20261111.json`](../evidence/touch-libc-exit-exact-source-20261111.json).

## Exact C touch init-array runtime — 2026-11-11

The touch C runtime now builds `__libc_init_array` from the pinned newlib
init-array loop. The linker binds its empty preinit range and single init
entry to the reconstructed stock RAM layout. Fresh qualification matched the
complete 72-byte code-and-literal section at the stock entry. The source plan
now covers 43 touch regions/3,448 bytes and 61 G2 regions/3,566 bytes. The
full manifest compiled 4,883/4,883 enabled C units without failures or
duplicate strong symbols; all seven strict links and the hybrid build passed.
The source-only OTA remains nonidentical. Evidence:
[`touch-libc-init-array-exact-source-20261111.json`](../evidence/touch-libc-init-array-exact-source-20261111.json).

## Exact C touch byte-loop runtime — 2026-11-11

The linked touch `memset` and `memcpy` implementations now compile from C
with the fingerprinted Arm GNU 14.2 compiler at `-Os`. Their complete 16-
and 18-byte bodies match the authenticated stock runtime exactly. The source
plan now covers 42 touch regions/3,376 bytes and 60 G2 regions/3,494 bytes.
The full manifest compiled 4,882/4,882 enabled C units without failures or
duplicate strong symbols; all seven strict links and the authenticated hybrid
build passed. The all-source bundle remains nonidentical. Evidence:
[`touch-nano-runtime-exact-source-20261111.json`](../evidence/touch-nano-runtime-exact-source-20261111.json).

## Exact touch plan points to linked C — 2026-11-11

Fresh qualification of the nine PDL units used by the source build found 38
stock-exact function bodies. Together with the two flash-address C helpers,
all 40 selected touch regions (3,342 bytes) now point to enabled, linked
source units. The old `cy_flash.c` and `cy_scb_ezi2c.c` selections were
replaced without changing any selected stock range or hash. The authenticated
hybrid bundle still passes, with 31,090 touch bytes supplied by binary
pull-through; the source-only bundle remains nonidentical. Evidence:
[`touch-linked-exact-source-provenance-20261111.json`](../evidence/touch-linked-exact-source-provenance-20261111.json).

## Source-owned exact touch flash address helpers — 2026-11-11

The row-write C path now calls separate flash address-validation and row-number
helpers. Compiled with the pinned Arm GNU 14.2 toolchain, their complete 52-
and 28-byte bodies match stock byte for byte at the independently inventoried
entries. The exact-source plan now selects these **linked C** helpers instead
of the equivalent upstream probe, without increasing its 58 G2 exact regions.
The full G2 manifest compiled 4,881/4,881 enabled C units with no failures or
duplicate strong symbols; all seven strict links and the authenticated hybrid
build passed. The all-source bundle still differs from stock. Evidence:
[`touch-flash-address-source-20261111.json`](../evidence/touch-flash-address-source-20261111.json).

## Nine touch PDL units built with the qualified compiler — 2026-11-11

The source manifest now builds GPIO, SCB common, system interrupt, system PM,
and SysTick PDL units with the fingerprinted Arm GNU 14.2 compiler, alongside
the four PDL units switched earlier. GCC's PM callback static state is pinned
to the same stock RAM cell. The full manifest compiled 4,880/4,880 enabled C
units with no failures or duplicate strong symbols, and all seven payloads
strictly linked. Only touch changed in the assembled OTA: its component gained
104 bytes and 112 more same-offset bytes match stock, but it is still 5,172
bytes shorter and the bundle is not byte-identical. Evidence:
[`touch-gcc14-nine-pdl-source-build-20261111.json`](../evidence/touch-gcc14-nine-pdl-source-build-20261111.json).

## Touch reset-copy source ownership — 2026-11-11

The source-linked `.touchdata` covers the stock 964-byte reset-copy extent.
Against the authenticated stock load image, 946 bytes match at the same data
offset. The other 18 bytes are in nine 32-bit pointers to functions or
configuration objects whose source-linked flash addresses differ. This closes
the earlier missing-generated-config *data ownership* question for that span;
it does not prove the code layout, hardware behavior, or the whole touch image.
Evidence: [`touch-reset-copy-source-ownership-20261111.json`](../evidence/touch-reset-copy-source-ownership-20261111.json).

## Arm GNU 14.2 touch PDL in the all-C source build — 2026-11-11

Four touch PDL translation units now use the fingerprinted Arm GNU 14.2.Rel1
compiler and pinned PDL input cache in the source manifest. The touch RAM
linker script places GCC's `compRunStat.0` section at the authenticated ILO
state cell. The full G2 manifest compiled 4,880/4,880 enabled C units with no
failures or duplicate strong symbols; all seven strict payload links passed.
The six-component source candidate is 4,638,140 bytes and differs from the
locked OTA. Its touch component is 5,276 bytes shorter than stock. These gates
establish a source build, not source completeness, hardware behavior, or byte
identity. Evidence: [`touch-gcc14-source-build-20261111.json`](../evidence/touch-gcc14-source-build-20261111.json).

## Exact touch PDL bodies with Arm GNU 14.2 — 2026-11-11

The locally fingerprinted Arm GNU 14.2 compiler and pinned PDL inputs match
four more complete stock touch functions: `Cy_MSCLP_Configure` (424 bytes),
`Cy_SCB_I2C_Init` (484), `Cy_SysClk_ClkHfGetFrequency` (56), and
`Cy_SysLib_SetWaitStates` (56). All 36 prior exact touch selections remain
matched. The source plan now verifies 40 touch functions and 3,342 touch
bytes, or 58 G2 functions and 3,460 bytes overall. The authenticated hybrid
build passes and matches the locked OTA by pulling through all remaining
bytes. The separate source-only candidate is still different. Evidence:
[`g2-touch-gcc14-exact-source-plan-20261111.json`](../evidence/g2-touch-gcc14-exact-source-plan-20261111.json).

## Fresh exact G2 source-plan qualification — 2026-11-11

The fingerprinted ARM GNU touch PDL run retained all 23 previously selected
exact touch functions and found 13 more, adding 534 verified stock bytes.
An audit of the checked-in G2 source plan found six stale selections: two no
longer compile to their recorded bodies and four referenced deleted source
files. The moved case critical-entry function was requalified from its current
C source, restoring 24 exact bytes. The revised plan now selects 54 current
G2 regions covering 2,440 bytes. Its default authenticated hybrid build
passes and is byte-identical to the locked OTA **using binary pull-through for
the remaining bytes**. The separate source-only candidate is still not
identical, and source completeness is unproven. Evidence:
[`g2-exact-source-plan-refresh-20261111.json`](../evidence/g2-exact-source-plan-refresh-20261111.json).

## C-compiled bootloader ROM Thumb aliases — 2026-11-11

The bootloader's remaining first-party `.S` link helper is now a C translation
unit containing three typed declarations for external resident-ROM entry
points. The ARM C compiler emits absolute Thumb function symbols and no text,
data, or BSS. The focused bootloader link and the full six-component OTA
candidate are byte-identical to their preceding source candidates. The full
G2 manifest compiled 4,880/4,880 enabled units without failures or duplicate
strong symbols, and all seven strict payload links passed. The resident ROM
bodies are outside the OTA and are not reconstructed here. Evidence:
[`bootloader-rom-thumb-aliases-c-20261111.json`](../evidence/bootloader-rom-thumb-aliases-c-20261111.json).

## Single EM9305 PML_Init source body — 2026-11-11

The older controller candidate carried a second implementation of the stock
`PML_Init` routine at `0x30f4b0`. It had no source references but occupied
252 bytes in the linked EM9305 image. That duplicate and its unused helpers
were removed; the separately recovered C body remains linked as
`opencfw_em9305_stock_30f4b0`. The focused EM9305 build compiled 775/775
units and linked. The full G2 build compiled 4,880/4,880 enabled units with
no failures or duplicate strong symbols, and all seven strict links passed.
Only the EM9305 package changed in the new source bundle. The OTA candidate
still differs from the locked artifact. Evidence:
[`em9305-single-pml-init-20261111.json`](../evidence/em9305-single-pml-init-20261111.json).

## Authenticated codec KWS weights in a source bundle — 2026-11-11

The codec A model-weight input is now a declared 120,800-byte data asset
extracted from the authenticated locked codec component, with its source
offsets and SHA-256 recorded. `make -C g2 source-bundle` links all seven C
payload candidates and assembles the six-component OTA using this asset.
The candidate codec FWPK's full 129,964-byte KWS command-and-weight region
matches the locked component byte for byte. The trained-weight candidate has
158,191 equal same-offset codec bytes, versus 40,124 with the zero-weight
fixture. The outer 4,638,044-byte candidate still differs from the locked
4,301,227-byte artifact, and model behavior has not been tested. Evidence:
[`codec-a-trained-kws-source-bundle-20261111.json`](../evidence/codec-a-trained-kws-source-bundle-20261111.json).

## Touch reset-copy zero padding from linker source — 2026-11-11

The final `STOCK-BYTES` touch reset-copy unit held only seven zero padding
bytes. The linker now fills those three gaps with zero, and the superseded C
unit was removed. The focused touch build compiled 99/99 units and linked a
28,804-byte image byte-identical to the previous source candidate. The full
G2 manifest compiled 4,880/4,880 enabled units without failures or duplicate
strong symbols, and all seven strict links passed. Touch code completeness
and hardware behavior remain unverified. Evidence:
[`touch-source-zero-padding-20261111.json`](../evidence/touch-source-zero-padding-20261111.json).

## Apollo main shared state and initialized nonce — 2026-11-11

Five address-named Apollo state groups that previously had split C storage now
share their source-defined arrays: HCI radio result, HCI error, Nema frame
buffer context, three adjacent case reconnect/force-out flags, and the four
case nonce bytes. The nonce alias uses the existing initialized word
`0x0202ffff`, which emits the required `ff ff 02 02` startup bytes. The
separate reconnect and nonce units were removed. A focused Apollo-main build
compiled 2,717/2,717 units and linked; the full G2 manifest compiled
4,881/4,881 enabled units without failures or duplicate strong symbols, and
all seven strict payload links passed. This closes the bounded duplicate
allocations found in the address-named ELF symbols; broader RAM-layout and
hardware behavior remain unverified. Evidence:
[`apollo-shared-state-aliases-20261111.json`](../evidence/apollo-shared-state-aliases-20261111.json).

## Apollo main shared EasyLogger state — 2026-11-11

The EasyLogger event-flags handle and the transport free-list head now share
the same source-defined eight-byte state cell. Previously, the named handle
linked at `0x200a25dc` while the transport state linked at `0x200b4f50`;
the handle now aliases the latter, with the free-list head at offset four.
An Apollo-main build compiled 2,719/2,719 units and linked successfully. The
full G2 manifest compiled 4,883/4,883 enabled units with no failures or
duplicate strong symbols, and all seven strict payload links passed. This
corrects one split allocation; the other Apollo RAM-address inconsistencies
and hardware behavior still need review. Evidence:
[`apollo-logger-shared-state-20261111.json`](../evidence/apollo-logger-shared-state-20261111.json).

## Touch PDL ILO measurement and clock callback — 2026-11-11

The touch ILO compensation wrapper now calls the pinned PDL C measurement
functions used by the stock wrapper. Its reset-copied PM descriptor points to
the PDL clock deep-sleep callback. The separate hand-reconstructed ILO helpers
and callback were removed, and the four PDL state cells link at the stock RAM
addresses `0x20000f1c` through `0x20000f20`. A focused touch build compiled
100/100 units and linked its 28,804-byte candidate without duplicate strong
symbols. The full G2 manifest compiled 4,883/4,883 enabled units with no
failures or duplicate strong symbols, and all seven strict payload links
passed. Source completeness, stock equivalence, and hardware behavior remain
unverified. Evidence:
[`touch-pdl-ilo-callback-source-20261111.json`](../evidence/touch-pdl-ilo-callback-source-20261111.json).

## Touch deep sleep through pinned PDL C — 2026-11-11

The touch application now calls `Cy_SysPm_CpuEnterDeepSleep` from the pinned
Infineon PDL C source, matching the stock main call target. The separate
hand-reconstructed callback executor and deep-sleep routine were removed;
the local callback unit now checks only the reset-copy ABI. A focused touch
build compiled 101/101 units and linked without duplicate strong symbols.
The linked PDL function retains the callback root at `0x20000f34` and the
`wfi` path. The full G2 manifest compiled 4,884/4,884 enabled units with no
failures or duplicate strong symbols, and all seven strict source links
passed. Clang inlines its helper functions here, and the resulting
300-byte deep-sleep function does not match the stock 104-byte function.
Hardware behavior and whole-image byte identity remain unverified. Evidence:
[`touch-pdl-deepsleep-source-20261111.json`](../evidence/touch-pdl-deepsleep-source-20261111.json).

## Touch shared power-management callback RAM — 2026-11-11

The registered clock callback previously landed in the upstream PDL root
array at `0x20000f5c`, while the C deep-sleep path read the stock root at
`0x20000f34`. The linker now places the PDL root, failed-callback array, and
last-callback cell at their stock zeroed RAM addresses (`0x20000f34`,
`0x20000f28`, and `0x20000f24`). Both the BSP clock descriptor and the
application descriptor register through that single PDL function. The unused
duplicate C registrar was removed. A focused touch build compiled 101/101
units without failures or duplicate strong symbols, and its strict link
passed. The full G2 manifest compiled 4,884/4,884 enabled units without
failures or duplicate strong symbols, and all seven strict source links
passed. Deep-sleep behavior still needs hardware validation. Evidence:
[`touch-pm-shared-root-20261111.json`](../evidence/touch-pm-shared-root-20261111.json).

## Touch BSP deep-sleep callback registration — 2026-11-11

The touch BSP now passes its reset-copied callback descriptor at
`0x20000850` to the upstream `Cy_SysPm_RegisterCallback` implementation.
The C function returns zero on success and the stock `0x06020000` error on
failure. `cybsp_init` now calls generated initialization followed by that
registration, as the locked `0x4650` call chain does. The prior source only
returned success and made two reset-reason calls absent from the stock BSP
entry. A focused 101-unit touch build and strict link passed; the registration
function and PDL provider are both retained in the 29,000-byte image. The
full G2 manifest compiled 4,884/4,884 enabled units without failures or
duplicate strong symbols, and all seven strict source links passed. The whole
touch image and hardware behavior remain unverified. Evidence:
[`touch-bsp-pm-registration-20261111.json`](../evidence/touch-bsp-pm-registration-20261111.json).

## Touch EEPROM reset-copy source ownership — 2026-11-11

The touch image now links the typed, mutable 12-byte EEPROM configuration at
`0x200004c0` from `reset_owned_data.c` instead of copying a stock-byte array.
Its fields compile to the exact 12 bytes in the authenticated reset image.
Removing the duplicate `SystemCoreClock` from that unit allowed it into the
touch source composition without a duplicate strong symbol. A focused touch
build compiled 101/101 units and linked; the resulting 28,844-byte image is
byte-for-byte unchanged from the previous C candidate. The full G2 manifest
compiled 4,884/4,884 enabled units without failures or duplicate strong
symbols, and all seven strict source links passed. Overall touch image
identity and hardware behavior remain unverified. Evidence:
[`touch-eeprom-reset-copy-source-20261111.json`](../evidence/touch-eeprom-reset-copy-source-20261111.json).

## Touch CRT reset-copy hooks and exit path — 2026-11-11

The touch reset copy now carries C-linked init and fini function pointers at
`0x2000087c` and `0x20000880` instead of eight placeholder zero bytes. The
reset-entry C visits the one init entry after data and BSS initialization,
matching the locked image's empty preinit array and one-entry init array.
If the application returns, the C exit wrapper visits the optional cleanup
callback at `0x20000f54` and enters the terminal loop. The source hook bodies
have no work because this image has no TM clones.
The focused touch build compiled 101/101 units without failures or duplicate
strong symbols, and its strict link passed. The full G2 manifest compiled all
4,884 enabled units without failures or duplicate strong symbols, and all
seven strict payload links passed. The linked pointers resolve to
Thumb addresses in the new image; the 28,844-byte touch payload is 5,588
bytes shorter than the locked application and has not been tested on hardware.
Evidence: [`touch-crt-hook-source-20261111.json`](../evidence/touch-crt-hook-source-20261111.json).

## Codec A BINH stage-1 module lookup — 2026-11-11

The C module lookup at `0x10000160` now matches all 164 locked bytes. A
stage-1 copy of the pinned MIT-licensed SDK clock header changes only the
ordering of its direct-table candidate comparison and `info->param` clear;
the strict linker pins that header's digest and checks the function bytes.
A focused codec A build compiled 367/367 units and linked successfully. The
full G2 manifest compiled 4,884/4,884 units without failures or duplicate
strong symbols, and all seven strict payload links passed. The
exact clock-source and clock-gate functions remain unchanged; same-offset
agreement in the non-padding stage-1 load rose from 2,212 to 2,228 bytes.
Evidence: [`codec-a-stage1-module-lookup-20261111.json`](../evidence/codec-a-stage1-module-lookup-20261111.json).

## Codec A BINH stage-1 clock placement — 2026-11-11

The C clock-source leaf now links at `0x1000014c` and matches all 20 stock
bytes. Moving the module lookup to its observed `0x10000160` address, placing
the clock-gate and clock-frequency sections at `0x100005a4` and `0x100006a4`,
and pinning the switch tables at `0x10000f48` makes the 256-byte C clock-gate
function byte-identical to stock. The source linker checks both new exact
ranges. The 4,756-byte stage-1 load still has exact vectors and initialized
data; the remaining 7,504 bytes of the locked boot block are all zero and
the source wrapper pads that tail. Same-offset agreement in the non-padding
load rose from 1,476 to 2,212 bytes. The
module lookup matches 148/164 bytes, clock frequency 288/448, and switch
tables 203/224; their remaining differences need separate work. The fresh
full manifest build compiled 4,884/4,884 enabled G2 units with no failures
or duplicate strong symbols, and all seven strict source links passed. A
synthetic zero-weight OTA candidate authenticated against the locked bundle
remains different in all six components; the codec component's same-offset
agreement rose from 39,052 to 40,108 bytes.
Evidence:
[`codec-a-stage1-clock-placement-20261111.json`](../evidence/codec-a-stage1-clock-placement-20261111.json).

## Codec A BINH stage-1 XIP divider call — 2026-11-11

The locked flash-reader path calls unsigned division with arguments 24 and 4,
shifts the result by four, and ORs it with `0x08c09406` before programming
XIP control. The source now expresses that call through the existing C helper
instead of hard-coding the folded `0x08c09466` value. A focused codec A build
compiled 367/367 units and its strict link passed. The stage-1 load still fits
at 4,756 bytes, with the 254-byte stock-matched SPI function range preserved.
The C reader now occupies 536 bytes including its literal pool, the same span
as the locked reader, but its bytes and location still differ.
The divider helper has not been placed at its stock address, so the complete
reader remains a source candidate. Evidence:
[`codec-a-stage1-xip-divider-20261111.json`](../evidence/codec-a-stage1-xip-divider-20261111.json).
A separate ignored linker probe placed the 536-byte reader at its stock address
but matched only 41 bytes there; the production layout was not changed for
that probe. See
[`codec-a-stage1-reader-placement-probe-20261111.json`](../evidence/codec-a-stage1-reader-placement-probe-20261111.json).

## Codec A BINH stage-1 SPI helper placement — 2026-11-11

Five existing C-compiled functions now occupy their locked addresses from
`0x10000b40` through `0x10000c3e`: clock status, SPI idle wait, flash write,
flash transaction, and flash ready wait. All 254 function bytes match the
authenticated codec component at those addresses. The source linker checks
that range and the two previously placed SDK helper ranges on each BINH A
stage-1 link. A focused codec A build compiled 367/367 units without failures,
duplicate strong symbols, or unresolved symbols; its strict link passed.
The source load remains 4,756 bytes with exact vectors and initialized data.
The full G2 manifest then compiled 4,884/4,884 enabled units without failures
or duplicate strong symbols, and all seven strict source links passed.
The other stage-1 code and complete codec payload remain unverified. Evidence:
[`codec-a-stage1-spi-placement-20261111.json`](../evidence/codec-a-stage1-spi-placement-20261111.json).

## Codec A BINH stage-1 C helper placement — 2026-11-11

The C-compiled SDK helpers `__reg_set_val` (18 bytes) and
`__module_get_div.isra.1` (28 bytes) now link at their locked BINH A stage-1
addresses, `0x10000138` and `0x10000204`, with exact stock function bytes.
The intervening source module lookup is placed to fit the bounded boot
block but does not match stock. The 4,756-byte source load still has exact
vectors and initialized data. A fresh manifest build compiled 4,884 enabled
units with zero failures or duplicate strong symbols. All seven strict source
links and the synthetic six-component candidate build passed; the complete
codec and outer OTA remain different from stock. Evidence:
[`codec-a-stage1-helper-placement-20261111.json`](../evidence/codec-a-stage1-helper-placement-20261111.json).

## Authenticated six-component candidate comparison — 2026-11-11

The repeatable comparison tool authenticates the locked manifest and each
official component against `g2/workflow/target.json`, validates the source
candidate's EVENOTA structure and link receipt, and reports per-component
size and same-offset byte differences. None of the six candidate components
is byte-identical. The codec's 9,164-byte KWS command window is exact; its
weight input is still synthetic. The source candidate is 295,664 bytes larger
for Apollo main, 36,748 larger for EM9305, 5,633 larger for the bootloader,
4,416 larger for case, and 5,644 smaller for touch. These are placement and
compiler diagnostics, not a classification of missing executable code.
Evidence: [`g2-source-candidate-comparison-20261111.json`](../evidence/g2-source-candidate-comparison-20261111.json).

## Six-component source OTA candidate — 2026-11-11

The strict source linker now assembles all seven linked G2 payload candidates
into a six-component EVENOTA candidate, combining codec A and B into one FWPK.
It uses recovered container metadata and recomputes sizes and CRCs; it reads
no official component bytes during assembly. A synthetic, all-zero codec
weight fixture exercised the complete path. Structural validation passed for
the 4,638,044-byte candidate, but it differs from the locked 4,301,227-byte
artifact and has no functional trained model. It is not a release or evidence
of source completeness. The source-linked Apollo main, EM9305 and case images
also differ in size from stock. Evidence:
[`g2-source-candidate-bundle-20261111.json`](../evidence/g2-source-candidate-bundle-20261111.json).

## Codec A candidate packaging from source regions — 2026-11-10

The strict G2 source linker can now assemble its separately linked BINH A
stage-1, XIP, and SRAM loads with the C-generated KWS command stream into a
BINH A candidate when given a 120,800-byte weight asset and matching JSON
SHA-256 provenance. If codec B is selected in the same run, it also packages
the UART and BINH images into a codec FWPK candidate. A synthetic all-zero
weight fixture in ignored `build/` exercised both wrappers; the output's NPU
command and weight windows matched their declared inputs, and an incorrect
weight digest was rejected before linking. This establishes the packaging
path only. The repository still lacks a sourced trained model, and the
resulting synthetic image is not a functional firmware release. Evidence:
[`codec-a-source-candidate-packaging-20261110.json`](../evidence/codec-a-source-candidate-packaging-20261110.json).

## Codec A KWS command corpus — 2026-11-10

Field-level C descriptors and encoders under `g2/src/codec/npu/` now cover
all 212 commands in the locked 9,164-byte GXNPU KWS stream. The host C oracle
compares every emitted record and the assembled stream with the authenticated
codec firmware. `make -C g2 kws-command-stream` writes this stream from the C
sources under `build/` without reading the official firmware. The seven-payload
strict source link also emits it as a separate codec A source region. These source
units remain compile-only while the 120,800-byte
trained weight block lacks a declared source. Some command control-bit and
geometry-axis meanings remain unresolved. This command-stream match does not
qualify the codec executable, BINH A, FWPK bundle, or hardware behavior.
Evidence: [`codec-a-kws-command-corpus-20261110.json`](../evidence/codec-a-kws-command-corpus-20261110.json).

## Codec BINH A stage-1 source link — 2026-11-10

The BINH A stage-1 tree now includes C candidates for clock initialization,
clock trim and frequency policies, timer configuration, unsigned division,
oscillator control, and initialized boot state. Its nine source units compose
and link into a separate boot image at `0x10000000`, without an undefined
symbol. The 4,756-byte source load fits the locked 12,260-byte stage-1 limit.
Its 256 vector bytes and 620 initialized-data bytes at
`0x20001028..0x20001294` match stock exactly. The code does not match stock;
the candidate is not hardware-qualified. BINH A XIP and SRAM still exceed
their locked spans, and source NPU weights are missing, so a
complete source BINH A or FWPK cannot yet be built. Evidence:
[`codec-a-stage1-source-link-20261110.json`](../evidence/codec-a-stage1-source-link-20261110.json).
The stable full manifest build compiled 4,877/4,877 enabled G2 units with no
failures or duplicate strong symbols. All seven strict source links passed
without an external binary archive; the existing codec A UART image remained
unchanged while its separate BINH A stage-1 candidate was added.

## Codec BINH A stage-1 reset and boot dispatch — 2026-11-10

Added C-compilable source for the BINH A stage-1 vector table, naked reset
entry, default handler, boot setup, audio gate, boot-mode read, clock status
and setup, and timer-start wrapper. The 64 stock vector words point to reset
at `0x10000100` and the default loop at `0x10000130`. The default handler,
return-only leaf, and clock-status leaf compile to the exact stock bytes.
The other six measured function bodies have the stock lengths and match
outside call or address relocations. A relocatable composition of the seven
stage-1 C units leaves clock initialization, timer configuration, and the
image-A SRAM reset symbol external; the SRAM reset already has C source in
the codec A tree. The stage-1 block is still excluded from the final codec A
link. Evidence: [`codec-a-stage1-startup-boot-c-review-20261110.json`](../evidence/codec-a-stage1-startup-boot-c-review-20261110.json).
The stable full manifest build compiled 4,875/4,875 enabled G2 units with
zero failures or duplicate strong symbols. All seven strict source links
passed without an external binary archive, and the linked codec A binary is
unchanged.

## Codec BINH A stage-1 clock gate — 2026-11-10

Reconstructed the stage-1 `0x100005a4` clock-gate dispatcher from the pinned
GRUS clock policy. Its 256-byte C-SKY function body has the stock length and
matches stock outside two literal-address relocations and two calls to the
module descriptor lookup helper. The helper compiles to the stock 164-byte
length but has a different instruction schedule near its entry. Composing
the clock gate with the C loader, NOR reader, and SPI transactions leaves no
undefined symbols. This proves closure only for those candidate units; the
complete BINH A stage-1 boot block remains unlinked and unverified.
The stable full manifest build compiled 4,872/4,872 enabled G2 units with
zero failures or duplicate strong symbols; all seven strict source links
passed without an external binary archive. The codec A linked binary is
unchanged because these stage-1 candidates remain `link:false`.
Evidence: [`codec-a-stage1-clock-gate-c-review-20261110.json`](../evidence/codec-a-stage1-clock-gate-c-review-20261110.json).

## Codec BINH A stage-1 SPI transactions — 2026-11-10

Added C candidates for the locked BINH A stage-1 SPI write at `0x10000b5c`
and read at `0x10000bbc`. Each compiles to 96 bytes, the stock function
length. Comparing their object sections with the locked stage-1 load leaves
only the two call relocations to the bus-busy poll in each function; all
other bytes match. Composing these functions with the loader and NOR reader
resolves both SPI references. The separately reconstructed clock-gate
dispatcher closes this candidate call graph. These units are
still excluded from the final codec A link, and BINH A stage 1, its NPU
payload, and the complete FWPK are not source-built or hardware-qualified.
Evidence: [`codec-a-stage1-spi-transactions-c-review-20261110.json`](../evidence/codec-a-stage1-spi-transactions-c-review-20261110.json).

## Codec stage-1 flash readers — 2026-11-10

Added a C BINH A NOR reader candidate at `0x10000c40`, including JEDEC
handling, XIP setup and a 64 KiB SPI chunk loop. Its bus-busy poll compiles
to the exact 16 stock bytes. Its 34-byte status-ready poll matches stock
except for the unresolved call relocation. Together with the preceding C
loader, the new reader resolves the loader's flash-read reference; clock
gating and the two SPI transaction functions remain separate missing source
dependencies. The BINH A units remain `link:false` and have not been checked
on hardware. Evidence:
[`codec-a-stage1-reader-c-review-20261110.json`](../evidence/codec-a-stage1-reader-c-review-20261110.json).

The locked BINH B reader initializes SPI when its cached JEDEC word equals
`0x00ffffff`. Its linked C candidate had the condition reversed even though
the initial cached word is that sentinel. Correcting the branch changed one
byte in the 6,764-byte stage-1 load. A host check covers both sentinel and
non-sentinel paths. The 94,352-byte source BINH B package now has SHA-256
`8cd3cb7ce492b974c2fa1e86903b367fbc6f94f1c9c8efd29b0cb678669e676e`;
it still differs from stock and is not hardware-qualified. Evidence:
[`codec-b-jedec-branch-correction-20261110.json`](../evidence/codec-b-jedec-branch-correction-20261110.json).

The full manifest build compiled 4,870/4,870 enabled units with zero
failures or duplicate strong symbols, and all seven strict source links
passed without an external binary archive.

## Codec BINH A stage-1 loader C — 2026-11-10

Added a C candidate for the locked BINH A NOR scatter loader at
`0x10000a2c`. The normal branch reads the XIP length at `package+0x3000`,
copies 14,716 bytes to `0x10023400`, and enters `0x10023500`. The alternate
`0xaabbccdd` marker branch reads at `package+0x323b0`, then copies 82,060
bytes from `0x323b4+xip_length` to `0x20003000` and enters `0x10003100`.
Those addresses and branch shapes come from the locked stage-1 disassembly.
The host branch-plan check and direct C-SKY compilation pass; the focused
codec A manifest build compiled 352/352 units, and its final linked binary
is unchanged. The new unit remains `link:false` while its flash reader and
the rest of BINH A stage 1 are reconstructed. The full G2 manifest build
compiled 4,869/4,869 enabled units with zero failures and duplicate strong
symbols; all seven strict source links passed without an external binary
archive. See
[`codec-a-stage1-loader-c-review-20261110.json`](../evidence/codec-a-stage1-loader-c-review-20261110.json).

## Codec image-A reset entry moved to C — 2026-11-10

Replaced the standalone image-A SRAM reset assembler unit with a naked C
translation unit. Its CPU control and stack instructions remain inline C-SKY
assembly, because they run before a C stack exists. The C unit emits the same
44 bytes as the superseded assembler section, including the exception bridge.
The focused 351-unit codec A build and final link passed; its flat binary,
UART stages, image-A regions and UART candidate package are byte-for-byte
unchanged. The full 4,868-unit G2 build and seven strict source links also
passed, with zero failures, duplicate strong symbols or external binary
archive. Apollo main differed between full build directories because six
generated LVGL objects embed their build path; its source hashes did not
change. This reproducibility gap is separate from the codec reset conversion.
See
[`codec-a-reset-c-conversion-20261110.json`](../evidence/codec-a-reset-c-conversion-20261110.json).

## Codec BINH A source boundary — 2026-11-10

The codec A source ELF already contains image-A XIP and SRAM code. The strict
link now extracts both load regions and reports their stock capacity checks.
XIP is 46,764 bytes against 36,484 stock bytes; SRAM is 14,940 against
14,716. The source SRAM vector table resets at the stock `0x10023500`, but its
exception and IRQ entries point to `0x1002351e` and `0x1002575c` instead of
the stock `0x10023640` and `0x10025574`. A garbage-collection probe reduced
XIP to 31,376 bytes while discarding 54 named stock XIP functions, so it was
not adopted.

The new BINH A and codec FWPK builders reproduce the locked bytes from stock
inputs. They reject an over-limit source image; there is still no C BINH A
stage-1 block or source NPU command/weight payload. All seven strict source
links continue to pass. Evidence:
[`codec-a-binh-source-boundary-review-20261110.json`](../evidence/codec-a-binh-source-boundary-review-20261110.json).

## Codec BINH B stage-1 source link — 2026-11-10

The eleven existing BINH B stage-1 C units were compilable but excluded from
the codec B composed object. Their profile emits shared `.text`/`.data`
sections, so merging them with image B stage 2 placed boot code in the later
image and exceeded its stock SRAM bound. The final-link path now verifies
those eleven object hashes, composes a separate stage-1 object, and maps it
into the `0x10000000` boot block. The stage-1 vector table matches stock
byte-for-byte, with reset at `0x10000100` and default handler at
`0x10000130`. Stage-1 initialized data loads at `0x10001720` with a D-bus
view at `0x20001720`. Image B stage 2 still starts at `0x10003000` and ends
at `0x10016ec0`, below the locked `0x1001708c` bound.

The source link now wraps the 6,764-byte stage-1 load and 81,600-byte stage-2
load into a 94,352-byte BINH B candidate, computing its stage-1 CRC-32/MPEG-2.
The wrapper reproduces the locked BINH B bytes exactly when given the locked
stage inputs. The source candidate is different and remains unverified on
hardware. The full manifest build compiled 4,868/4,868 enabled units with
zero failures and duplicate strong symbols; all seven strict source links
passed without an external binary archive. See
[`codec-b-stage1-source-package-review-20261110.json`](../evidence/codec-b-stage1-source-package-review-20261110.json).

## Codec UART stage-2 vectors and source segment — 2026-11-10

The codec A source image now has a 64-word UART stage-2 vector table at
`0x10002800`, reset at `0x10002900`, exception-frame entry at `0x10002950`,
exception bridge at `0x10002994`, and common IRQ entry at `0x10003124`.
The table's 256 bytes and the bridge instruction match the locked UART stage
byte-for-byte. The naked C exception entry follows the stock frame sequence;
66 of its first 68 bytes match stock, with differences in a literal load and
the C report call. The C ISR uses the same VIC active-vector field and
`0x2000984c` callback table, but its floating-point save sequence differs.
The source trap report emits the register groups through the source UART sink;
its output and interrupt behavior have not been compared on hardware.

The source linker now extracts both UART stages and builds the type-1 GX8002
boot segment with its fixed-length padding and computed additive checksum.
The stock stages reproduce the stock 38,236-byte segment exactly through the
same builder. The linked source stages are 9,408 and 24,158 bytes; they are
shorter than the stock 10,240 and 27,964 bytes, and the source candidate is
not stock-identical. The codec BINH images and NPU command/weight payload
still lack a source-built FWPK package. See
[`codec-uart-source-segment-review-20261110.json`](../evidence/codec-uart-source-segment-review-20261110.json).
The subsequent full manifest build compiled every selected G2 unit with no
failures or duplicate strong symbols, and all seven final source links passed
without an external binary archive; that receipt does not establish a
complete codec FWPK or hardware boot.

At the earlier audit, BINH B stage-1 source was outside the final link: its
11 C units were registered with `link:false`, and the codec B ELF contained neither their
`.spl.vectors` section nor their reset symbol. A source link must place those
units in the separate `0x10000000` stage-1 boot block before BINH B can be
packaged. The later section above records that source link and package. See
[`codec-b-stage1-link-gap-20261110.json`](../evidence/codec-b-stage1-link-gap-20261110.json).

## Codec UART stage-1 boot vectors — 2026-11-10

The source-linked codec A ELF had code at IRAM `0x10000000`, where the locked
FWPK UART stage 1 has a 64-word vector table. Its reset function was at
`0x10000eb4` instead of the vector's `0x10000100`. A C vector-table unit now
owns the first 256 bytes, and the linker pins reset, exception and IRQ trap
entries at `0x10000100`, `0x10000130` and `0x10000134`. All 256 vector bytes
and the two trap entries match stock; the source reset body does not. The
focused codec A build compiled 348/348 units, linked with zero undefined
symbols, and its stage-1 load image is 9,408 bytes versus 10,240 stock bytes.
See [`codec-uart-stage1-vector-review-20261110.json`](../evidence/codec-uart-stage1-vector-review-20261110.json).

The existing stage-2 reset function was also collected into stage 1 because
its symbol is named `gx8002_uart_stage1_second_entry`. It now has a dedicated
section and links at the stock stage-2 reset address `0x10002900`, with a
linker assertion. At this intermediate checkpoint the source stage-2 load
still started there, rather than at the stock vector base `0x10002800`.
The later stage-2 vector and handler work is recorded above. See
[`codec-uart-stage2-reset-review-20261110.json`](../evidence/codec-uart-stage2-reset-review-20261110.json).
Neither UART stage nor the codec BINH/NPU payload is qualified as a complete
source-produced FWPK image.

## Source package boundary audit — 2026-11-10

The touch image is linked at flash `0x3300`, but the FWPK wrapper previously
validated its reset vector against an address-zero image. That rejected the
source reset vector `0x9929` even though it is within the linked image. Both
the wrapper and validator now use the actual application flash base. The
source package path adds the touch controller's reflected CRC-32C footer to
the linked flash bytes, then the FWPK record and its independent CRC. The
stock touch payload still round-trips, and a regression test rejects an
out-of-range vector.

The seven-payload source link now emits wrapped source candidates for Apollo
main, case and touch in addition to the EM9305 record package. The touch
candidate is 28,820 bytes versus the 34,464-byte locked payload, so this is
format closure, not source completeness or byte identity. At that checkpoint,
codec A/B remained separate linked images and no source-built codec BINH or
NPU command and weight payload had been established. The later BINH B source
candidate is recorded above. See
[`touch-source-package-review-20261110.json`](../evidence/touch-source-package-review-20261110.json)
and `build/g2-all-packaging-link-20261110/link-report.json`.

## EM9305 record coverage audit — 2026-11-10

The current final-link check proves a source-linked **application** at
`0x00302400`, not a complete EM9305 firmware package. The authenticated stock
package also has 224 bytes at `0x00300000`, 656 bytes at `0x00300400`, and a
56-byte `FHDR` record at `0x00302000`. At the time of that audit, none of those
three records had a source-linked producer. The EM9305 datasheet places NVM bootloader stages
before the optional EM-Core and application, so the first two records cannot
be treated as disposable packaging. The `FHDR` contains an address field
`0x00302028`. The local SDK's public header layout and stock CRCs now establish
that this is the NVM entry address. The stock
record wrapper round-trips byte-for-byte with the existing parser, but this
does not create the record sources. Record hashes, addresses, the linked-app
scope, and qualifications are in
[`em9305-record-coverage-20261110.json`](../evidence/em9305-record-coverage-20261110.json).

The subsequent source record 2 and NVM bootloader candidate work is described
below. A zero-undefined application ELF alone does not close EM9305 firmware
coverage.

## EM9305 source record 2 — 2026-11-10

The local SDK's public `firmwareHeaderV0_t` defines the stock record 2 as a
40-byte `FHDR` followed by a 10-byte ARC NVM entry and six erased bytes.
The entry loads the stock stack top `0x80f978` and branches to the C boot loop.
The source header and entry now live in
`g2/src/em9305/boot-header/nvm_header_entry.c`, with a linker section fixed at
`0x302000`. `tools/build/em9305_record2.py` fills the firmware size and two
CRC-32 fields after linking; the CRC algorithm and span reproduce the locked
stock record exactly when given the stock entry and application. A probe link
generated a 56-byte record 2 from source without changing the 247,364-byte
source-linked application. The full seven-payload manifest build compiled
4,863/4,863 units with no duplicate strong symbols, and all seven strict
source links passed with no external binary archive. Receipts:
`build/g2-all-record2-20261110/report.json` (SHA-256
`7d7915b19ea63cacf21d9c3d469ca5ad551e3bb628b18aff555fbefea0b3cde2`)
and `build/g2-all-record2-link-20261110/link-report.json` (SHA-256
`c60478e78261beffffe868daa5e52a7982e10b0d905d80f5e0a7fbecec35d3c1`).

## EM9305 NVM bootloader source candidate — 2026-11-10

The authenticated records at `0x300000` and `0x300400` contain the NVM
bootloader entry, firmware-header accessors, CRC checking, header enumeration,
and execution selection. The local vendor SDK v4.6 symbolized ELF and public
headers identify these functions at the same addresses as the stock
disassembly. `g2/src/em9305/bootloader/nvm_bootloader.c` now implements that
path in C, linked at `0x300000` ahead of the source FHDR and application.
The source package builder emits one contiguous C bootloader record rather
than copying the two stock records, followed by the FHDR and application.

A host check loaded the four authenticated stock records into a simulated NVM
array. The C header search found `0x302000`, the firmware CRC passed, and
single-byte mutations to the payload and header were rejected. This checks
those routines against the stock image; it does not establish equivalence of
the boot-selection and reset paths, byte identity, or successful hardware boot.
The new source package is a candidate and must not be treated as a release.
The final focused EM9305 build compiled 775/775 units with no duplicate strong
symbols and linked with no undefined symbols. The source bootloader is 736
bytes at `0x300000`; record 2 remains 56 bytes, and the 247,364-byte
application is unchanged from the preceding source link. The three-record
source candidate package is 248,272 bytes. The same host check passed on that
package. Receipts are
`build/g2-em9305-bootloader-final-20261110/report.json` (SHA-256
`5f7c09ae56eba699de79a2e7ba99e113e93eed259be309b55be52c2c0f461d6c`)
and `build/g2-em9305-bootloader-final-link-20261110/link-report.json`
(SHA-256 `42c278804226cd8db662a682a3b707404b160beb239c9e1042e73fa3c0f4dcec`).
The final all-payload manifest run compiled 4,864/4,864 units with zero
failures and duplicate strong symbols. Seven final ELFs linked with zero
undefined symbols and no external binary archive. Receipts:
`build/g2-all-bootloader-final-20261110/report.json` (SHA-256
`dd7f883fa38b248f65a7002e98628e1ded88069aff15d9b7ffcc1ab6601c7f87`)
and `build/g2-all-bootloader-final-link-20261110/link-report.json`
(SHA-256 `1aa13e07395e87848dee3854ad1afd800fb40823f3deca9c88bc01ad29ec7904`).

## EM9305 boot-selection fidelity revision — 2026-11-10

The preceding 736-byte candidate selected a section by fixed priority and
left the PML boot-mode bits unchanged before entering the application. The
authenticated ARC disassembly instead gates CRC checks on reset flags, chooses
among updater, EM-Core, customer application and customer bootloader according
to PML mode bits, and updates those bits on fallback or application entry.
`bootloader/nvm_bootloader.c` now follows that observed sequence. It also
implements the stock `getNextPageIfHeaderAddress` rule, and its
`jumpToFunction` compiles to a direct ARC register jump.

The host check mapped both the authenticated four-record package and the
source candidate into an NVM array. It verified the header and firmware CRCs,
rejected separate header and payload mutations, and exercised application,
updater, EM-Core and bootloader selection across the observed PML modes and
CRC gate states. At this checkpoint the expected outcomes were transcribed
from the stock disassembly; the stock-code differential follows below.
The revised focused build compiled 775/775 units, linked with zero undefined
symbols, and produced a 1,160-byte C bootloader and a 248,696-byte three-record
candidate package. Its application and record 2 hashes remain unchanged.
Receipts: `build/g2-em9305-selection-final-20261110/report.json` (SHA-256
`7b915068e6e014b52ca14cce7f4469ca352c7a67a35984cd3361f2904db0507e`)
and `build/g2-em9305-selection-final-link-20261110/link-report.json` (SHA-256
`6a9a25d639c38aaec62abf39bb74fdce7382d06b97be1af067db77e443a4ead7`).
Physical boot and byte identity remain unverified.

### CRC-option correction and stock-code differential

The expanded QEMU ARC run reached the authenticated stock `checkCRCHeader`
with the normal option-0 G2 header. It called payload verification, exposing
an inverted condition in the C candidate: firmware option bit 8 **skips**
payload CRC verification. The C condition was corrected, so the ordinary
source image now checks the payload before boot. A host check verified the
source CRC against both stock and source packages and rejected a changed
payload; setting bit 8 skipped the check as the stock branch does.

The one-off QEMU ARC harness then called the authenticated stock record code
and the C code with identical NVM entries and PML state. Their outputs matched
across 155 cases covering section combinations, boot modes, reset-flag/CRC
gates, next-page handling and header-entry storage. The stock CRC instruction
is unsupported by this QEMU build, so the QEMU differential uses bit 8 to
skip that instruction; the payload CRC result is supported by the separate
host check. A second QEMU run loaded the complete source FHDR/application
span, retained the valid header entry after CRC verification, then rejected
that entry after one application byte was changed. Matching these functions
does not prove the whole bootloader or physical boot. The exact result is in
`g2/evidence/em9305-boot-selection-review-20261110.json`.
The current all-payload build compiled 4,864/4,864 units with zero failures
and duplicate strong symbols, then linked seven final ELFs with zero undefined
symbols and no external binary archive. The revised bootloader is 1,160 bytes;
the three-record source candidate package is 248,696 bytes. Receipts:
`build/g2-all-selection-final-20261110/report.json` (SHA-256
`40d1c2b71cf380829abf49e484b31b7f9fb74262e286a4222df97ae328225b80`)
and `build/g2-all-selection-final-link-20261110/link-report.json` (SHA-256
`450ef4664598f050ec83ab8ea9e26d26f161e710df7a3c288793ccef67dd1711`).

## Source-only fuel-gauge candidate — 2026-11-10

Apollo main now has a C provider for the five Nordic fuel-gauge API calls it
uses. The address-named shim forwards to this provider, and the final-link
tool no longer loads the Nordic binary archive. Its state of charge estimate
uses measured voltage and current with the stock firmware's 80 mAh design
capacity; the voltage curve is an **uncalibrated development estimate**. The
proprietary Nordic algorithm and undocumented EVENBAT model parameters were
not reconstructed. This is a source-only compilation milestone, not a
stock-equivalent battery implementation or permission to flash hardware.

The full G2 source build compiled 4,862/4,862 enabled units with zero compile
failures or duplicate strong symbols. All seven final ELFs linked with zero
undefined symbols and without an external binary archive. The exact aggregate
build and link receipts are in `build/g2-all-source-20261110/` and
`build/g2-all-source-link-20261110/`. A host-side contract check covered
initialization, charge and discharge direction, invalid input, and finite
time estimates. The exact final Apollo-main binary reached BLE advertising in
the lenient Renode model: 56 HCI host packets, byte-for-byte the same sequence
as the earlier archive-linked baseline. The durable hashes and qualifications
are in [`g2-source-only-link-20261110.json`](../evidence/g2-source-only-link-20261110.json).

Goal: complete compilable C with open toolchains; byte identity is not required
for this user-authorized campaign. Historical workflow gates/evidence remain unchanged.
EvenHub SDK is excluded. Compilation and relocatable composition do not prove
complete firmware, final linkage, or hardware operation.

## Historical payload inventory (2026-10-26 baseline)

| Payload | Registered units | Assembly syntax | Opaque markers | Candidate/unverified triage | Unresolved (report scope) |
| --- | ---: | ---: | ---: | ---: | ---: |
| apollo-main | 2835 | 172 | 17 | 2775 | 131 |
| apollo-bootloader | 381 | 205 | 4 | 381 | 3 |
| case | 408 | 106 | 3 | 407 | 0 |
| touch | 78 | 8 | 0 | 76 | 30 |
| codec-a | 344 | 35 | 4 | 322 | 5 |
| codec-b | 332 | 29 | 3 | 319 | 3 |
| em9305 | 618 | 489 | 0 | 618 | 37 |

Full per-payload unit lists, assembly/opaque unit paths, candidate/unverified paths,
and unresolved symbol lists are in
[`c-reconstruction-inventory.json`](../evidence/c-reconstruction-inventory.json).
Counts are per manifest unit, including shared units compiled into both codecs.
Assembly and opaque counts are conservative lexical triage, not an exhaustive
classification of executable bytes. Candidate/unverified is a review backlog,
not a count of proven incorrect bodies. Exact inferred-body count is unknown.
Composed ARM unresolved lists come from nm; object-only lists are definition-subtracted.

Baseline: `g2/evidence/source-build-goal-validation.json` and its referenced
full-tree/flash reports; fresh wave report supersedes payloads when available.
Codec A/B and EM9305 have object-scope unresolved counts (no composition).
Case zero unresolved does not establish source completeness.

## Coverage evidence and gaps

- Function ownership/frontiers: `g2/symbols/*.tsv`,
  `g2/tools/manifests/g2-case-final-function-frontier.tsv`,
  `g2/tools/manifests/g2-case-final-gap-frontier.tsv`.
- Existing pseudocode: `g2/research/corpus/*/ghidra/`; exports are not a
  reviewed, frozen, complete corpus.
- Historical audits: `g2/build/audits/2026-10-06-current-assessment-refresh/`
  and `g2/build/pseudocode-first/20260930T190500Z/`. They retain unknown regions,
  nested codec images, compressed initialization, and code/data ambiguity.
- Source unit counts do not cover all firmware functions. No whole-artifact
  C completeness percentage is established.

## Wave 01 — 2026-10-26

- Created this ledger and machine-readable per-payload backlog.
- Recovered missing RTC weekday helper at `0x004d3cf8` with REA/Ghidra 12.1.4;
  body hash matches authenticated pseudocode corpus. Recovered both month tables.
- Added one freestanding C unit, preserving invalid-input handling, wrapping
  arithmetic, signed remainder, and stock's unusual century/leap condition.
- 12,240 ARM-emulated stock/C comparisons passed, zero mismatches.
  Receipt: `g2/evidence/rtc-weekday-review.json`; harness/output under
  `build/g2-c-wave-01/`. This is bounded behavioral evidence, not hardware proof.
- Added G2-only `sources` and `sources-check` targets to `g2/Makefile`.
  `./g2/make.sh sources-check`: 4,996 units, 4,708 files, zero not built.
- Build: `./g2/make.sh sources SOURCES_OUT=build/g2-c-wave-01/sources`.
  Result pending; see `build/g2-c-wave-01/build.log`.
- Upstream shortcut triage: existing manifest already integrates LVGL, FreeType,
  FreeRTOS and vendor providers. No new dependency version is asserted or vendored
  without a fresh match. This wave closes a missing first-party helper instead.

## Historical unresolved checklist (2026-10-26 baseline)

- [ ] Complete full G2 source build and record fresh counts.
- [ ] Close Apollo-main unresolved functions, data, runtime and linker symbols.
- [ ] Close bootloader's three remaining dependencies with provenance.
- [ ] Classify/close touch's 30 dependencies (including ROM/external boundaries).
- [ ] Compose codec A/B and EM9305 with open-toolchain startup/link layouts;
      close respective object-scope unresolved lists (5/3/37 baseline).
- [ ] Convert assembly/opaque executable providers to C where technically possible;
      explicitly account for unavoidable architecture entry/interrupt intrinsics.
- [ ] Review/replace inferred bodies; candidate backlog is not resolved by compiling.
- [ ] Account for every executable region/nested image and all required resources.
- [ ] Produce final linked payload images/bundle from complete C and validate behavior.

## g2c session (2026-10-26) — Apollo-main closure and first GNU link

All uncommitted. Tooling: `.waves/bm.sh` (rebuild into `g2/build/g2c-wave`),
`.waves/promote.py` (flip `link:false` units that fill unresolved symbols
without a strong clash), `.waves/link.sh` (arm-none-eabi-gcc final link into
`g2/build/g2c-link/`, undefined list in `.waves/link-undef.txt`),
`.waves/iarlz.py` (decodes the stock IAR LZ77 init rows to `.waves/init_*.bin`).

Apollo-main composed unresolved: 130 (original baseline) -> 104 (session start)
-> 33 now (includes 10 linker-script symbols and 3 intentionally-weak IAR stdout
selectors). 0 duplicate strong symbols throughout. Final GNU link: 50 -> 19
undefined.

Closed this session:
- Cordio svc_core/svc_dis wrappers around upstream with stock AddGroup bodies;
  AttsRemoveGroup stubbed (pinned atts_main.c has it `#if 0`; stock never calls it).
- AmbiqHAL clkmgr (rename wrapper), pin, mcuctrl from upstream ambiqhal-apollo510;
  spotmgr leaves decompiled (stock is an older AmbiqSuite than upstream).
- dmGetConnParamPtr and ~30 other defsyms (spotmgr, pwrctrl, display flush,
  wear detect, NEMA rectangle, FreeRTOS first-task entry).
- ~69 `link:false` candidate units promoted to link (graphics buffer handlers,
  display driver, SMP rows). These are candidate-quality and need review.
- GNU runtime: `runtime/g2c-gnu/g2c_vectors.c` (151-entry table from stock),
  `g2c_gnu_init.c` (IAR-row-compatible init table), `link/g2-apollo-main.ld`.
- First-party data (`runtime/g2c-data/g2c_first_party_data.c`): shell buffers,
  FAL flags, appdb table pointer, LVGL level names, role strings, menu icon,
  B2S eDMP image (from decoded stock init data), dashboard-ext rx record.
- Port leaves (`runtime/g2c-data/g2c_port_leaves.c`): OS_Tick_*, elog_port_deinit.
- Upstream InvenSense `sif_feature_extract_ir.c` (SIF_* initialisers).
- BLE leaves (`ble/g2c-leaves/g2c_ble_leaves.c`): AppDbRecordInUse,
  paired count, AppDiscRegister, AT radio reset.
- NEMA leaves (`graphics/g2c-nema/g2c_nema_leaves.c`): set_gradient(_fx),
  interpolate_rect_colors, nema_init.

Still undefined at link (19):
- nrf_fuel_gauge_* (8) + g2_npm1300_battery_model: Nordic binary-only library
  under LicenseRef-Nordic-5-Clause (forbids reverse engineering). Not
  decompiled; needs an owner decision (obtain Nordic .a, clean-room estimator,
  or leave unresolved).
- Ambiq LVGL draw units (9: arc, border, box_shadow, fill, line, mask,
  triangle, vector_shape, label). Upstream `ambiq-lvgl/src/draw/ambiq/*` exists
  but needs NemaGFX headers/library (third-party/upstream/ambiqhal-nema is empty).
- nema_vg_init_stencil_prealloc_522400 (pulls a large nema_vg context reset).

Open guesses (flagged in code): DIS 0x20003AC4 = disValSn; dual clkmgr state;
10 vector slots bound to a spin handler (0x442114, 0x4b80be, 0x4c9d44, 0x4d58a6,
0x504488, 0x57a4d8 I2S, 0x57b940, 0x5b0114, 0x5fa0c8, 0x5fa120); linker script
ignores the 67 fixed-address `*.ld` fragments; LVGL level-name slot 5 = NULL;
OS_Tick/elog deinit semantics from upstream not stock; NEMA default context size
0x100; pwrctrl enable/disable mapping (stock names "irq_off"=enable,
"irq_on"=disable by bit behaviour); profile_handler_entry 0x5fa056 aliased to
vRestoreContextOfFirstTask (stock value is 2 bytes before it).

## g2c wave 3 (2026-10-26) — ambiq draw, NemaGFX raster, fuel gauge

Link status: `.waves/link.sh` → 2 undefined (was 19):
`audio_uart_ambiq_draw_box_shadow_540036`, `audio_uart_ambiq_vector_shape_draw_5202ec`.
Build: 2868/2868 compiled, 0 duplicate strong symbols, composed ok.

Third-party drop-ins added (user-approved 2026-10-26):
| Component | Source | Version | License | Notes |
|---|---|---|---|---|
| nrf_fuel_gauge | github.com/nrfconnect/sdk-nrfxlib `nrf_fuel_gauge/` @ v3.0.2 | lib 1.0.1 (build 2025-03-24T16:07:58Z), cortex-m4 hard-float | LicenseRef-Nordic-5-Clause (`license.txt` kept) | Linked UNMODIFIED from `third-party/upstream/nrf-fuel-gauge-1.0.1`. Stock reports version `c205a2`, build `2025-04-28T13:29:15Z`: no public release has that build date, 1.0.1 is the closest earlier one. GUESS: the ABI matches (the 24-byte init params, the process/tte/ttf signatures and the VFP/SP hard-float attributes agree). |
| ambiq-lvgl draw/ambiq | already vendored | — | MIT | Upstream units arc, border, fill, line, mask_rect, triangle and vector are built in profile 57. box_shadow and private.c are excluded (box_shadow needs LV_DRAW_SW_COMPLEX; private.c needs a newer NemaGFX than the vendored headers). |
| NemaGFX headers | ambiq-lvgl/libs/nema_gfx/include and atc-miband8-fw ThinkSi NemaGFX_SDK include/ | — | Think Silicon (headers only) | No NemaGFX .c source is publicly available. The prebuilt STM32 libnemagfx .a files are not used. |

New files:
- `graphics/g2c-nema/include/gpu_patch.h` maps `lv_ambiq_gradient_create`/`dashline_create` to the 0x5fa238/0x5fa7c0 reconstructions.
- `graphics/g2c-nema/g2c_nema_raster.c` reconstructs from stock: 0x514d2c cl_enough_space (GUESS name), 0x522848 set_matrix_all, 0x522b30 raster_rounded_rect, 0x522a24 raster_triangle_f, 0x522e9c raster_quad_fx, 0x52330c raster_stroked_arc_aa, 0x523674 raster_stroked_arc_aa_mask, 0x524260 atan.
- `graphics/g2c-nema/g2c_nema_vg_init.c` reconstructs 0x522400 nema_vg_init_stencil_prealloc plus 0x5155d6, 0x515304 (context reset), 0x5675b4 and 0x5675a8. The context storage at 0x2006cd30 is sized 0x390 (GUESS).
- `drivers/power/npm1300/battery-model/g2c_npm1300_battery_model.c` holds the 5632-byte struct battery_model "EVENBAT", copied bit-exact from ROM 0x646bf8.
- `drivers/power/npm1300/battery-model/g2c_nrf_fuel_gauge_shim.c` forwards the address-named entry points to the Nordic library, and maps expf/logf/fabsf to the IAR reconstructions.

Defsym aliases: these were identified by matching the stock draw-function callee order against the upstream sources, and each is a GUESS unless noted.
- nema_raster_rect→522ae0, set_raster_color→522a16, bind_tex→4b1298, cl_*→5144fa/514384/514cf2/514d00, sin/cos→52405c/524130, f2fx→5242cc
- mat3x3 identity/translate/scale/rotate/invert→561810/561856/5618b8/561964/561b38, set_matrix→5226e8, set_matrix_translate→5228b0
- set_clip_temp→4b1516, set_clip_pop→4b1548, set_tex_color→4b146c, enable_aa→52266e, enable_aa_flags→5226b2
- lv_ambiq_color_convert→4b06a8, set_blend_fill→4b0730, set_blend_blit→4b0748, blend_mode_change→4b06c0
- lv_draw_ambiq_decode_image→4b0f50, bind_image_texture→4b0d38, stencil_buffer_adjust→4b0b5a
- stock ambiq draw arc/border/fill/line/mask/triangle → upstream lv_draw_ambiq_*
- 48a0be→lv_draw_label_iterate_characters; fmod→iar_fmod_57dc40; lv_image_decoder_close→48908c

Remaining:
- 0x5202ec is nema_vg_draw_path (not lv_draw_ambiq_vector). Its NemaVG tessellator subtree has not been reconstructed: 516b34, 516c82, 516e0c, 5171f8, 51d2e0, 51f798, 515148, 51520c, 567230, 5619f2, 4b14ca, 4b14fe.
- 0x540036 box_shadow: reconstruct from stock (lv_ambiq_shadow_blur_corner is not in g2).
- Not started this wave: em9305, touch, codec-a/b, bootloader, and the version-matching of the existing third-party/upstream sets (AmbiqSuite, Cordio, FreeRTOS, LVGL, ...).

## g2c wave 4 (2026-10-26) — NemaVG path/tessellator + box_shadow

Link status: `.waves/link.sh` → **0 undefined** (was 2). Build 2869/2869 compiled, composed unresolved 22 (aliases reduce further at link).

### Vector / shadow reconstruction
- `graphics/g2c-nema/g2c_nema_vg_path.c` (~14.8k lines): mechanical lift of 45 Ghidra decompilations covering `0x5202ec` (`audio_uart_ambiq_vector_shape_draw_5202ec` / nema_vg_draw_path) and its tessellator subtree, plus `0x540036` (`audio_uart_ambiq_draw_box_shadow_540036`).
- Closure addresses: 5202ec 540036 4b14ca 4b14fe 515148 51520c 516b34 516c82 516e0c 5171f8 51d2e0 51f798 5619f2 567230 4b1794 51778c 517796 5156b8 51a8ec 516cf8 5179d0 519290 5177a4 51785c 517e18 51b8f0 51bf7c 522622 522f1c 522f50 522fb4 523284 523a34 524218 51b140 56395c 5639e8 5657d8 51a694 516bde 51c5ec 51a660 564974 5653a0 5640e4.
- Tooling added (uncommitted): `.waves/lobpatch.py` / `lobpatch.txt` (ARMv8.1-M WLS/DLS/LE → Thumb-2 trampolines for Ghidra), `.waves/pdecomp.sh` + `G2PatchDecomp.java` (read-only LOB patch + forced signatures + two-pass param commit), `.waves/extsigs.txt` / `forcesigs.txt` / `allsigs.txt`, `.waves/pcl/` patched decompilations.
- `0x540036` Ghidra failure ("memory range beyond end of address space") was caused by an intentional crash stub at `0x5401ae` (`movs.w r1,#-1; str r0,[r1]; b .` after a failed assert). Patched that site to `movs.w r1,#1` for analysis-only decomp (not shipped).
- Local shim for `display_driver_nema_mode_commit_52294c` (stock `mov r1,r0; mov r0,#0x11c; b 514846`) so we need not flip `link:true` on the helpers unit.

### Guesses / unverified (flagged in code)
- All `extraout_*` / `unaff_*` / `in_s*` / `stack0*` leftovers zero-initialized (VFP/GPR tracking gaps after LOB and float helpers).
- `in_fpscr` ignored; `Vector*ToFloat` helpers use C casts.
- ROM float-pair slots at 0x5202d0/d8/e0 mapped to zero pairs; some `&DAT_*` sites rewritten to stock VAs.
- Float↔pointer punning via `g2c_ptr_as_float` / `g2c_float_as_ptr` at bad decomp sites.
- Fuel-gauge version still 1.0.1 vs stock `c205a2` (unchanged from wave 3).
- `g2c_nemavg_area_copy_540024` is a 16-byte struct copy (stock 0x540024).

### Other payloads (wave-4 status, no new drop-ins this turn)
| Payload | Build | Composed undef | Notes |
|---|---|---|---|
| g2-apollo-main | 2869/2869 | 22 (link 0) | vector+shadow done |
| g2-em9305 | 618/618 | 37 | no composition |
| g2-touch | 78/78 | 30 | composed |
| g2-codec-a | 344/344 | 5 | no composition |
| g2-codec-b | failed | — | `backup_stage2_gpio_irq_masks.c` |
| g2-apollo-bootloader | 381/381 | 3 | composed |

### Library sweep (partial)
Already under `third-party/upstream/`: ambiq-lvgl, ambiqhal-*, ambiqsuite-sdk, cmsis-*, cordio, easylogger, flashdb, freertos-kernel, goodix-gh3x2x, invensense-icm45608, liblc3, lvgl, lz4, nrf-fuel-gauge-1.0.1, nanopb, littlefs, … Version-matching against stock and EM9305/touch/codec vendor SDK downloads were **not** finished this turn (time spent on NemaVG/box_shadow for the clean link).

## g2c wave 5 (2026-10-26) — payload closure + library sweep start + nvg cleanup start

### Per-target link / compose status
| Payload | Build | Composed undef | Notes |
|---|---|---|---|
| g2-apollo-main | (unchanged wave 4) | 22 (link 0) | NemaVG cleanup started |
| g2-apollo-bootloader | 381/381 | **0** | compose `--defsym` ROM ABS (also `bind_resident_rom.py`); full ELF still Thumb ABS reloc warnings (ENTRY=`opencfw_boot_reset_entry`) |
| g2-codec-a | 345/345 | **0** | compose via new `csky-ld`; fpadd_parts_nan exported; stage1 CRT GUESS stubs |
| g2-codec-b | 332/332 | **0** | gpio_irq_masks compiles; sample_app linked; BSS clear stock 0x20017090..0x2002d79c |
| g2-touch | 81/81 | **0** | CapSense/PDL GUESS stubs + soft memset/uidiv; lp history enabled; CapSense v5/PDL staged (need cycfg) |
| g2-em9305 | 619/619 | **0** | compose via new `arc-ld`; ROM call bindings + GUESS app/QP/HCI closure |

### Files changed (high level)
- `tools/build/bind_resident_rom.py` — ROOT `parents[2]` fix
- `g2/src/sources.json` — csky-ld/arc-ld; codec/em compose; sample_app + touch/em glue
- codec-a: `resident_xip_fpadd_parts.c`, `uart_stage1_crt_initializers.c` (GUESS)
- codec-b: `backup_crt_clear_bss.c`, sample_app `link:true`
- bootloader: `link/g2-apollo-bootloader.ld`, `.waves/link-bootloader.sh`
- touch: `glue/touch_runtime_soft.c`, `touch_cybsp_stub.c`, `touch_pdl_capsense_stubs.c`, freestanding `string.h`; PDL symlinks in psoc4-touch-slice
- em9305: `application/em9305_link_closure.c`
- nvg: `g2c_nema_vg_path.c` — `g2c_fpscr_eq/lt` helpers; first FPSCR bitfields rewritten

### Library sweep (version-match notes)
| Component | Stock / target | Tree copy | Action |
|---|---|---|---|
| CapSense | v5.0 (upstream-map); LP APIs | `reference/infineon-capsense-v5` (5.0); pinned upstream 3.0.1 lacks LP | Prefer v5; cycfg missing → GUESS stubs for link |
| mtb-pdl-cat2 | PSoC4000T | `vendor-cache/.../touch-gcc-14.2/pdl-input` symlinked into psoc4-touch-slice | Partial |
| EM9305 SDK | product ROM | `local-vendor/sources/em9305-v4.6` (+ v4.2) | ROM addrs bound; SDK bodies not substituted |
| NationalChip LVP | image A/B | `nationalchip-lvp-kws` @ 8bf9ee5 | Already used for codec |
| AmbiqSuite | apollo-main | upstream + local R3.2.0 (`release_sdk_3_2_0-dd5f40c14b`) | Version note only |
| QP/C | 6.5.1 (myapp) | `qpc-official` acquisition | GUESS ctor/top for compose |

### Guesses (new this wave)
- uart stage1 initialize_*/start_application (stock 0x100001fc/1dd8/1378/2c8 not in seed set)
- touch CapSense/PDL/cybsp stubs; soft `__aeabi_uidiv(mod)`
- em9305 empty HCI tables; QP ctor/top; app veneers
- bootloader MRAM map in new `.ld`
- image-b BSS sentinel objects (clear uses stock absolute span)

### Remaining
- bootloader full ELF Thumb ABS; apollo-main composed-22
- touch: CapSense v5 + PDL once cycfg exists
- em9305: SDK/QP/Cordio for GUESS closure; HCI tables
- nvg: finish extraout/unaff/in_s* and remaining FPSCR bitfields; float↔pointer punning


## g2c wave 6 (2026-10-26) — real completeness: final ELF/bin + stub replacement + inventory

Goal: turn composed-0 into linked ELF/bin, replace GUESS stubs with upstream/stock, inventory remaining inference, continue nvg cleanup.

### Per-target final link status
| Payload | Composed undef | Final ELF | Final BIN | Notes |
|---|---:|---|---|---|
| g2-apollo-bootloader | **0** | `g2/build/g2c-w6-final-apollo-bootloader/g2-apollo-bootloader.elf` (290028 B) | `.bin` 171900 B | `resident_rom_thumb_set.S` (`.thumb_set` typed ABS); MRAM LENGTH 0x40000 |
| g2-codec-a | **0** | `.../g2c-w6-final-codec-a/g2-codec-a.elf` (200652 B) | `.bin` 88964 B | stage1 CRT = stock `.S` bytes |
| g2-codec-b | **0** | `.../g2c-w6-final-codec-b/g2-codec-b.elf` (173476 B) | `.bin` 89722 B | BSS stock span retained |
| g2-touch | **0** | `.../g2c-w6-final-touch/g2-touch.elf` (109504 B) | `.bin` 57572 B | CapSense v5 sensing_lp+generator_lp + PDL; text/data/bss 57416/156/1804 |
| g2-em9305 | **0** | `.../g2c-w6-final-em9305/g2-em9305.elf` (935772 B) | `.bin` 325624 B | HCI tables from stock; QP ctor/top real; NVM LENGTH 0x80000 + sdata |

Linker scripts: `g2/src/{apollo-bootloader,touch,codec,em9305}/link/g2-*.ld`. Driver: `.waves/link-final.sh`.

### Stub → real replacements
- **touch CapSense/PDL/cybsp**: upstream `infineon-capsense-v5` (`sensing_lp`, `generator_lp`, control/structure/sensing/processing/filter) + `psoc4-touch-slice` PDL (`cy_gpio/sysclk/syslib/msclp`…); `touch_cybsp.c` → `init_cycfg_all`; freestanding `stdlib.h`; `touch_syslib_cycles.c` (clang lacks `.func`); vectors + CapSense lib tails in `touch_vectors_and_capsense_tail.c`; stubs `build/link:false`.
- **em9305 HCI**: `em9305_hci_cmd_tables.c` — 56 stock entries at VMA 0x334xxx.
- **em9305 QP**: `em9305_qpc_ctor.c` — real `QHsm_top`/`QHsm_ctor`/`QActive_ctor` + minimal vtable; start/post still thin (inventory).
- **stage1 CRT**: `uart_stage1_crt_initializers.S` (stock bytes); `.c` disabled.
- **image-b BSS**: stock span in `backup_crt_clear_bss.c` retained.

### Remaining-inference inventory (definitive)
See `g2/docs/wave6-remaining-inference-inventory.md` (+ `.json`).

| target | GUESS | stub/placeholder | weak | raw-decompile | nvg leftovers |
|---|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 2 | 0 | 3 | 0 |
| g2-codec-a | 0 | 3 | 0 | 3 | 0 |
| g2-codec-b | 0 | 0 | 0 | 5 | 0 |
| g2-touch | 2 | 1 | 3 | 0 | 0 |
| g2-em9305 | 0 | 6 | 0 | 0 | 0 |
| g2-apollo-main | 104 | 28 | 3 | 14 | 340 |

### nvg cleanup (continued)
- `g2c_nema_vg_path.c`: `g2c_fpscr_*` usage ~93; leftover tokens still 245 (`in_fpscr`/`extraout_*`/`unaff_*`).
- `display_lv_init_children.c`: helpers + ~17 `g2c_fpscr_*`; leftover tokens 95.
- Bit-flag `(int)((uint)*(byte*)…<<N)<0` idioms and multiline VFP compares remain.

### Files changed (high level)
- touch: vendor `cycfg_capsense*.h`, `cycfg_peripherals.h`, glue (`touch_cybsp.c`, `touch_syslib_cycles.c`, `touch_system_core_clock.c`, `touch_vectors_and_capsense_tail.c`, freestanding `stdlib.h`, runtime aeabi), `link/g2-touch.ld`, CapSense/PDL units in `sources.json`
- em9305: `em9305_hci_cmd_tables.c`, `em9305_qpc_ctor.c`, `em9305_link_closure.c`, `link/g2-em9305.ld`
- codec: `uart_stage1_crt_initializers.S`, `link/g2-codec-{a,b}.ld`
- bootloader: `link/g2-apollo-bootloader.ld`, `link/resident_rom_thumb_set.S`
- nvg: `g2c_nema_vg_path.c`, `display_lv_init_children.c`
- build: `.waves/link-final.sh`, `g2/src/sources.json`
- docs: `wave6-remaining-inference-inventory.{md,json}`, this ledger section

### Remaining after wave 6
- apollo-main composed-22 / nvg leftover tokens (~340) and GUESS-heavy mechanical lift
- em9305: full QEQueue post / qf_actq; more SDK substitution
- touch: CapSense closed lib (`.a`) vs thin `UpdateThresholds_Lib`/`CalculateRawTarget`; cycfg from design.cycapsense
- Final images larger than stock in places (bootloader/em9305 MEMORY expanded) — not byte-identical

## Wave 7 — inference burn-down (2026-10-26 16:44 CDT)

Burned `wave6-remaining-inference-inventory` biggest-first; regenerated inventory.

| target | GUESS | stub/placeholder | weak | raw-decompile | nvg leftovers |
|---|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 0 | 0 | 0 | 0 |
| g2-codec-a | 0 | 0 | 0 | 0 | 0 |
| g2-codec-b | 0 | 0 | 0 | 0 | 0 |
| g2-touch | 0 | 0 | 2 | 0 | 0 |
| g2-em9305 | 0 | 0 | 0 | 0 | 0 |
| g2-apollo-main | 0 | 0 | 3 | 0 | 0 |

Wave6 baseline was 104/28/3/14/340 on apollo-main; nvg leftovers 340→0 (rename/lift); GUESS/stub/raw cleared.

### Link status
| target | compose U | final ELF |
|---|---:|---|
| g2-apollo-main | 22 (unchanged wave4/5 gate) | compose ok `g2/build/g2c-w7-apollo-main/` |
| g2-touch | 0 | `g2/build/g2c-w7-final-touch/` ELF+bin |
| g2-apollo-bootloader | 0 | w6 final ELF kept (comment-only edits) |
| g2-codec-a | 0 | w6 final ELF kept |
| g2-codec-b | 0 | w6 final ELF kept |
| g2-em9305 | 0 | w6 final ELF kept |

Residual weak: IAR optional putchar selects (3); PDL `Cy_SysLib_*` soft overrides in touch_cybsp (2).

### Notable proofs / fixes
- touch SP `0x20002000` (FWPK+0x20) in `touch_vectors_and_capsense_tail.c`
- `audio_uart_nema_error_set_4b127c` / `cl_node_release_514178` return types aligned to stock (via headless-decomp)
- path 0x514846 / 0x52294c / related returns verified; broken `g2c_fpscr_eq(x<0)` sites → `g2c_fpscr_lt`
- nvg: `in_fpscr`/`extraout_*`/`unaff_*` → `fpscr_bits`/`vfp_*`/`saved_*`/`vg_ctx_r6`; display got local `g2c_fpscr_*` helpers

### Files changed (high level)
- apollo-main: `g2c_nema_vg_path.c`, `display_lv_init_children.c`, `iar_stdout.c`, `g2c_*` data/port/vectors/clkmgr/ble leaves, UI comment scrub, shim/gpu_patch headers
- touch: `touch_vectors_and_capsense_tail.c`, `touch_cybsp.c`
- bootloader/codec/em9305: comment scrub only (false-positive inventory hits)
- docs: `wave6-remaining-inference-inventory.{md,json}`, this ledger section

## Wave 8 — audit of wave7 burn-down (2026-10-26 16:52 CDT)

Wave7 cleared inventory counts largely via **(c) comment scrub / renames**. Honest restore done.

See `g2/docs/wave8-audit-wave7.md` for per-class (a)/(b)/(c) tables.

### Audit split (markers removed from wave6 counts)

| target | (a) evidenced | (b) code unverified | (c) comment/rename |
|---|---:|---:|---:|
| g2-apollo-main | ~6 | ~10 | ~473 |
| g2-touch | 1 (SP) + reset entry added | CapSense thin tails | ~5 keyword scrubs |
| bootloader/codec/em9305 | 0 | 0 | all wave7 stub/raw burns |

### Honest inventory (restored)

| target | GUESS | stub | weak | raw | nvg | UNVERIFIED |
|---|---:|---:|---:|---:|---:|---:|
| bootloader | 0 | 3 | 0 | 3 | 0 | 3 |
| codec-a | 0 | 1 | 0 | 3 | 0 | 1 |
| codec-b | 0 | 0 | 0 | 5 | 0 | 0 |
| touch | 3 | 1 | 2 | 1 | 0 | 0 |
| em9305 | 0 | 2 | 0 | 0 | 0 | 2 |
| apollo-main | ~91 | ~7 | 3 | ~12 | ~341 | ~11 |

(Exact table in regenerated inventory md.)

### Link status
- apollo-main compose **U=22** — documented intentional (linker script 11 + IAR weak 3 + nrf_fuel_gauge 8)
- touch compose U=5 (`__data_*`/`__bss_*` from CRT); final ELF **U=0** with `touch_runtime_0164_reset_entry` @ stock VA 0x3464 shape
- bootloader/codec/em9305: w6 finals kept

### Files
- audit: `g2/docs/wave8-audit-wave7.md`
- touch: `glue/touch_runtime_0164_reset_entry.c`, vectors Reset_Handler → entry; `sources.json`
- nvg: restored `in_fpscr`/`extraout_*`/`unaff_*` in path + display_lv
- restored GUESS/UNVERIFIED/stub/Ghidra markers across scrubbed sites

## Wave 9 (2026-10-26, America/Chicago)

Evidence-gated burn of honest inventory. Markers removed only with stock VA +
corpus decompile/disasm or upstream file+version citation. No nvg renames
without FP/register recovery.

| target | GUESS | stub | weak | raw | nvg | UNVERIFIED |
|---|---:|---:|---:|---:|---:|---:|
| g2-apollo-bootloader | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-codec-a | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-codec-b | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-touch | 2 | 2 | 2 | 0 | 0 | 0 |
| g2-em9305 | 0 | 0 | 0 | 0 | 0 | 0 |
| g2-apollo-main | 90 | 0 | 3 | 0 | 344 | 3 |

Wave8 baseline: boot 0/3/3, codec-a 0/1/3 UV1, codec-b 0/0/5 UV4, touch 3/1/1,
em 0/2 UV2, apollo 91/7/12/341 UV11.

Link: all 6 compose ok; touch final U=0; apollo compose U=22 documented.
Details: `g2/docs/wave9-evidence-removals.md`.


## Wave 10 (2026-10-26)
- Touch: the CapSense UpdateThresholds_Lib/CalculateRawTarget stubs were removed. Their dead callers are gc-stripped, and the closed lib was proven absent from stock. Final ELF links with 0 undefined symbols.
- apollo-main: nvg 344→262 and GUESS 90→81, all in `g2c_nema_vg_path.c`. UNVERIFIED is still 3. Compose is 2869/2869 with U=22, the documented gate.
- See `wave10-evidence-removals.md` and `wave6-remaining-inference-inventory.md`.
- Bootloader final relink still fails (ld script syntax error, from Wave 9). Its compose gate is clean.

## Wave 11 (2026-10-26)
See g2/docs/wave11-evidence-removals.md. All 6 targets final-link with 0 undefined. Wave 10 apollo-main "no final link" claim corrected. apollo-main guess 81->17, nvg 262->133; touch stub/weak 0. FLAG: bootloader text overlaps 0x438000.

## Wave 12
See g2/docs/wave12-evidence-removals.md. apollo-main markers: guess 15, stub 1, weak 3, nvg 61, unverified 3. Other targets: 0. Bootloader now fits 0x410000..0x438000 with region enforcement.

## Wave 13 — loadable image origins (see g2/docs/wave13-loadable-images.md)
- touch 0x3300 / em9305 0x302400 / codec-a 0x10023400+XIP 0x10203004 / codec-b 0x10003000 now match stock, with bounded regions (overflow fails the link, tested).
- All 6 relinked from fresh w13 composes with 0 undefined: g2/build/g2c-w13-final-{touch,em9305,codec-a,codec-b,apollo-main,apollo-bootloader}.
- Step 3 (display_lv in_fpscr, draw_fill carriers, remaining apollo markers) not started; counts unchanged: guess 15, stub 1, weak 3, nvg 61, unverified 3.

## Wave 14
See g2/docs/wave14-ram-size-alias.md. touch: stock-layout reset RAM (954/964 bytes match plus relocated pointers), stack 4212 vs 4264 B. em9305: -Os, 216,988 B. codec: SRAM alias proven; codec-b overlap of 7052 B is still open. inventory.py now scans .ld files.

## Wave 15
See g2/docs/wave15-codecb-touch.md. codec-b fits the stock bound: -Os plus printf without float, ending 0x10016cd8 <= 0x1001708C. touch: SystemCoreClockUpdate rebuilt from stock; 36 B gap shown to be unused; .noinit discard made explicit. apollo display_lv/FPSCR work is not done.

## Wave 16
apollo-main in_fpscr 53->0; nvg 61->1, guess 16->15, unverified 3->2 (g2/docs/wave16-apollo-fpscr.md).

## Wave 17

## Ledger
- The stray root C-RECONSTRUCTION-PROGRESS.md (Waves 12-16) was merged into this file and deleted.

## display_lv_init_children.c
- Each of the 10 batch-3 sign tests has its own stock citation: 0x563106, 0x563188, 0x5632ec, 0x56336a, 0x563400, 0x563446, 0x5634e4, 0x56352e, 0x563588, 0x5635da. Pattern: vcmp #0; ite gt; vmov +/-1.0. Matched by order and sqrt-operand shape (flagged).
- The last NAN test was rewritten as `!(a >= b)` (stock 0x562ab2, it lt). The NAN macro was removed, and nvg_leftover went 1 -> 0.

## g2c_nema_vg_path.c
### draw_fill_51d2e0
- All FPSCR-carrier compares were rewritten as direct compares, each citing its branch condition (see the in-code comments).
- Decompiler bugs fixed:
  - NaN-only tests at 0x51dafa and 0x51df2e.
  - 8 zero-pair sites: the stock code copies the value, not the address.
  - sp+0 out0 slot (fStack_2d0).
- The uVar4 0xfffffff masks were removed. uVar14 is now only a stencil handle.

### vector_shape_draw_5202ec
- Fixed out-of-bounds UB: 3 scalar residuals were indexed `i*8`.
- Stock frame: push 9 regs, sub sp,#4, vpush d8-d15, sub sp,#104 (0x5202ec-0x5202f8). That puts sp at entry-0xd0.
- The 3 residuals and afStack_c4 (sp+0xc) now share one `uint g2c_sp_frame_5202ec[26]`.

### draw_box_shadow_540036
- Fixed a real semantic bug: stock 0x540938-0x540948 memcpy's 3 bytes from dsc+0x20 into [sp] and passes [sp] as color_resolve arg0. The decompiled C passed uVar5 (the old [sp] value) and discarded the memcpy.

### path_cmd_5156b8
- The two CONCAT31 GUESS sites were replaced with byte stores to sp+4: stock 0x515b22 and 0x516588 `strb.w sl,[sp,#4]`, read back as bytes at 0x515b8a and 0x5165ee. The old `(float)CONCAT31` was a value conversion, not a byte merge.

## Not done (still flagged; no evidence recovered)
- apollo guess (8):
  - file headers in g2c_ble_leaves, am_hal_clkmgr_g2, g2c_vectors, g2c_nema_leaves, g2c_ghidra_shim.h, gpu_patch.h
  - the vg_path file header (about 240 FPSCR/carrier sites remain outside draw_fill)
  - .ld MRAM/SSRAM size
- stub 1 (notify_app_icon), unverified 2 (vg_path header), inferred 11.
- .ld raw_decompile 1: this is the provenance line "Ghidra 12.1.4" in the memory-map note, a scanner false positive. Left as is.
- em9305 .ld FLAG/UNVERIFIED (RAMHI 0x80fe20..0x810000 unused by stock): the stock em9305 binary was not at hand this wave. Next check: grep it for 0x80fe20-0x810000 literals and the initial SP (the stack may sit there).
- codec-a .ld FLAG/GUESS (stage1/2 and generic .text ownership): not resolved.

## Builds (0 undefined each)
| Target | Output | Notes |
|---|---|---|
| apollo-main | g2/build/g2c-w17-final-apollo-main | from g2c-w17b-apollo-main; text 3,481,241 / data 168,651 / bss 1,999,768 |
| apollo-bootloader | g2/build/g2c-w17-final-apollo-bootloader | identical to w15 |
| em9305 | g2/build/g2c-w17-final-em9305 | |
| codec-a | g2/build/g2c-w17-final-codec-a | |
| codec-b | g2/build/g2c-w17-final-codec-b | |
| touch | g2/build/g2c-w17-final-touch | |

Inventory: g2/docs/inventory-w17.json

## Wave 18
See g2/docs/wave18-markers.md and g2/docs/inventory-w18.json. All 6 targets were relinked into g2/build/g2c-w18-final-* with 0 undefined. apollo-main text 3,480,737 (W17 3,481,241), data 168,651, bss 1,999,768. vg_path NAN( tokens 215 -> 158. em9305 pins added (FLAG/UNVERIFIED kept). codec-a stage2/res.text ownership cited. Inventory marker counts are unchanged from W17.

## Wave 19
- em9305 relinked against the current .ld (0 undefined).
- g2c_nema_vg_path.c: NAN( 158 -> 0 and g2c_fpscr_* 43 -> 0, all with per-site stock vcmp citations. The carrier macro and helpers are removed. The file compiles rc=0 with 54 uninitialized warnings (unchanged).
- stroke_path/fill_path: the 4 order-matched citations are now address-verified.
- em9305 myapp pin addresses were found as limm operands in stock (0xca2e/0xcb0e). Sizes are still UNVERIFIED.
- Compose g2c-w19-apollo-main: 2869/2869 compiled. Finals are in g2/build/g2c-w19-final-*, all 6 with 0 undefined.
- apollo-main text dropped 3,480,737 -> 3,479,921 (-816). The other 5 sizes are unchanged.
- Inventory (inventory-w19.json): identical to W18 except em9305 unverified 1 -> 2 (new honest sizes marker). Details in wave19-markers.md.

## Wave 20
- Scanner: explicit, documented rules in .waves/inventory.py (wave20-markers.md): a Ghidra word inside a stock-address citation or a tool-version line is not raw; an explicit negation of "inferred" is not counted. The wave19 stroke/fill comments are restored to their "Ghidra label" wording.
- apollo-main: guess 8->4, unverified 2->0, raw 1->0, inferred 11->5, stub 1, weak 3. .ld guess/raw/inferred 1/1/1 -> 0/0/0.
  - Evidence: vg_path header, nema ctx size, gpu_patch prototypes, MRAM/SSRAM upstream match, DIS serial attribute, app_db offsets.
- em9305: myapp AO 36 B / queue 16 B verified from the ARC objdump corpus (unverified 2->1); "not plain ARC" corrected.
- codec-a: 11 libgcc routines and crc32_no_comp verified in stock image_a_xip; DSP has no image_a body (GUESS kept).
- Builds g2c-w20-apollo-main (2869/2869) and g2/build/g2c-w20-final-*: all 6 targets 0 undefined, sizes identical to W19 (comment-only source changes).
- inventory-w20.json written. The unresolved list with reasons is in wave20-markers.md.

## Wave 21

- Vectors: the 10 spin-alias slots are bound to stock-verified bodies (8 existing, 2 new: 0x4b80be GPIO0_607F, 0x4d58a6 IRQ82). The vectors GUESS is removed, and the readback of the linked table is checked.
- Clock manager: full stock RAM map of g_sClkMgr* state (pools 0x4c43dc..0x4c46a0). clock_release_all is reimplemented from stock 0x4c45a4. This fixes a real no-op: the upstream copy walked an empty private bitmap. The GUESS is narrowed to the upstream-only private_clkgen helpers.
- g2c_ghidra_shim.h had no includers and is removed (backup in .waves/w21-bak).
- em9305: the 16 gp loads (43 gp operands) are rodata mis-decoded at 0x334122..0x334ca4, gp is never written, and no code touches 0x80fe20..0x80fe28. The UNVERIFIED is narrowed to possible ROM use.
- inventory.py: new CORPUS citation rule (documented in the script).
- Builds: g2c-w21-apollo-main (2869/2869), and g2c-w21-final-* for all 6 targets, each with 0 undefined. apollo-main text is 3,479,921 -> 3,480,017; the other targets are unchanged.
- apollo-main inventory: guess 4->2, raw 0, stub 1, weak 3, inferred 5. Other targets unchanged. Details are in wave21-markers.md and inventory-w21.json.

## Wave 22
- Correction: wave 21 claimed "stock has no private_clkgen helpers". That was wrong. Stock am_hal_clkgen_control 0x4d3628 calls 0x4c45fc/0x4c465c/0x4c4668/0x4c46b4; Ghidra corpus just has no function entries there. am_hal_clkmgr_g2.c now carries stock-derived release_all and the hfadj/hf2adj helpers, and the upstream include is dropped. The clkmgr GUESS is removed.
- ble +0xc3 GUESS is resolved: it is the link-role byte (AppDbNewRecord 0x47a71c, Master/Slave log).
- aging_test LVGL callees are string-anchored to lvgl 9.3. The dmic/i2s providers are verified against decomp. Citations were added for em9305 controller_init and touch FLAG.
- inventory.py: CORPUS extended, NEG2 added (both documented inline).
- inventory-w22 versus w21:
  - apollo-main: guess 2→0, stub 1, weak 3, inferred 5→2.
  - codec-a: guess 1, flag 1.
  - codec-b: raw 1→0, inferred 2→0.
  - touch: flag 1.
  - em9305: unverified 1, flag 1, inferred 1→0.
- Links: all 6 have 0 undefined. apollo-main is 3,476,849/168,627/1,999,612.
- Remaining items: wave22-markers.md.

## Wave 23
- Scope: em9305 inline asm -> C (the largest remaining share, 29.5% of FUNC bytes). The unmatched apollo-main runs were triaged first and are mostly not unported code:
  - 0x5d2fee..0x5d8908 (22.8 KB, 114 runs) is FreeType 2.9.1 psaux cf2_* (upstream-map.tsv, followups.md line 16). It is covered by an upstream unit and only unmatched because IAR inlines it.
  - `_bleSlaveProcMsg` 0x46e098 already has source in ble-slave/display_ble_slave_proc_msg.c (the coverage tool misses it by name).
  - The remaining first-party unmatched runs (113 runs, 50,540 B) need per-function string/xref matching and are queued for wave 24.
- em9305: 59 lowered-asm units in qpc-scheduler/initializer_lowers are now C (symbol names unchanged, so the remaining asm units still link to them):
  - 29 leaf/tail-call wrappers and 30 more (enter_s/push_s call chains, small predicates, record writers).
  - Evidence for each unit: the C was compiled with the g2-em9305-1 profile (arc-elf32-gcc 15.2, -mcpu=arcem -mcode-density -Os) and its disassembly was diffed against the stock-lowered asm unit with `.waves/em-conv.sh`.
  - 4 units are byte-identical. The other 55 differ only by delay-slot scheduling (ARC `b.d`/`j_s.d` slots, which gcc does not fill), a redundant `extb_s`/`exth_s` after a volatile byte/halfword load, absolute-address `ld`/`st` forms, and strength reduction of `a % 625` (child_31340c). Each diff was read by hand. Each unit's header says so.
  - Delay-slot pitfall handled: a `bl.d` slot runs before the call, so `mov_s r13,r0` in the slot captures the original r0 (the arguments are `a`, not the callee's result).
  - Each unit carries its stock address range. No guess markers were added.
- Metrics (em9305):
  - asm-defined FUNC bytes: 61,860 -> 61,138 (29.5% -> 29.2%).
  - unit files still containing `__asm__`: 464 -> 411 by the file scan (the scan was taken after the first conversion, which is why it is -53 rather than -59).
  - text: 216,984 -> 217,032 (+48, mostly gcc `extb_s` and `nop_s` padding).
  - The compose is 621/621 with the same 6 libgcc/memcpy externals as wave 22, and the final link has 0 undefined (`g2/build/g2c-w23-final-em9305`, -Os kept).
- Other targets: no source changes this wave, so their wave-22 links stand (apollo-main 3,476,849 / 168,627 / 1,999,612).
- Paired sim vs stock: not re-run. This wave changed only em9305 ARC sources, which the Renode paired sim does not execute (it models the EM9305 as a peripheral). The apollo-main image is unchanged, so the earlier GPUJIM=1 results stand.
- inventory-w23.json: em9305 unverified 1 / flag 1 (unchanged). apollo-main now shows guess 5: these are the honest GUESS flags added by the sim-fix RAM-cell work after wave 22 (stock_ram_cells.c x3, display_ring_descriptor_data_20002c48.c, g2-apollo-main.ld ucHeap base). They are flagged, not new decompilation guesses.
- `make sources-check` reports one existing gap unrelated to this wave: g2/src/apollo-bootloader/link/resident_rom_thumb_set.S is not in sources.json.
- Tooling: `.waves/arc.sh` runs any arc-elf32-* tool in the container, `.waves/emdump.sh` prints a compact disassembly of a lowered unit, and `.waves/em-conv.sh` compiles a candidate, diffs it against the stock lowering, and replaces the unit only on an identical match (or with FORCE=1 for the same size).
- Next: the larger em9305 units (1-2 KB each, e.g. associated_callback_329888, dispatch_child_31d6a4, radio_cb_31dfd0) and the first-party unmatched apollo runs (0x5bdfbc, 0x5bd3a0, 0x504d2c, 0x5a2d24).

## Wave 24
- Scope: the "113 first-party unmatched apollo runs (50.5 KB)" first, then large em9305 asm units, then coverage-tool honesty and `resident_rom_thumb_set.S`.
- Apollo triage: the 113 runs were mostly not first-party. `.waves/sim-fix/coverage3.py` now reads the four reference maps plus the new `ranges-w24.tsv` and classifies every TSV row (see apollo-coverage-map.md, "Wave 24 re-measurement"). Result: 8,445 strong (matched 6,890, upstream 1,238, lvgl 184, data 10, blocked 19, range-upstream 104), 376 weak attributions (family / sandwich / callee / name-ref / stock-anchor / addr-ref), 23 residual functions (1,746 B). The strong total is the number to quote; the weak ones are flagged as attributions.
- `ranges-w24.tsv` rows are decompile-checked (ftglyph.c, ftstroke.c, ftbitmap.c, am_hal_uart/i2s/syspll statics). The npmx static range 0x55ea40..0x55fab0 is weaker evidence (all callers are npmx_*) and is labelled so.
- No apollo source was changed, so no apollo rebuild or paired sim was required. The apollo-main image is unchanged, and earlier GPUJIM=1 results stand.
- `resident_rom_thumb_set.S` is first-party (three `.thumb_set` ABS symbols that give the resident-ROM entries a Thumb FUNC type), but it is a link helper assembled by `.waves/link-final.sh` with `g2-apollo-bootloader.ld`. Adding it as a compose unit would double-define the symbols, so `sources.json` has a new top-level `not_built` map (read by `tools/build/sources.py`) that records it with that reason. `./g2/make.sh sources-check` passes again (5,064 units, 1 not built). `sources.json` is kept at the repo's 1-space JSON indent.
- em9305: 7 more lowered-asm units are C (init_native_child_30e910, 315d68, 316384, 319978, 31a900, 328814, init_native_enc_action_315dd8). Method as in wave 23: arc-gcc 15.2 -Os profile, `.waves/em-conv.sh` (same-size, diff read by hand). 319978 returns `a+826`, the incidental r0 from the stock code. Not ported because gcc's output has a different size and would shift later addresses: init_native_child_325c9c, 32cb2c, 32d598, init_native_dispatch_child_32543c. A further 14 small units (gen4: 31636c, 325cb4, 31c9f4, 315d50, 325648, 315c18, 31a920, 31a3ec, 3268e8, 3268cc, 326a48, 325284, dispatch_callback_31ca0c, pawr_queue_resume_31694c) were tried and all came out a different size (gcc does not use the IAR-style delay slots and absolute-address forms), so they stay asm. The large units (associated_callback_329888, 592 instructions) are not ported by hand, because the Renode sim does not execute the EM9305 and nothing could verify them.
- Metrics (em9305): asm-defined FUNC bytes 61,138 -> 60,984 of 209,394 (29.2% -> 29.1%). Compose 621/621, 6 libgcc/memcpy externals as before, final link `g2/build/g2c-w24-final-em9305` has 0 undefined, -Os kept.
- Other targets: no source changes, so their links stand.
- inventory-w24.json: unchanged versus w23 (em9305 unverified 1 / flag 1; apollo-main guess 5, stub 1, weak 3, inferred 2). No markers added or removed.
- Next: the 23 residual functions, then the em9305 units that need a hand-written ARC asm -> C pass (dispatch_child_31d6a4, radio_cb_31dfd0, associated_callback_329888), which are best done together with an ARC emulator check.

## Wave 25
- ARC execution check (new): QEMU arc-2026.03 harness that runs the stock lowered unit and the C candidate on random inputs with mocked externs and compares r0, call log, memory, callee-saved registers and sp. See `g2/docs/em9305-arc-harness.md`. A negative-control mutant is caught. Caveats: random inputs (not exhaustive), stub side effects and MMIO not modelled, arity taken from the candidate's extern prototypes.
- em9305: all 14 gen4 units are now C (31636c, 325cb4, 31c9f4, 315d50, 325648, 315c18, 31a920, 31a3ec, 3268e8, 3268cc, 326a48, 325284, dispatch_callback_31ca0c, pawr_queue_resume_31694c). Each is QEMU-equivalent on 500 tests; several are a different size (24-36 B vs 24-28 B), accepted because their references are symbolic. Metrics: asm-defined FUNC bytes 60,984 -> 60,632 of 209,430 (29.1% -> 29.0%). Compose 622/622 (new `qp_module_names.c`), same 6 external refs, final link `g2/build/g2c-w25-final-em9305` has 0 undefined, -Os kept, image 217,096 B.
- Absolute addresses: base vs +0x100 shifted-link audit in `g2/docs/em9305-abs-address-audit.md`. Fixed the 4 QP assert module-name strings (symbolic now). Remaining stock-address tables / function pointers / HCI handler addresses are listed there as NOT fixed. The image was already not stock-layout, so those literals are already wrong in our build.
- Big units (dispatch_child_31d6a4 ~885 asm lines, associated_callback_329888 ~1,190 lines, radio_cb_31dfd0) are now checkable with the harness but NOT converted this wave.
- Apollo: no source changes, so no apollo rebuild or paired sim was run (apollo-main image unchanged; earlier GPUJIM=1 results stand). Coverage: residual 23 -> 17 functions (1,746 -> 1,150 B) via six cited rows appended to `upstream-map.tsv` (elog_set_text_color_enabled, elog_output_lock, elog_set_filter_tag_lvl_default, elog_get_filter_tag_lvl, lv_label_revert_dots, poll_rtc_clksrc_edge_and_wait). New `verified-w25.tsv` (decompile-vs-source side-by-side, evidence per row): pcm22 sequences 13 (0x5A326C) and 11 (0x5A2EEA). strong 8,445 -> 8,453, weak 376 -> 374.
- Weak firm-up: a literal-set cross-check of the 84 stock-anchor weak functions was inconclusive (Ghidra shows literal-pool values as DAT_*, and the source factors them through helpers), so nothing was promoted on that basis. 374 weak remain; the rest need per-function side-by-side review like `verified-w25.tsv`.
- inventory-w25.json equals w24 except files_scanned (+1).
- Unresolved residual (17 fns, 1,150 B): 0x4416b8, 0x47e812, 0x47e93c, 0x48086a, 0x480ed8, 0x483030, 0x492114, 0x492198, 0x492200, 0x4bfdf4, 0x4c387e, 0x4c4058, 0x4d3dda, 0x4d94e6, 0x529ae4, 0x529d40, 0x53456c.
- Next: convert dispatch_child_31d6a4 / associated_callback_329888 / radio_cb_31dfd0 with the harness; turn the remaining hard-coded tables into symbols; continue side-by-side verification of the weak list (31 PCM2.x functions first).

## Wave 26
- Priority 1 (em9305 hard-coded stock addresses) done. See `g2/docs/em9305-abs-address-audit.md`. Found that the stock image begins with a 66-word interrupt vector table that our image lacked (stock 0x30ed96 sets `int_vector_base` to 0x302400), and about 160 stock functions that were reachable only by raw address (HCI vendor handlers, ISRs, vendor-NVM closure, lctr decode, PML/RF helpers). New units, all in `sources.json` (origin g2c-wave26): `application/stock_residual_code.c` (lowered stock asm, 5,673 instructions), `application/stock_residual_data.c` (vector table, radio tables, lctr pointer table, INI tail), `qpc-scheduler/stock_data_tables.c`. Regenerated `em9305_hci_cmd_tables.c` (symbolic handlers; first table now 34 records, count still 12: flagged). Linker script: vector table first and asserted at the NVM base, `opencfw_em9305_image_end` symbol.
- Metrics: compose 625/625, 0 duplicate strong symbols, final link `g2/build/g2c-w26b-final-em9305` 0 undefined, -Os kept, image 217,096 -> 237,884 B (the added bytes are code that was missing before, not growth of existing units). Shift-link audit clean (6 legitimate masks/flash-base/vector-pin literals, 2 coincidental u16 pairs). `.waves/abs/audit.py` now automates the audit.
- Caveats: the lowered code is asm, not C, so the asm share of the image goes up (asmshare script still reports 29.0% because it scores the stock function set); QEP/QF real functions still unported; two over-wide regions duplicate 1.5 KB of ported code; flags listed in the audit doc. inventory-w26.json: em9305 flag markers 1 -> 5 (new honest FLAG notes only).
- Priorities 2 (convert big units with the harness) and 3 (weak-list verification, PCM2.x first) were NOT started this wave. No apollo changes, so no apollo rebuild or paired sim.


## Wave 27 (checkpoint 1: upstream QP/C identified and ported to wrapper units; NOT yet integrated into the image)
- Priority 1 (QEP/QF = upstream QP/C): the stock 0x310d18..0x3117d8 is **QP/C 6.5.1** (GPL-3.0-or-later). Basis is code structure, not a version string: QMsm-era `QHsm` vtable `{QHsm_init_, QHsm_dispatch_}` at stock 0x33450c, `QActiveVtable {init, dispatch, start_, post_, postLIFO_}` at 0x3344e8, `QEP_reservedEvt_ = {0,1,2,3}` at 0x3344fc, `Q_REQUIRE_ID` ids 200/210/220 (init_), 400/410/510/520 (dispatch_), 410 (QK_sched_), `QPSet` as a 16-bit set with `QK_attr_` fields at stock offsets (readySet at +6, intNest at +4), and the six module-name strings (`qf_act`, `qep_hsm`, ...). Upstream pulled as submodule `third-party/upstream/qpc` at 416dcec8 (v6.5.1); no upstream file is modified.
- New port + wrappers (untracked until `sources.json` registration): `g2/src/em9305/qpc-port/{qep_port,qf_port,qk_port,qp_unit}.h` and seven `*_unit.c` that `#include` the unmodified upstream .c (QF_MAX_ACTIVE 16, QF_MAX_EPOOL 2, `clri/sync` critical section, `uint_fast8_t`=u8, `uint_fast16_t`=u32, `log2p1` ext insn, `Q_onAssert` -> `opencfw_em9305_assert`, SRAM globals pinned to stock addresses by section name). All seven compile clean with `-Os -Werror` (ARC profile). `qp_module_names.c` gained `qf_act` (0x334528) and `qep_hsm` (0x334530).
- Verification with the QEMU harness (random inputs, call-log + memory + callee-saved comparison, stock lowered unit vs upstream-compiled function): EQUIVALENT on 300-400 tests for `QActive_get_`, `QActive_post_`, `QActive_postLIFO_`, `QActive_ctor`, `QF_add_`, `QF_gc`, `QF_newX_`, `QF_poolInit`, `QMPool_get`, `QMPool_init`, `QMPool_put`, `QK_sched_`, `QHsm_ctor` (aligned `me`), `QHsm_top`. `QF_add_`, `QF_gc`, `postLIFO_` needed `--nor0` (void functions). Harness artifacts explained: stub module-name pointers (fixed by renaming to the shared symbol), QK_attr_/QF_active_ pins (linker PROVIDE), vendor `log2p1` unsupported by QEMU (harness-only soft-log2 via `OPENCFW_QEMU_SOFT_LOG2`, a bit-length substitution that is an assumption about the instruction).
- Found deviations: stock `QF_bzero` is `memset` when len != 0 (not the upstream loop), so upstream `QF_bzero` must stay excluded; stock `QF_init` differs from upstream (no `QF_timeEvtHead_` bzero; `QF_subscrList_` 0x801390, `QF_maxPubSignal_` 0x801364) so the hand-written `QF_init` stays. Stock `QHsm_ctor` sets `vptr` (the old stub ctor did not).
- Not yet verified: `QHsm_init_`, `QHsm_dispatch_`, `QActive_start_`, `QK_activate_` (need function-pointer mocks). Harness now has `--handlers/--mockobj/--mockact` (mock state handlers + mock vtable, assert aborts the test via longjmp); `QHsm_init_` matched the first 24 tests exactly, then the candidate hangs on test 25 (orig aborts on 2nd assert). Cause unknown (possibly the candidate loops where the stock aborts via assert); open.
- Not done this checkpoint: linker pins/discards in `g2-em9305.ld`, `sources.json` registration, removing `em9305_qpc_ctor.c` stub vtables, dead duplicate regions (priority 2), residual asm -> C (3), weak list (4). The built image and all six targets are unchanged by this wave so far (no source in the build touched except the two new module-name strings); apollo unchanged, no paired sim needed.
- Tooling edits (untracked `.waves/`): `qrun.py` (`--clamp`, `--chunks`, `--mockobj/--mockact/--handlers`, per-build stub files, pin PROVIDE symbols), `qemu-arc/h/driver.c`, `w27/{cc.sh,q.sh,mkorig.py}`.

### Wave 27 (step log, 2026-10-27 ~10:35 PM America/Chicago)
- QHsm_init_ EQUIVALENT on 300 QEMU tests (`--mockobj`). The earlier "hang" was the harness stub `Q_onAssert` returning (real one never returns); the stub now aborts the test at the first assert.
- QHsm_dispatch_ EQUIVALENT on 300 tests (`--mockobj --mockeq --nor0`; 6.5.1 dispatch_ is `void`). `mockeq` makes `temp == state` (required by assert 400); a counting mock `mhtop` replaces `QHsm_top` in the mock objects so state-machine walks terminate.
- QActive_start_ and QK_activate_ EQUIVALENT on 300 tests each, run against a combined stock unit (start + activate + QK_sched_ lowered together, so both sides run real callees): `--mockobj --mockact --noevt --args7`; 27k / 32k stub calls, 228 / 286 outcome classes.
- Harness additions: `--mockeq`, `--noevt`, `--args7` (r4..r6 args; `--clamp 4=,5=,6=`), QK_attr_ initialised (intNest=0) under `--mockact`, all `QF_active_[]` entries valid mock objects, dispatch-mock call cap, weak `QHsm_top` in the stub files.
- All QP/C 6.5.1 functions the stock image uses are now verified EQUIVALENT except QF_init / QF_run / QF_bzero (kept hand-written: documented stock deviations).
- QEQueue_init (`qf_qeq_unit.c`, upstream `qf_qeq.c`) EQUIVALENT on 300 tests; replaces `qpc-queue/qequeue_init.c`.
- **Integration done (10:45 PM America/Chicago):** 8 wrapper units registered in `sources.json` (origin `g2c-wave27`, flags `-I` qpc-port/include/src/qf/qk, `-ffunction-sections -fdata-sections -mno-sdata`; -Os profile unchanged). Removed the hand-written replacements `activate.c`, `event_gc.c`, `queue_pool.c`, `scheduler.c`, `log2p1_port.c`, `qpc-queue/qequeue_init.c`, the stub-vtable `application/em9305_qpc_ctor.c`, and the hand-written `QF_newX_` / `QMPool_get` / `QMPool_init` bodies in `controller_init.c`. Callers now use the upstream names (`QF_newX_`, `QMPool_get`, `QMPool_init`, `QK_activate_`, `QK_sched_`); `framework_init.c`/`framework_run.c`/`idle.c` keep stock bodies and are renamed `QF_init`/`QF_bzero`/`QF_run`/`QK_onIdle` (upstream QF_init / QF_run / QF_bzero are renamed `*_upstream_unused` in the wrappers and discarded). Link scripts (`g2-em9305.ld`, `.waves/abs/base.ld`, `shift.ld`): `/DISCARD/` for upstream functions the stock image does not link (QTicker, QF_remove_, QF_stop, QK_schedLock/Unlock, QHsm_isIn, QEQueue_post/get, ...) and pins for `QF_active_` 0x80131c, `QF_maxPool_` 0x801360, `QF_pool_` 0x801368, `QK_attr_` 0x801394.
- Build `g2/build/g2c-w27-em9305`: 626/626 compiled, 0 duplicate strong symbols; composed object lists 7 more unresolved names than before (`QF_onCleanup`, `QF_onStartup`, `QF_tickX_`, `QF_timeEvtHead_`, `QF_maxPubSignal_`, `QF_subscrList_`, `..._qf_qeq`), all referenced only from discarded sections; final link 0 undefined, image 239,152 B (was 237,884; the vtable stubs were replaced by real QActive_start_/post_/dispatch_/init_ code). Shift-link audit unchanged (6 insn masks, 2 data coincidences). `tools/build/sources.py check` ok (5069 units).
- Priority 1 complete (QP/C integrated, built, linked, audited, docs updated). inventory-w27: em9305 guess/stub/weak 0, flag 5, unverified 1 (unchanged). Starting priority 2 (dead duplicate lowered regions).
- P2 step: removed dead duplicates from stock_residual_code.c: 0x302664..0x3026a8 (ported as dispatch_child_302664), 0x3027c8..0x302844 (ported child_3027c8/3027f4/stack_check_302820), whole 0x329574..0x329842 (ported callback_329574 + child_329610). KEPT 0x3026a8..0x3027c8 and 0x302844..0x30299c: referenced by lowered callers (undefined L302760 when removing everything). Residual object text 17,536 -> 16,628 B. Rebuilding.
- Priority 2 complete: build g2/build/g2c-w27b-em9305 626/626 compiled, 0 duplicate strong symbols; final link g2c-w27b-final-em9305 0 undefined, -Os kept; image 239,152 -> 238,244 B (-908); shift audit unchanged (6 insn, 2 data, 0 undef refs). Apollo/other targets untouched, no paired sim. Next: priority 3 (residual asm -> C, harness) and 4 (weak list).
- P3 step 1 (wave 28): lctrSlvBigBeginOp 0x3288b0 (450 B asm) -> C (g2/src/em9305/lctr/lctrSlvBigBeginOp.c), QEMU EQUIVALENT 400 tests, 3 mutants caught; compiled 508 B (-Os). New harness bits: qrun --pre FILE (per-test RAM setup hook) and --outb name:argidx (stub writes a byte through an out-pointer, arg excluded from hash); tool .waves/w28/conv.py (rename/convert+register). Callees lctrBigTxCtrlQueuePeek/lctrSlvBisSetupTxData/lctrSlvBisTxData renamed from stock_<addr>. Not yet rebuilt.
- P3 step 1b (wave 28) BUG FOUND+FIXED in the lowering: `.waves/lower.py` silently dropped every DSP instruction whose mnemonic objdump prints on a continuation line after a "Warning: disassembly may be wrong" (ARCv2 DSP mpywhl/mpywhul, 233 occurrences in stock2.dis). 10 were missing in `stock_residual_code.c` (blank `"\n"` asm lines; incl. the kept 0x3026a8 64-bit divide helper and lctrSlvBisTxControl/TxData), so those lowered units were NOT byte-equivalent to stock. All 10 restored from stock2.dis (mpywhl/mpywhul), lower.py fixed (continuation-line mnemonic), the older initializer_lowers/ files were already correct. lctrSlvBigBeginOp's `{lo,hi}` pair was wrong too: hi = mpywhl(w+0x24, byte+0x18) + hi(mpydu), not ptr+hi; C fixed (FLAG: mpywhl = 32x16 multiply, product bits [47:16], per the ARCv2 DSP definition; QEMU arcem has no DSP so qrun now substitutes a base-ISA sequence on the orig side, `dspsub`, and rewrites short conditional branches to long forms for range). Harness: driver.c `pre_cb` (logs the pair the callback sees) now makes the pair observable; the old wrong C fails (8/60), fixed C EQUIVALENT 60.
- P3 step 1c (wave 28): lctrSlvBisSetupTxData 0x329230 (196 B) -> C (g2/src/em9305/lctr/lctrSlvBisSetupTxData.c, 224 B), QEMU EQUIVALENT 100, mutants 0x20->0x10 and >=0 -> >0 caught. Renamed callees lctrBisFlushStaleSdus (0x317534), lctrBisTxQueuePeek (0x317890). Residual text now 16,024 B. Not yet rebuilt.
- P3 step 1d (wave 28): lctrSlvBisTxControl 0x3293e0 (130 B -> 176 B C) and lctrSlvBisTxData 0x329464 (152 B -> 252 B C; macdu/ACC 64-bit callback arg, mpywhl hi word) converted (lctr/lctrSlvBisTxControl.c, lctrSlvBisTxData.c), QEMU EQUIVALENT 150 tests each with the callback path observed (pre_cb2); mutants caught: acc col2->col, kind +2->+3, mode mask 0x1c->0x18, mpywhl >>16 -> >>15. BbBleBisTxData 0x302fa8 renamed in the residual. Residual text 15,740 B.
- P3 step 1e (wave 28): lctrSlvBisTxCompletionInterleaved 0x3292f4 (116 B -> 156 B C) and lctrSlvBisTxCompletionSequential 0x329368 (118 B -> 172 B C) converted (lctr/lctrSlvBisTxCompletion*.c), QEMU EQUIVALENT 120 tests each, 7 mutants caught (+0xb0 / 0x198 / +0xc|+0x30 field offsets, >= vs >, cursor byte). The whole 0x3288b0..0x3294fc BIS slave family (7 functions) is now C. Residual text 15,504 B (was 17,536 at wave-28 start; 16,628 after priority 2).
- Build g2c-w28a-em9305 (630/630 compiled, includes the lower.py mpywhl fix + setuptx/txctl/txdata/BigBeginOp; comp pair installed after it): link/audit 6 insn hits, 2 data hits, 0 undefined refs; final link g2c-w28a-final-em9305 0 undefined, image 238,540 B (+296 B vs w27b: the 10 restored instructions and the C unit sizes).
- P3 step 2 (wave 28): QF_maxPubSignal_ (0x801364, enum_t) and QF_subscrList_ (0x801390, QSubscrList *) defined as pinned data (qpc-port/qp_unit.h externs, definitions in qpc-scheduler/framework_init.c, pins `.bss.stock_801364/801390` added to g2-em9305.ld, .waves/abs/base.ld, shift.ld; QP global size ASSERT extended). QF_init now uses the symbols (QF_subscrList_, QF_maxPool_, QF_maxPubSignal_, QF_active_, QK_attr_.actPrio/.lockPrio = QF_MAX_ACTIVE) instead of literal addresses; same stores as stock (checked in objdump). framework_init.c's sources.json entry gained the QP include flags. Remaining literal QK_attr_ users: framework_run.c (0x801396 lockPrio), startup_hook.c / controller_init.c (0x801398 intNest at QK_attr_+4... see next wave).
- P3 step 1f (wave 28): three more residual BIS helpers converted to C and verified in the QEMU-ARC harness (all EQUIVALENT: qpeek 100, flush 300, qpk 500 tests): lctr/lctrBigTxCtrlQueuePeek.c (0x3172ec, 24 B), lctrBisFlushStaleSdus.c (0x317534; note stock's `ld.as r0,[r0,76]` sits in the delay slot of the auxiliary_elapsed call, so arg0 = cfg->+0x130, not cfg), lctrBisTxQueuePeek.c (0x317890, 238 B; two wsf_event_at scan loops, mpyw/mpyuw/min semantics replicated). Removed from stock_residual_code.c; registered in sources.json (g2c-wave28). Build g2c-w28b pending.
- P3 step 3 (wave 28): weak-list verification, PCM2.2 transition sequences in audio/transition-snapshot/producers.c (the only PCM2.x file with weak rows; transition.c/completion.c do not exist). 12 more verified side-by-side (new g2/docs/reference/coverage-2.2.6.10/verified-w27.tsv; coverage3.py reads it): sequences 3, 8, 9, 10, 12, 14, 15, 16, 17, 19, 20, 21. Method: .waves/decompr.sh (Ghidra decompile + resolved literal-pool values; new G2DecompR.java / .waves/words.sh) and every pool address checked against the source literals (0x200742d4..e8 publish block, 0x2005665c table, 0x4002004c/44/48/80/37c, 0x400083e0/40008064 wait). No source diffs found. Weak 374 -> 362 fns (52,054 B). Still unverified: sequences 0,1,2,4,5,6,7,18,22,23 (+24..26 empty stubs) and the helper functions; pcm22_sequence_10 is a known dedupe of 8.
- Build g2c-w28b-em9305 (BigBeginOp/SetupTx/TxControl/TxData + Completion pair + 3 queue helpers + pinned QF_subscrList_/QF_maxPubSignal_): 635/635 compiled, 0 duplicate strong symbols; abs audit 6/2/0 undef 0; final link g2c-w28b-final-em9305.bin 238,680 B; nm confirms QF_maxPubSignal_=0x801364, QF_subscrList_=0x801390. sources.py check: 1 not built (unchanged, presumed resident_rom_thumb_set.S).
- P3 step 1g (wave 28): lctrDecodeCtrlPduCasePduChannelMapInd (0x319268, 48 B) converted to C (lctr/lctrDecodeCtrlPduCasePduChannelMapInd.c) and verified EQUIVALENT in the QEMU-ARC harness (300 tests, 140 distinct outcome classes). Removed from stock_residual_code.c (stock_residual_data.c reference renamed, still symbolic); registered in sources.json. Skipped lctrDecodeCtrlPduCasePduConnUpdateInd (0x31936c): it uses `mpywhul` whose exact semantics are unproven (the Bluetooth supervision-timeout rule `(latency+1)*interval < timeout*4` suggests a plain 32x16 product, but the campaign model is the DSP [47:16] reading), so it stays lowered asm until the mpywh* semantics are settled (same FLAG as BigBeginOp). Build pending.
- P3 step 1h (wave 28): lctrDecodeCtrlPduCasePduCisTermInd (0x319310, 40 B) converted to C (lctr/lctrDecodeCtrlPduCasePduCisTermInd.c), harness EQUIVALENT (300 tests; memory hash covers the three byte copies), removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1i (wave 28): lctrDecodeCtrlPduCasePduPwrCtrlReq (0x3195cc, 38 B) converted to C (lctr/lctrDecodeCtrlPduCasePduPwrCtrlReq.c), harness EQUIVALENT (300 tests), removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1j (wave 28): lctrDecodeCtrlPduCasePduPwrCtrlRsp (0x3195f4, 42 B) converted to C (lctr/lctrDecodeCtrlPduCasePduPwrCtrlRsp.c), harness EQUIVALENT (300 tests), removed from stock_residual_code.c, registered in sources.json. Build pending.
- Build g2c-w28c-em9305 (+4 lctrDecodeCtrlPdu cases: ChannelMapInd, CisTermInd, PwrCtrlReq, PwrCtrlRsp): 639/639 compiled, 0 duplicate strong symbols; abs audit 6/2/0 undef 0; final link g2c-w28c-final-em9305.bin 238,688 B (+8 vs w28b); sources.py check still '1 not built'. Residual lowered asm extents now 14,714 B (14,882 B before this step).
- P3 CORRECTION (wave 28): the harness model of ARCv2-DSP `mpywhl`/`mpywhul` was WRONG (earlier rows for lctrSlvBigBeginOp, lctrSlvBisTxControl, lctrSlvBisTxData assumed product bits [47:16], i.e. `(x*(int16)y)>>16`). Public docs (ARCv2 DSP ISA, binutils arc-opc/arc-dis, GCC arc builtins, nSIM, QEMU-arc) give only "32x16 integer multiply" and do not pin the result slice; the slice is settled from firmware usage instead: `mpywhl r0,r0,72/656/912/784/1250/1000/625/0xb08` and `mpywhl d,0x01010101,byte` are plain scale/µs/replicate multiplies (only the LOW 32 bits make sense), the BigBeginOp/TxControl/TxData `{+0x24:+0x20} * byte(+0x18)` is a 64-bit multiply (mpydu for lo/hi of the low word + mpywhl(+0x24,byte) added to hi), and ConnUpdateInd's `(latency+1)*interval < timeout*4` is the Core-spec supervision rule. So `mpywhl d,x,y` = low32(int32 x * int16 y[15:0]); `mpywhul` = low32(uint32 x * uint16 y[15:0]). Confidence high, unproven on silicon. Fixed: .waves/qrun.py dspsub (now emits sext/zext16 + mpy), the three C files (`hi = W32(big+0x24)*b + (prod>>32)`, FLAG lines removed). The old harness runs had passed only because the model and the C shared the wrong shift; re-run with the corrected model: BigBeginOp 100/100, TxControl 100/100, TxData 100/100 EQUIVALENT, and a negative control (old >>16 C) now MISMATCHes 35/100 in TxControl, so the harness discriminates. This changes the C (and image) of those three functions; build pending.
- P3 step 1k (wave 28): lctrDecodeCtrlPduCasePduConnUpdateInd (0x31936c, 106 B) converted to C (lctr/lctrDecodeCtrlPduCasePduConnUpdateInd.c) with the corrected mpywhul model; harness EQUIVALENT (800 tests, targeted pre-hook for the latency-500 edge and product==timeout*4 equality; mutants `lat*iv`, `>` vs `>=`, `lat<499/501`, `timeout<<3` and `window>` are all caught). Removed from stock_residual_code.c (residual extent sum now 14,608 B), registered in sources.json. Build pending.
- P3 step 1l (wave 28): lctrGetBigRefTime (0x31afd4, 38 B) converted to C (lctr/lctrGetBigRefTime.c): BIG table entry lookup (base 0x805c3c, 0x200-byte entries, handle-7), state byte==1 returns the +0x130 word and stores +0x134 through the optional out pointer. Harness EQUIVALENT (300 tests, 102 outcome classes; a handle-offset mutant is caught). Removed from stock_residual_code.c (extent sum 14,570 B), registered in sources.json. Build pending. lhciVsExtDecodeCmdPkt (0x332b70) skipped: it calls a ROM address (0x101e48) the harness cannot mock.
- P3 step 1m (wave 28): three more decode cases converted to C in lctr/ and harness-verified EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduCteReq (0x3193d8; feature bit 2, type 2, splits src[1] into pdu+0xc/+0xd), lctrDecodeCtrlPduCasePduCteRsp (0x319400; feature bit 1 only), lctrDecodeCtrlPduCasePduMinUsedChainInd (0x319450; the first harness run caught a wrong `bmsk_s r2,r2,2` reading: ARC `bmsk` masks bits [u:0], so it is &7 not &3; fixed, a `>219` mutant is caught; it validates a PHY mask and a count in 2..37, so the stock name is probably a typo for MinUsedChannelsInd, FLAG: name kept, semantics guessed from the range). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1n (wave 28): five more decode cases converted to C in lctr/ and harness-verified EQUIVALENT (300 tests each; shared pre-hook `.waves/w28/mk.sh` generates orig/pre/run for the "flag bit + packet type + child validator" shape): lctrDecodeCtrlPduCasePduCisInd (0x319298; word 0x805a94 bit 29, type 0x10, child packet_child_32dbe4), CisReq (0x3192c0; bit 29, type 0x24, child 32dc40), CisRsp (0x3192e8; len==1 rejected, bit 28, type 9, child 32dd20), ConnParamReq (0x319338; byte 0x805a94 bit 1, type 0x18, child 32de08), ConnParamRsp (0x31935c; len==1 rejected else tail-calls ConnParamReq; 110 outcome classes). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1o (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduPeriodicSyncInd (0x3194f4; byte 0x805a97 bit 1, type 0x23, child 32dffc), PeriodicSyncWrInd (0x319518; same, type 0x2b, child 32e068), and the two copies in the stock block "unnamed 0x31948c" which are two identical functions at 0x31948c/0x3194ac (feature byte 0x805a97 bit 2, type 2, copy src[1] to pdu+0xc). The opcode dispatch table lctr_decode_actions_334d0c is indexed by the LL control opcode (BT Core Vol 6 Part B 2.4.2): slots 0x1d/0x1e are CLOCK_ACCURACY_REQ/RSP, so the two are named lctrDecodeCtrlPduCasePduClockAccuracyReq/Rsp (FLAG: names from the opcode position, not from stock symbols). Same table position also confirms 0x19 = MIN_USED_CHANNELS_IND for MinUsedChainInd (FLAG removed). Residual extent sum now 14,158 B. Build pending.
- P3 step 1p (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlPduCasePduPhyReq (0x31953c; byte 0x805a95 &9, type 3, child 32e114), PhyRsp (0x319564; len==1 rejected else tail-calls PhyReq), PhyUpdateInd (0x319574; len==0 rejected, &9, type 5, child 32e128), PwrChangeInd (0x3195a0; byte 0x805a98 bit 2, copies src[1..4], type 5). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1q (wave 28): four more decode cases converted to C in lctr/, harness EQUIVALENT (300 tests each): lctrDecodeCtrlCasePduRejectInd (0x3191ac; stores 0xff/err code, type 2), lctrDecodeCtrlCasePduVersionInd (0x3191c4; child 32e1f4, type 6), lctrDecodeCtrlPduCasePduChReportingInd (0x319208; len!=0, byte 0x805a98 bit 7, copies src[1..3], type 4), lctrDecodeCtrlPduCasePduChStatusInd (0x319234; its `lp` hardware loop is a 10-byte copy src[1..10]->pdu+0xc; QEMU does execute the loop, a 9-byte mutant is caught, so `lp` code IS harness-testable when the loop has no MMIO). Removed from stock_residual_code.c, registered in sources.json. Build pending.
- P3 step 1r (wave 28): the rest of the small LL control PDU decode cases converted to C in lctr/, each harness-EQUIVALENT (300 tests): lctrDecodeCtrlPduCasePduPerFeatureReq (0x3194cc; len==1 rejected, byte 0x805a94 bit 3, child 32dfe8, type 9), RejectExtInd (0x319620; bit 2, copies src[1..2], type 3), and from stock blocks the image calls 'unnamed'/shares: FeatureReq (0x319414; len==0 rejected, then the FeatureRsp body), FeatureRsp (0x319420; child 32dfe8, type 9), LengthReqRsp (0x319438, referenced by both the LENGTH_REQ and LENGTH_RSP slots; child 32deac, type 9), TerminateInd (0x3196ec) and UnknownRsp (0x319700) (copy src[1], type 2), and lctrDecodeCtrlPduCaseDefault (0x319204, always 0x19, 8 table refs). FLAG: the six unnamed ones are named from their slot in the stock opcode dispatch table 0x334d0c vs BT Core Vol 6 Part B 2.4.2 opcode numbers (consistent with every named neighbour), not from stock symbols. Removed from stock_residual_code.c (extent sum 13,706 B; was 17,536 B at the start of wave 28), registered in sources.json. Only SubrateInd/SubrateReq (0x319644/0x319698, 82/84 B) remain of the decode cases. Build pending.
- P3 step 1s (wave 28): lctrDecodeCtrlPduCasePduSubrateInd (0x319644, len==0 rejected) and SubrateReq (0x319698, len==1 rejected) converted to C in lctr/ (byte 0x805a98 bit 5; five little-endian halfwords src[1..10] -> pdu+0xc..0x15; type 0xb), harness EQUIVALENT (300 tests each; the first SubrateReq run hung because my lowering extent cut off the function epilogue, fixed to 0x319698-0x3196ec). All 0x3191xx-0x3196xx LL control PDU decode cases are now C. Residual extent sum 13,540 B. Build pending.
- Build g2c-w28d-em9305 (steps 1k-1s: corrected-mpywh BigBeginOp/TxControl/TxData, ConnUpdateInd, GetBigRefTime and 30 more LL control PDU decode cases): 671/671 compiled, 0 duplicate strong symbols; abs shift-link audit 6/2/0 undef 0 (unchanged); final link g2c-w28d-final-em9305.bin 238,692 B (w28c 238,688 B); sources.py check still '1 not built'. Residual lowered asm extent sum 13,540 B (14,714 B before this round, 17,536 B at the start of wave 28).
- P3 step 2a (wave 28): ROM-call mocking needs no new harness feature: a ROM call goes through a named facade `opencfw_em9305_rom_<name>_<hex>` (em9305_link_closure.c, absolute IROM address inside), and `--rename 0x101e48=<facade>` on the stock side turns the lowered `jl 0x101e48` into an ordinary stub call that both sides log. lhciVsExtDecodeCmdPkt (0x332b70, 36 B, the boot-installed callback) converted this way (lctr/lhciVsExtDecodeCmdPkt.c + new facade opencfw_em9305_rom_lhci_vs_ext_101e48 with args (opcode halfword, len byte, arg, 0xff, 256-byte stack scratch)); harness EQUIVALENT (200 tests; a 0xff->0xfe mutant is caught). What the ROM routine does is unknown (ROM not in the repo). Removed from stock_residual_code.c; controller_init.c prototype updated. Build pending.
- P3 step 2b (wave 28): the unnamed 202-B block at 0x302a1c was two things: a 4-byte `b 0x30299c` veneer (the word after AOAD_Init in ini_record_335820) and a verbatim stock duplicate of 0x302a20 that controller_init.c already carries as C (`opencfw_em9305_controller_initialize_stack`). Harness (new `--deref name:NWORDS[:idx=mask]` option hashes the words a stub's pointer argument points at, so struct contents built on the stack are compared) shows the C EQUIVALENT to stock on 100 tests, and a changed `capabilities` constant is caught. Residual block removed (-198 B asm); veneer is now C (application/AOAD_Init_veneer.c, EQUIVALENT, 50 tests) and the data word renamed to opencfw_em9305_AOAD_Init_veneer_302a1c. Note: wsf_os_register_start_304610 in em9305_link_closure.c is still an empty stub, so initialize_stack has no caller (pre-existing).
- P3 step 2c (wave 28): the EM9305 SDK `em_system` vendor-command handlers (EMSG_*/EMSMM_*/EMSRC_*, 0x304bb4..0x3058c0, ~4 KB, all of the shape handler(op, plen, params, ctx, resp): write the status at resp[3], then reply through ROM 0x102588(op, resp length, ctx, resp, after-callback)) are being converted as a family with the harness. New in the tooling: `fam.sh` (one-line harness per handler, ROM calls mocked through facades via --rename/--arity), `--mmio` (maps and hashes the 0xf00000..0xf05000 MMIO window as RAM so register read-modify-write order is compared), 5th-argument hashing for 5-arg stubs (4-arg hashing silently dropped the callback argument), `mut.sh` (mutant check), `inst_em.py` (installer) and `chkref.py` (every opencfw_em9305_stock_X reference has a definition). Batch 1 installed, 21 functions (EMSG_CallWeakFunction + callback + weak default hook, three reset commands + callbacks, GetEmCoreInformation, SetBootModeFlags + callback, SetPublicAddress, SetRssiOffset, SetSleepOptions, SetUartBaudRate + callback, SvldMeasurement, NVMEraseFull, NVMEraseMain, status-1 reply), each EQUIVALENT on 100 tests with at least one mutant caught for the data-dependent ones. Three new ROM facades in em9305_link_closure.c (0x102588 reply, 0x1020e8 delay, 0x104b98 uart baud: the last two names are inferred from use). Nameless handlers are `emsys_*_<addr>` because the command id/name is not recoverable from the sources. Global labels added for 0x30ef04/0x30ef0c (NVM erase wrappers, `b nvm_op` with op 8 / 4) so the C can call them.
- step 2c cont.: e22-e25 (EMSMM_NVMErasePage/ReadAtAddress/WriteAtAddress/WriteContinue) installed; callees 0x3059d8/0x305a20/0x30ef14 given global labels in the residual. WriteAtAddress/WriteContinue only reply when op == 0xfd03/0xfd04 on success (the original compares the op against a long immediate).
- step 2c cont.: e26-e29 (four identical 'status 1 if NVM magic valid else 0x2f' handlers, opcodes 0xfd81..0xfd84, mutant caught) and e30-e32 (EMSRC_EmCoreReceiver154TestEnd/ReceiverTest/ReceiverTestEnd, opcodes 0xfccf/0xfcc5/0xfcc6) installed, all EQUIVALENT on 100 tests with mutants caught. New harness option `--outp name:argidx:nbytes[:argidx:nbytes]` (qrun.py + driver.c stub_outp): hashes an out-parameter buffer on the stack or in the RB window before the call, then fills it with PRNG bytes, so the C is checked on how it uses the callee's out values without depending on stack layout. Found: 0x30592c..0x305940 (6 stubs) are weak default hooks returning 0xc (the EMSRC test functions call them); em_system_command_gap 0x30592c is 6 stubs + a region classifier (0x305944) + memory read (0x3059d8) + write (0x305a20), a later conversion target. The HCI opcode for each handler is in em9305_hci_cmd_tables.c.
- P3 step 2d (wave 28 checkpoint, Oct 28 2026 ~2:30 AM CT): rebuilt after the em_system handler batches (build w28f): 705/705 units compile, 0 duplicate strong symbols, shift-link audit 6 insn / 2 data-word hits (unchanged, expected), undef 0, final link OK, image 238,436 B (was 238,692). First build failed only on -Werror=unused-parameter in six handlers (fixed with (void) casts). Installed this wave: 32 em_system handlers (e1-e32), 3 new ROM facades, 5 new global labels in the residual (0x30ef04, 0x30ef0c, 0x3059d8, 0x305a20, 0x305930). Not yet paired-sim'd: em9305 only, apollo unchanged, so no sim required.
- step 2e (wave 28): em_system_command_gap 0x30592c (392 B) converted: 6 weak default hooks that return 0xc (0x30592c/30/34/38/3c/40; callers: EMSRC receiver/adv-pattern/scan/transmitter test commands), emsmm_region_id_305944 (memory-map classifier), emsmm_read_memory_3059d8 and emsmm_write_memory_305a20 (word-copy ROM facades 0x100ca8/0x100d20 added; 0x30f014 flash-write helper stays asm). 9 functions EQUIVALENT on 100 tests. New harness option --stubret name:v1:v2:... makes a stub return from a fixed list; it was needed to reach the flash-write branch (the random stub returns 2/3 too rarely, so the first mutants survived). With it the region-base, region-accept and return-code mutants of the write helper are all caught (the list must contain duplicated 1/2 entries; the distribution of the hash index is uneven). mut2.sh passes extra opts to mutants.

### P3 step 2f (Oct 28 2026, ~3:40 AM America/Chicago): EMSRC e42-e45
- Converted EMSRC_EmCoreScan15_4 (0x3052dc, HCI 0xfcce), EMSRC_EmCoreStartAdvPattern (0x305328, 0xfcc9), EMSRC_EmCoreTransmitterTest (0x305358, 0xfcc1), EMSRC_EmCoreTransmitterTestEnd (0x3053b4, 0xfcc2) to C. Each is EQUIVALENT to the lowered stock on 100 QEMU-ARC tests; 24 mutants were killed (status codes, parameter indices, int8 sign, loop bound 0x63, reply length 3, delay 0x32, LE32 shifts, W32 source).
- Harness: stub arg names extended to 8 (`g`,`h`) for the 7-arg hook 0x30593c; `--outp` now hashes args 5/6 correctly (out index >= 4 was an IndexError).
- Survivors (2, by construction): in TransmitterTestEnd the loop's `[0x8019a1] == 0` arm (`>= 0x64` bound and the `[0x8019ac]` test) is unreachable while the flag byte is static, which the stubbed delay cannot change. Kept verbatim from the stock branch structure (flag is volatile and set by ISR code).
- 0x333b48 (the transmitter-test parameter check) got a global label in stock_residual_code.c; still residual asm.
- Note: TransmitterTestEnd replies with length 3 (status + LE16 count) but also zero-writes resp[6..7]; copied verbatim. The reply length counts from resp[3].
- Not yet rebuilt (build after the next batch).

### P3 step 2g (Oct 28 2026, ~4:00 AM America/Chicago): second EMSRC command table, e46-e52
- Converted to C, each EQUIVALENT to the lowered stock on 100 QEMU-ARC tests with all mutants killed (about 50 mutants): EMSRC_ReceiverTest (0x305448; opcodes 0xfcc5/0xfccc/0xfccd), emsrc_receiver_test_end_3054f0 (0xfcc6; name inferred), emsrc_status1_reply_305548 (0xfcc3), EMSRC_SetRfPower (0x30555c, 0xfcc4), EMSRC_TransmitterTest (0x3055ac; 0xfcc1/0xfcca/0xfccb), EMSRC_TransmitterTestEnd (0x3055f8; 0xfcc2), EMSRC_setAOADCteConfig (0x305658; 0xfcce).
- Harness: `--outp` size with bit 0x1000 set skips hashing the incoming bytes (for uninitialised stack out-structs); `--stubret` now also fills `--outp` buffers; `--stkw 5` for 20-byte config structs.
- Misread caught by the harness: SetRfPower stores the return of radio_mode_312290 (not the level byte) at resp[5].
- Interrupted mutant runs left `cand/e47.c` and `e49.c` mutated; restored from /tmp/mut_*.good and rerun (both killed).
- 0x302760 got a global label; chkref `bad 0`; residual extent sum now 10,142 B (was 11,502).
- Next: rebuild into a fresh dir, then EMSS_Le*.

### P3 step 2h (Oct 28 2026, ~3:50 AM America/Chicago): build w28g checkpoint
- Fresh build `g2/build/w28g`: 725/725 units, 0 duplicate strong symbols, audit insn hits 4 / data-word hits 2 (was 6 / 2; two absolute-address hits went away with the converted handlers), undef 0, final link OK (`w28g-final-em9305`).
- Image 238,404 B (w28f: 238,436 B; stock-extent residual sum 10,142 B, was 11,502 B). `sources.py check` result as in earlier waves.
- Remaining: EMSS_LeDecrypt/LeDecryptKC/LeEncrypt/LeEncryptKC/LeRand (0x3056ac..0x3058c0), remaining unnamed blocks, weak list, PCM2.2 Ghidra retry, harness doc.

### P3 step 3a (Oct 28 2026, ~4:40 AM America/Chicago): EMSS_Le* handlers e53-e57
- Converted EMSS_LeDecrypt (0x3056ac, HCI 0xfc8a), EMSS_LeDecryptKC (0x30573c, 0xfc8b), EMSS_LeEncrypt (0x3057b8, 0xfc88), EMSS_LeEncryptKC (0x305844, 0xfc89), EMSS_LeRand (0x3058c0, 0xfc87). All EQUIVALENT on 100 QEMU-ARC tests; about 45 mutants killed (byte reversal indices, flag, lengths, status codes, config constants, plen boundary).
- New facades in em9305_link_closure.c: rom_le_cipher_1060c4 (6 args), rom_le_cipher_kc_10093c (4 args), names inferred from the callers. rom_random_10a7f8 now has the 3-argument signature its callers already use (was declared with 1 argument; same tail-call code).
- Harness: new `--derefb name:argidx:nbytes:hexmask[:...]` hashes selected bytes of an in-parameter buffer (skips uninitialised stack padding); combines with `--outp` and `--stubret`. `stub_derefb` in driver.c.
- FLAG: LeRand's stack config struct is largely uninitialised in stock; C zeroes byte 3 of word 0 and leaves the rest untouched.
- Not rebuilt yet.

### P3 step 4a (Wed Oct 28 2026, before the w28h build): tiny unnamed/named blocks to C
- Converted 20 tiny functions (`.waves/w28/inst_small.py`, compiled -Os instructions compared with the lowered stock code; no harness run for these): noop 0x302d80, 0x30f6d8, 0x30fab0, 0x30fabc, 0x313778, 0x3137f4, 0x3137f8; PML_ClearConfigurationModeFlag (0x30f1f8), PML_ClearModeFlag (0x30f208), PML_SetConfigurationModeFlag (0x30f710; name INFERRED from the Clear sibling, same bit 23 of 0xf00430) plus its byte-identical copy 0x30f720; PML_VoltMonitorReStoreConfig (0x30fa9c); 0x30f6c8 timer/mode update, 0x30f6dc (restore then 0x30f6c8), 0x30f934 (two empty calls), dispatch_child_30fab4 (tail to common_activate_310580); 0x311f84 (u16 store at 0x805fdc), 0x3122f0 (RSSI offset byte at 0x80fd5e), 0x3335c8 (2 when transport idle is 0 else 1). Names marked inferred in each header.
- The residual copy of 0x30fab8 (`b common_activate_310580`) was dropped: the same address is already defined in C by dispatch_child_30fab8, so this also removes a duplicate.
- chkref: bad 0. Not yet rebuilt (next fresh dir w28h).

### P3 step 5 (before the w28h build): harness doc
- g2/docs/em9305-arc-harness.md: added the em_system handler workflow, ROM-mocking recipe, new options (--derefb, --outp no-hash bit, --stubret+--outp, 8-arg stubs) and the pitfalls.

### P3 step 6 (before the w28h build completed): PCM2.2 Ghidra retry + weak list
- The Ghidra headless retry worked this time (`.waves/decompr.sh`, one or two addresses per call, run in the background). Sequence addresses come from the dispatch table at 0x200002a8 (init image offset 680).
- Verified side-by-side against the source (pool values resolved, writes and order compared): sequences 0, 1, 2, 4, 6, 7, 18, 22, 23 (9 rows appended to g2/docs/reference/coverage-2.2.6.10/verified-w27.tsv). coverage3.py: weak 362 -> 356 fns, 52,054 -> 50,074 B; residual unchanged (17 fns, 1,150 B).
- **FINDING (not fixed, not added to the TSV): pcm22_sequence_5 (stock 0x5A26BE) differs from audio/transition-snapshot/producers.c.** Stock has the same early exit as sequence 0: if (0x400083e0 & 1) and next == [0x200002a4], it runs ton_adjust(ton,next), sets 0x40020044 field = nc, calls the timer stop (FUN_004802ce = pcm22_timer_stop) and sets byte 0x20004540 = 0x1a, then returns before publishing. The source has no such branch. The rest of the body matches. Proposed fix: copy sequence 0's early block to the top of sequence 5 (needs next/old/ton, nc, `W(g2_stock_ram_20000290+0x14)`). It is an apollo-main source change, so it needs an apollo rebuild and paired sim; left for the user to approve. Sequence 0..4,6..23 otherwise verified or earlier verified; still unverified: 24..26 (empty stubs) and the helper functions.

### Build w28h checkpoint (Wed Oct 28 2026, ~4:21 AM America/Chicago; earlier "~" times in steps 4a-6 above were estimates, the clock is the box clock)
- g2/build/w28h (e53-e57 + the 20 small functions): 749/749 units compiled, 0 duplicate strong symbols, 0 undefined. Audit: insn hits 4, data-word hits 2 (unchanged), undef 0. Final link g2/build/w28h-final-em9305: 0 undefined, -Os kept, image 238,424 B (238,404 B at w28g, +20 B). Residual extent sum 9,324 B (10,142 B at w28g). sources.py check: 5,192 units, 4,871 source files, 1 not built (unchanged).
- Only em9305 changed: no apollo rebuild or paired sim needed.

### P3 step 7 (Wed Oct 28 2026, ~4:30 AM America/Chicago): pcm22_sequence_5 fixed to match stock
- Approved by the user. audio/transition-snapshot/producers.c: pcm22_sequence_5 now starts with the same early exit as pcm22_sequence_0 (same helpers and symbols: W(0x400083e0)&1 test, `g2ref_g2_stock_ram_20000290+0x14` compare with `next`, stock_ton_adjust, field(0x40020044,nc,0,7), pcm22_timer_stop, B(g2ref_g2_stock_ram_20004530+0x10)=26). Verified against the Ghidra decompile of 0x5A26BE (pool 0x200002a4 = 20000290+0x14, 0x20004540 = 20004530+0x10). Apollo rebuild `g2c-w28i-apollo-main` and a paired GPUJIM=1 sim follow.
- Apollo build `g2c-w28i-apollo-main`: 2870/2870 compiled, 0 duplicate strong symbols, 24 unresolved in the composed object (same as the prior apollo build), sim link ok (bin `simw28i.bin`, 3,862,175 B).
- Paired sim (GPUJIM=1 WIDE LISTPAGE PAIRED NOSILENT TOUCHONLY; hooks lst=common_list_container_inject_event, lcb=common_list_event_callback, resolved from each ELF/stock symbol suffix; one `single` tap + release, a GUESS at the earlier TOUCHX): runs nsw28i (ours) vs nsstk2 (stock2210). Hooks lst 1 / lcb 1 per arm on both. 22 notifs each. After masking the seq/CRC bytes (the first-payload byte that differs by a constant 0x1a, a counter offset) they are identical except idx 1 and 4 (heartbeat counters), the same as the earlier ns68/nsstk result. No regression. The touch scenario does not exercise the new sequence-5 branch (unverified; no PCM2.2 hook was run), so this only shows nothing else moved.
- verified-w27.tsv: added pcm22_sequence_5 (0x005A26BE). coverage3: weak 355 fns / 49,560 B, residual 15 runs / 1,150 B.

### P3 step 8 (Wed Oct 28 2026, ~4:45 AM America/Chicago): apollo unresolved-symbol check (w28i)
- Composed object `g2c-w28i-apollo-main`: 24 undefined symbols = 21 `U` + 3 weak (`g2_iar_fputc_weak`, `g2_iar_putchar_select_a/_b`, by design weak, resolve to 0). The 21 U are all linker-script symbols (`__bss_end/__bss_start/__data_end/__data_load_start/__data_start/__dtcm_bss_*/__start_kvdb_migration/__stop_kvdb_migration/_estack/_etext/_sstack/_stext`) or `nrf_fuel_gauge_*` from the vendor library; every one is defined in the final ELF.
- Final link (`g2c-w28i-final-apollo-main`): 0 `undefined reference` in link.log, `nm -u` on the ELF = 0.
- Versus the previous apollo build (`g2c-sim68-apollo-main`): that composed object had 26 (the same 24 plus `__stack_chk_fail` / `__stack_chk_guard`), so w28i is a strict subset, not an identical set; the two stack-protector symbols are no longer referenced. The `report.json` count of 24 for w28i is therefore correct, but "same as prior" was only true for the 24.

### P3 step 9 (time not recorded; between 4:49 and 4:53 AM America/Chicago): 0x30611c identified; ISR-wrapper family
- 0x30611c is the vector-table slot 23 handler (`opencfw_em9305_vector_table`, `stock_residual_data.c`): slot 21 = Cmp0 (0x306050), slot 22 = default (30f170), slot 23 = 0x30611c, slot 24 = Cmp3 (0x3061e4). Body: full context save, `st 4,[0xf00820]` (1<<2), sync, call 0x333404 with arg 2, restore, rtie (Cmp0 writes 1/arg 0, Cmp3 writes 8/arg 3). Header comment now `IRQHandler_ProtocolTimerOutCmp2`, FLAGGED as an inferred name (not in the stock symbol table); the symbol stays `opencfw_em9305_stock_30611c`.
- ISR family finding: 19 `rtie` blocks in stock_residual_code.c share a ~44-instruction compiler-style frame (st.aw r0,[sp,-88] ... saves r0-r12, r30, blink, r58/r59, lp_count, lp_start/lp_end, aux 1409/1411; `rtie`). Only the middle (MMIO ack plus indirect callback or call) differs. The ARC gcc `interrupt` attribute does not emit this frame (it saves only what it needs), so a C rewrite would not be byte-identical and would silently drop the context save. They stay residual asm; no conversion attempted. No size change (coverage3 residual runs 15 / 1,150 B unchanged: this metric counts the non-first-party runs, the em9305 asm is counted in the 9,324 B extent sum).
- 0x311c14 (210 B, channel-2 radio completion IRQ body, root record 0x8019d4 = the `radio_schedule_311ef0` record: +0 pending, +4 callback, +8 fallback callback, +0xc u16 base, +0xe u16 delta): written as C in `.waves/w28/cand/irq2.c`, NOT installed. Semantics read from the lowered code: status 0xf00860 bit0 -> ack 1 at 0xf00868, refresh(1), delta = base - byte(0xf0407c) + (field(lr 1686,>>8,13 bits) != 0x1fff ? ~field : 0) after `sr 4,[1666]`, store delta, exit unless bit 7 of 0xf04054, then call callback(0, delta) (callback = +4, else +8, clearing +0/+4); bit4 -> ack 16, restore(), same measure, callback(2, delta). The ARC gcc -Os build is 248 B vs stock 210 B (no `xbfu`, extra extb/exth, different branch layout), and I have not run it in the harness (needs aux-register and indirect-call mocking), so the stock block stays in stock_residual_code.c. Exact reproduction via rewriting is not achievable with this compiler; the next step would be a harness equivalence run (--mmio) for behaviour only.

### P3 step 10 (time not recorded; before 4:45 AM America/Chicago): PCM2.2 sequences 24-26
- Dispatch-table entries 24/25/26 = 0x5A40B0 / 0x5A40B2 / 0x5A40B4 (2 bytes apart). Ghidra decompile of each: empty `return;`. Matches the empty `pcm22_sequence_24/25/26` in producers.c. Three rows added to verified-w27.tsv (coverage3 weak count unchanged at 355 fns / 49,560 B; these were not in the weak count). Correction: 25 of 27 PCM2.2 sequences have TSV rows; sequences 11 (0x5a2eea) and 13 (0x5a326c) have none and are still to be verified. The static helpers (setup_profile, load_core, switch_low, doubled_boost, publish, finish_previous) were compared as part of each sequence's decompile but have no stock symbol of their own to cite, so no separate row.
- No em9305 code changed this step (comment-only edit at 0x30611c), so no em9305 rebuild; last built image remains w28h (238,424 B, residual extent sum 9,324 B).

### P3 step 11 (time not recorded; before 4:53 AM America/Chicago): shared ISR frame, 11 handler bodies in C (user request)
- New `g2/src/em9305/application/em_irq_frame.h`: the stock 88-byte frame (save r0-r12/r30/blink/r58/r59/lp_count, aux lp_start/lp_end/1411/1409; restore; rtie) as one asm template (`EM_IRQ_SAVE`/`EM_IRQ_RESTORE`) plus `EM_IRQ_HANDLER(SYM, BODY)` = save, `bl BODY`, restore. The save/restore were checked byte-for-byte equal across the stock handlers by script (the 11 standard ones; RadioRx/RadioTx differ only in having the call in the `bl.d` delay slot). Bodies are C; the handlers are a few bytes larger than stock (a call instead of inline code).
- Converted with conv.py (blocks removed from stock_residual_code.c, symbols renamed in the vector table, registered in sources.json, origin g2c-wave28): `opencfw_em9305_IRQHandler_` ArcTimer0 (0x305b1c), ArcTimer1 (0x305be0), PmlClock (0x305d84), ProtocolTimerOutCmp7 (0x305f74, 4 vectors), ProtocolTimerOutCmp0 (0x306050), ProtocolTimerOutCmp2 (0x30611c, FLAG inferred name), ProtocolTimerOutCmp3 (0x3061e4), ProtocolTimerSync (0x3062ac), RcCalib (0x3064fc), SWI7 (0x30660c, 6 vectors), SleepTimerFullVal (0x3066e8). Bodies written from the lowered asm; NOT harness-run (they are MMIO/aux-register handlers) so they are transcriptions, flagged as such in each file header.
- An interrupted tool call left Cmp3 half done (block removed and renamed, file missing); fixed by installing the file and registering it by hand. conv.py was not re-run for it.
- Still residual: the 6 `enter_s`-frame ISRs (SWI0, SWI1, QK_noPreemption, GPIO, PmlSvld, SleepTimerOutCmp3) and RadioRx/RadioTx (their bodies are 0x311ab4 RF_HandleInterrupt_Rx and 0x311c14).

### P3 step 12 (~5:05 AM America/Chicago): 0x311c14 harness-equivalent
- Discovery: IRQHandler_RadioTx (0x306440) is the shared frame with `bl.d L311c14` in the prologue's last delay slot, so 0x311c14 is the Tx body and 0x311ab4 (RF_HandleInterrupt_Rx, 350 B, still asm) is the Rx body. Name for 0x311c14: `RF_HandleInterrupt_Tx`, FLAG inferred from its sibling.
- Harness `.waves/w28/run_txirq.sh` (--mmio --nor0; pre `pre_txirq.h` sets the 0x8019d4 record with callbacks = the harness `pre_cb2` logger or null, and a RAM word standing in for aux 1686): EQUIVALENT on 60 tests, 53 outcome classes, 45 stub calls. QEMU has no aux registers 1666/1686 (`helper_sr` assertion), so for the run both sides had `sr 4,[1666]` -> no-op and `lr r0,[1686]` -> `ld` of a RAM word (orig by text substitution, cand by macro in a copy `cand/txirq_h.c`); the installed source uses the real `__builtin_arc_sr/lr`. Limits: the aux register values are not modelled beyond one random word, and 45 stub calls in 60 tests is modest coverage.
- Mutants, all killed: field compare 0x1fff->0x1ffe, bit 7 -> bit 6 test, fire(2)->fire(3), ack 16->17, pending clear removed, shift 8->9, callback clear removed, status bit 0x10->0x20 (8 of 8).
- Install is waiting for the em9305 w28j build (running since 4:53 AM) to finish so the tree is not changed mid-build.

### P3 step 13 (Wed Oct 28 2026, ~5:10 AM America/Chicago): w28j build of the 11 C ISR wrappers
- `g2/build/w28j`: 760/760 compiled with -Werror, 0 duplicate strong symbols, 0 undefined refs after link; abs audit ran; final link OK.
- Image 238,548 B (was 238,424 B in w28h; +124 B for 11 handlers, the cost of the `bl BODY` indirection). The 11 bodies are still NOT harness-run (transcribed from lowered asm).

### P3 step 14 (Wed Oct 28 2026, ~5:11 AM America/Chicago): 0x311c14 installed in C; RadioTx/RadioRx wrapped
- 0x311c14 `opencfw_em9305_RF_HandleInterrupt_Tx` (harness-equivalent, 8/8 mutants killed; 240 B vs 210 B stock, no `xbfu`) installed as `RF_HandleInterrupt_Tx.c`; removed from `stock_residual_code.c`.
- `IRQHandler_RadioTx.c` (frame + `bl RF_HandleInterrupt_Tx`) and `IRQHandler_RadioRx.c` (frame + `bl opencfw_em9305_stock_311ab4`, the body is still stock asm) replace the stock blocks 0x306440/0x306384; vector table renamed; chkref `bad 0`. Both differ from stock only in where the last aux save sits relative to the call (stock uses the delay slot).
- Rebuild `g2/build/w28k` started 5:11 AM; result not yet checked.

### P3 step 15 (Wed Oct 28 2026, ~5:18 AM America/Chicago): PCM2.2 sequences 11 and 13 verified; enter_s ISR wrapper prepared
- Sequences 11 (0x005A2EEA) and 13 (0x005A326C): side-by-side Ghidra decompile vs `producers.c` matches on order, fields, masks, the 0.9f factor (0x3f666666, unsigned convert rounding toward zero) and clamps. Rows added to `verified-w27.tsv`. Limit: the literal-pool values of the switch-helper register pointers were not printed (same helpers as sequences 9/18). With this, all 27 PCM2.2 sequences have rows (fixes the 25-of-27 note in step 8's correction). `coverage3.py` still reports weak 355 fns / 49,560 B (these two were not counted in the weak set by that script), residual 15 runs / 1,150 B.
- Prepared (not yet installed, build w28k is running): `.waves/w28/cand/irq/em_irq_frame_e.h` (second frame macro, `enter_s [r13,blink]` / `[r13-r15,blink]`, same save order as stock) and bodies for GPIO 0x305ca4, SleepTimerOutCmp3 0x3067b8, PmlSvld 0x305e68. They compile with -Wall -Wextra -Werror and the disassembly matches the stock sequence structurally; NOT harness-run. FLAGS: aux 1034 unnamed; PmlSvld's controller_timer_changed argument taken from timer_apply's return (guess), and the bit-6 timer-context read kept as a volatile read.
- SWI0 0x30251c, SWI1 0x3025f8 and QK_noPreemption 0x3025d0 are the QK preemption glue (they build a fake frame and `rtie` into QK_activate_), not a frame around a body; they stay asm.

### P3 step 16 (Wed Oct 28 2026, ~5:27 AM America/Chicago): w28k build OK; enter_s ISR wrappers installed
- `g2/build/w28k` (RadioTx/RadioRx wrappers + `RF_HandleInterrupt_Tx` in C): 763/763 compiled with -Werror, 0 duplicate strong symbols, 0 undefined refs at final link; image 238,584 B (w28j 238,548 B; stock 210,888 B).
- Installed `em_irq_frame_e.h` plus `IRQHandler_GPIO.c`, `IRQHandler_SleepTimerOutCmp3.c`, `IRQHandler_PmlSvld.c` (blocks removed from `stock_residual_code.c`, vector table renamed, registered in `sources.json`, chkref `bad 0`). Bodies are NOT harness-run (flags in step 15 and file headers).
- Rebuild `g2/build/w28l` started 5:26 AM; result not yet checked.
- All 19 `rtie` ISRs now have their frame as one shared macro and the body in C, except SWI0/SWI1/QK_noPreemption (kernel preemption glue, stay asm) and RF_HandleInterrupt_Rx 0x311ab4, which is a C wrapper around a body that is still asm (350 B).

### P3 step 17 (Wed Oct 28 2026, ~5:40 AM America/Chicago): w28l build OK (checkpoint)
- `g2/build/w28l`: 766/766 compiled with -Werror, 0 duplicate strong symbols, abs audit run, final link 0 undefined; image 238,640 B (w28k 238,584 B, w28j 238,548 B, w28h 238,424 B, stock 210,888 B). +216 B total vs w28h for 16 C ISR wrappers and `RF_HandleInterrupt_Tx` (240 B vs 210 B stock).
- Not harness-verified: the 14 ISR bodies other than 0x311c14 (transcriptions of lowered asm; flags in file headers). Still asm: SWI0, SWI1, QK_noPreemption, RF_HandleInterrupt_Rx 0x311ab4 (350 B body). Next: 0x311ab4 harness lift, then 0x30ecf8, 0x30f014, 0x333a94/0x333b48.

### P3 step 18 (Wed Oct 28 2026, ~5:50 AM America/Chicago): harness for the transcribed ISR bodies
- Method: `.waves/w28/isrh.py` lowers each stock handler and removes its frame (88-byte frame or `enter_s` frame, replaced by `push_s blink` ... `pop_s blink; j_s [blink]`) so the stock middle runs as a plain function; the candidate is the installed `IRQHandler_<Name>.c` (its `_body`, aux 1034 replaced by a RAM word at 0x801ff8 on both sides). Driver: `isrrun.sh NAME STARTHEX 'arity'`, mutants: `isrmut.sh`; hooks `pre_isr_common.h` (every callback slot 0x801900..0x80192f is 0 or the logging callback) plus `pre_isr_<Name>.x`. MMIO 0xf00000.. randomised and hashed. Not covered: the frame itself (save/restore order was checked by script earlier), `rtie`, real aux semantics.
- ArcTimer0 (0x305b1c): EQUIVALENT on 60 tests (47 outcome classes); mutants: slot 0x801904->0x801908 killed (callhash mismatch in 27 tests), unconditional call killed (hangs on null call).

### P3 step 19 (Wed Oct 28 2026, ~6:10 AM America/Chicago): 13 more ISR bodies run in the harness; 2 real bugs found and fixed
- Baseline (60 tests each, outcome classes / stub calls): EQUIVALENT for ArcTimer1 (46/45), PmlClock (26/39), ProtocolTimerOutCmp0 (36/60), Cmp2 (36/60), Cmp3 (36/60), ProtocolTimerSync (26/102), RcCalib (55/18), SleepTimerFullVal (49/49), GPIO (43/110), SleepTimerOutCmp3 (50/105), PmlSvld (17/96); this also confirms the PmlSvld guess that controller_timer_changed receives timer_apply's return, because the stub return values depend on the argument.
- MISMATCH (callhash, 43 and 44 of 60 tests) for ProtocolTimerOutCmp7 and SWI7: the stock code leaves the vector index in r0 at the callback call, so the callback receives it. Fixed in the installed files: Cmp7 calls `cb((uint8_t)(cause-0x15))`, SWI7 `cb(cause-0x38)` (unmasked, as stock). Both then EQUIVALENT on 60 tests. The earlier transcription (`cb()` with no argument) would have changed behaviour if the callback reads its argument.
- Mutant runs in `/tmp/isr_mut.log` (N=30); results in the next step. The installed headers still say "not harness-run" and need updating once all mutants are in.

### P3 step 20 (Wed Oct 28 2026, time not recorded, before 6:25 AM America/Chicago): 0x311ab4 RF_HandleInterrupt_Rx lifted to C (candidate; installed in step 21)
- `.waves/w28/cand/RF_HandleInterrupt_Rx.c`: five paths on status 0xf00860 (bits 25, 22, 16, 21), record at 0x8019c4 (same layout as the Tx record at 0x8019d4), callback codes 3, 4/7/8/10, 9, 5; measure uses aux 1666/1689 (FLAG: unchecked; Tx uses 1686/`sr 4`). Header documents each path.
- Harness (`rxrun.sh`, orig = lowered 0x311ab4..0x311c12; aux lr/sr substituted on both sides as for Tx, plus `mov_s r0,0` before the two stock `bl common_radio_restore` calls since that function ignores its argument and the stock r0 there is leftover junk): EQUIVALENT on 60 tests (44 outcome classes, 86 stub calls). Mutants in `/tmp/rx_mut.log`.

### P3 step 21 (Wed Oct 28 2026, 6:26 AM America/Chicago): mutant results; RF_HandleInterrupt_Rx installed; headers updated; w28m build started
- ISR mutants (`/tmp/isr_mut.log`, 30 mutants over the 14 bodies, N=30): 26 killed at once (memhash, callhash or ncalls mismatch). Four came back EQUIVALENT, which showed weak hooks, not equal code: PmlClock `status & 6 -> 7` (needed a status word covering all 16 low-bit patterns), GPIO `0xfff -> 0xffff` (pending word had to be shifted so the lowest bit can be >= 12), SleepTimerOutCmp3 `0xf -> 0x7` (the lr 1034 stand-in word had to be forced to 0x1f + 0..7). Hooks fixed (`pre_isr_PmlClock.x`, `pre_isr_GPIO.x`, `pre_isr_SleepTimerOutCmp3.x`); baselines still EQUIVALENT on 60 tests and the three mutants now die (ncalls, memhash, memhash).
- One mutant stays unobservable: PmlSvld `flags & 64 -> flags & 32`. The guarded statement is a dead volatile read of 0x80fde0 (the stock `ld` result is not used), so no harness can see it. Kept in C as a read for fidelity. The header says so.
- Rx mutants (`/tmp/rx_mut.log`, 11 mutants): all killed. The `? 4u : 10u` swap needed N=200 (killed in 4 of 200 tests, since it needs status bit 16 with ctl bit 6 set and bits 4/5 clear).
- Installed `g2/src/em9305/application/RF_HandleInterrupt_Rx.c` through `conv.py` (0x311ab4 block removed from `stock_residual_code.c`, `IRQHandler_RadioRx.c` now calls the C body, `chkref.py` bad 0). FLAG: aux 1666/1689 meanings are unchecked (harness substitutes lr/sr on both sides).
- The 14 ISR headers now say "harness-checked" with the method and the limits (frame, `rtie` and real aux semantics are not covered); SWI7 notes the index argument.
- Build `g2/build/w28m` started in the background (log `/tmp/w28m.log`).

### P3 step 22 (Wed Oct 28 2026, 6:47 AM America/Chicago): w28m checkpoint
- `g2/build/w28m`: 767/767 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object (ok, same as the composed pass before aliases); `.waves/abs/link.sh` + `audit.py`: undef refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link `g2/build/w28m-final-em9305` links with 0 undefined, image 238,708 B (w28l 238,640 B, +68 B for the C Rx handler; stock 210,888 B).
- The em9305-only change needs no paired sim. Remaining stock asm in `stock_residual_code.c`: SWI0 0x30251c, QK_noPreemption 0x3025d0, SWI1 0x3025f8 (QK preemption glue, stays asm), and the gaps 0x30ecf8, 0x30f014, 0x333a94/0x333b48.

### P3 step 23 (Wed Oct 28 2026, 7:43 AM America/Chicago): the three gaps lifted and harness-checked (not yet installed)
- Interrupted at 7:37 AM: stray mutant runs killed, candidate files restored from the `.good` copies. The Mac load average was about 200, so docker runs hit the 90 s timeout at N>=200 (a timeout is not a result; rerun at lower N).
- 0x30ecf8 (three functions): F1 `.waves/w28/cand/nvmgap1.c` (EQUIVALENT, 60 tests, 5/5 mutants killed), F2 `nvmgap2.c` (100 tests, 98 outcome classes, 11/11 mutants killed; the `sleep_rom_start(3)` mutant needed N=200 because the path needs the warm-boot branch), F3 `nvmgap3.c` (60 tests, 5 of 6 killed; the `0xf0041e = 14` mutant is unobservable because the final restore overwrites it). Combined file `cand/application_boot.c`, ROM facades added to `em9305_link_closure.c` (names are address-only).
- 0x30f014 (NVM write, called by emsmm_write_memory_305a20): `cand/nvmw.c`, EQUIVALENT on 60 tests with args clamped (bank 0..3, index < 0x4000, count < 32) and hooks that put the range at the 0x2000/0x20000 limits, 128-word and 2K-word boundaries. 0x30f170 in the same block is the vector filler (88-byte frame + system reset): becomes `EM_IRQ_HANDLER(opencfw_em9305_stock_30f170, em9305_rom_system_reset_103f14)`; the restore half is unreachable in stock too.
- 0x333a94 / 0x333b48: `cand/sbi.c` (transmitter test command: EQUIVALENT 100 tests) and `cand/sbv.c` (parameter check, modes 0/1/2: EQUIVALENT 150 tests). Mutants running (boundary hooks added because ret-only functions hide off-by-one mutants at random inputs).
- FLAGS: stale ROM arguments (boot_status/ready, packet_limit(1) = leftover validator result); roles of ROM 0x103180, 0x104ce4, 0x1030f8, 0x103c00, 0x1032b4, 0x103370 unknown; mode word at 0xf02800 unknown; int_vector_base aux 0x25 written by F2; bytes 9..11 and 17..19 of the 0x333a94 command record are uninitialised in stock and stay so.
- NOTE: the first nvmw runs used `--nor0` by mistake (ignores the return value); removed. Baseline and mutants must be rerun with return values compared before installing.

### P3 step 24 (Wed Oct 28 2026, 8:41 AM America/Chicago): gap 0x333a94 / 0x333b48 installed as `transmitter_test_params.c`
- Stray mutant runs killed at 8:27 AM, candidate files verified against their `.good` copies. Only this one gap was installed in this session (the smallest, 342 B).
- `0x333b48` (`opencfw_em9305_stock_333b48`, parameter check for the transmitter-test commands, modes 0/1/2): EQUIVALENT on 150 qemu-arc tests with boundary hooks; 24 of 24 mutants killed (off-by-one on every limit, mode tests, power sign handling).
- `0x333a94` (`opencfw_em9305_stock_333a94`, called by EMSRC_TransmitterTest): EQUIVALENT on 60-100 tests; 14 of 20 mutants killed (the `power <= limit` boundary needed a hook that makes the power equal the limit). Not run for lack of time: `0x7f -> 0x7e`, `cmd[8]`, `cmd[2]`, `cmd[0]`, the `params[0]/params[1]` argument swap, and `return r -> return 1` in the 305ab4 path. FLAGS: packet_limit_3047fc is called with the leftover validator result, written as 1; bytes 9..11 and 17..19 of the 20-byte command record stay uninitialised as in stock.
- Installed through `conv.py` (0x333a94 block removed from `stock_residual_code.c`, `stock_` names kept, file registered in `g2/src/sources.json`). `chkref.py` now also accepts C definitions of `opencfw_em9305_stock_*` symbols (a lifted block keeps its stock name); `bad 0`. The arc compile of the new file is clean with -Wall -Wextra -Werror.
- Build `g2/build/w28n` started at 8:40 AM (log `/tmp/w28n.log`, 13-20 min). Audit and final link still to do.
- Ready but NOT installed: `cand/application_boot.c` (0x30ecf8, F1-F3 all harness-equivalent, compiles) and `cand/application_nvm_write.c` (0x30f014 + the 0x30f170 vector filler, harness-equivalent with return values compared, 11 of 11 sampled mutants killed, compiles). `em9305_rom_page_103370` facade added to `em9305_link_closure.c`.

### Step 25 (Wed Oct 28 2026, 9:19 AM CDT): remaining 0x333a94 mutants, 0x30ecf8 + 0x30f014 installed, build w28o

- The 6 remaining 0x333a94 (sbi) mutants are all killed (`0x7fu->0x7eu`, `cmd[8]=2u->3u`, `cmd[2]=params[1]->params[2]`, `cmd[0]=0u->1u`, argument swap `params[0],params[1],params[4]`, `return r -> return 1u`). With the earlier ones, sbv/sbi mutants are 100% killed.
- Installed `application_boot.c` (0x30ecf8 hook/boot + 0x30ed80 + 0x30ee78 and the 0x30ef04/0x30ef0c wrappers) and `application_nvm_write.c` (0x30f014 plus the 0x30f170 vector filler) via conv.py. The remaining asm in `stock_residual_code.c` (NVM_ErasePage) called the local label `L30ee78`; now `bl.d opencfw_em9305_stock_30ee78`. chkref `bad 0`.
- Build w28o (-Os, fresh dir): 770/770 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object (as before). Audit: undefined refs 0, 350 in-range words, insn hits 4, data-word hits 2. Final link (g2-em9305): 0 undefined, image 238,888 B (w28m 238,708 B; stock 210,888 B).
- FLAGS (guesses): roles of ROM 0x103180, 0x104ce4, 0x1030f8, 0x103c00, 0x1032b4, 0x103370 unknown (address-only facade names); mode word 0xf02800 unknown; stale-register ROM args (boot_status/ready ignored; packet_limit_3047fc(1)); F2 writes aux 0x25; 0xf0041e=14 transient unobservable; sbi cmd record bytes 9..11, 17..19 uninitialised; C 0x30f170 saves aux 1409 before the reset call (stock saves it in the delay slot).
- w28n (superseded) was killed and removed.

### Step 26 (Wed Oct 28 2026, 10:39 AM CDT): ProtTimer_StoreConfig 0x310c08 (226 B) + ProtTimer_RestoreConfig 0x310aa8 (96 B) lifted to C

- New `application/ProtTimer_Config.c` (both functions, void; the state record at 0x80fd20 is addressed by literal as in stock: saved-config pointer at +0xc, timer index byte at +0x14). Registered once in sources.json.
- Harness (QEMU-ARC, `--mmio --nor0`, `run_ptc.sh`, hook `pre_ptc.h` with fixed saved-block pointer, idx set {0..5,16,17,31,32,33,255}, wake-marker path forced in 2/3 of tests, 0xf0047a/c..f preset): baseline EQUIVALENT on 60 tests for both. 14 mutants (`t<3->t<4`, `1u->0u`, `&0xf->&0x7`, 512->513, 2->3, `1<<17->1<<16`, `!=3->!=2`, `&2->&4`, loop 14->13, second+1, `|240->|224`, `0xf00480->0xf00484`, `&31->&15`, cleared 0->1): all killed in Restore and/or Store. One unobservable: `&0xf->&0x7` in StoreConfig (the bit it sets in 0xf0047a is cleared again at the end of the same call), still killed in RestoreConfig. The spin on bit 0 of 0xf0180c is not covered (the hook keeps the bit clear).
- Install: conv.py (two blocks, duplicate sources.json entry removed); chkref `bad 0`.
- Build w28p (-Os, fresh): 771/771 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit undefined refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link g2-em9305 0 undefined, image 238,940 B (w28o 238,888 B; stock 210,888 B).
- FLAGS (guesses): register meanings at 0xf018xx/0xf0047x/0xf0383b and the saved-block words 17..19 are address-only names; the four `nop`s after the wake-marker write are kept (delay purpose unknown); the state record at 0x80fd20 is not allocated by the linker (stock does the same).
- ini (0x30ef44 + 0x333c24 + 0x31435c) was a candidate at this point; installed in step 27.

### Step 27 (Wed Oct 28 2026, 12:25 PM CDT): NVM_InitCopy 0x30ef44 (206 B) + validate 0x333c24 (32 B) + _initdatCopy 0x31435c (20 B) lifted to C

- New `application/NVM_InitCopy.c` (`opencfw_em9305_stock_30ef44(record, ram_flag, full, high_flag)`, `_333c24(record)`, `_31435c(data, size, destination, &out)`), registered once in sources.json. New ROM facade `em9305_rom_1030dc(void)` in `em9305_link_closure.c` (address-only).
- Harness (QEMU-ARC, `--handlers --args7 --mmio`, `run_ini.sh`, hook `pre_ini.h`: 'INI' record with versions {0..5, random}, bad-signature cases, 1..5 entries from address pools, plus a boundary mode on odd tests with edge addresses around 0x801000, 0x80e978, 0x1ff000, 0x200000 and the ROM limit, `full`/`ram_flag` varied, `high_flag` forced 0): baseline EQUIVALENT on 64 tests (text 260 B orig and cand). The first orig hang was my own harness error (the orig extraction had dropped the last two instructions of the 0x31435c block).
- Mutants killed: skip window edges (0x801000->0x801004, 0x80e978->0x80e97c, 0x1ff000->0x1ff004, 0x200000->0x1ffffc), ram_flag and high_flag inverted, version <3->4 and >=4->5, entry start +4->+8 and +8->+12, advance size>=1->2 and (size+3)&~3 -> (size+2)&~3, memset size +1, signature 'N' check, full!=0 -> ==0, `addr==0` terminator (hang), `<0x801000 -> <0x800ffc`, limit +4, limit +2, `>=limit -> >limit`.
- Unobservable (flag): `*out = size+1` in `_31435c` (out word lives on the stack, which is not hashed).
- Install: conv.py (three blocks, duplicate sources.json entries removed); chkref `bad 0`; the three C/asm files compile with -Wall -Wextra -Werror.
- Build w28q (-Os, fresh): 772/772 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit undefined refs 0 (350 in-range words, insn hits 4, data-word hits 2); final link g2-em9305 0 undefined, image 238,944 B (w28p 238,940 B; stock 210,888 B).
- FLAGS (guesses): ROM 0x1030dc role unknown (named by address only; stock passes a stale r0 = version byte, no arguments modelled; the only caller passes full == 1 so that path is unreached); the weak `opencfw_em9305_image_end` test mirrors stock, reason unknown; the copy-callback signature (data, size, destination, &out) is inferred; the 0x1ff000..0x200000 branch only tested with high_flag == 0.

### Step 28 (Wed Oct 28 2026, 1:45 PM CDT): PML_Init 0x30f4b0 (184 B) lifted to C

- New `application/PML_Init.c` (`opencfw_em9305_stock_30f4b0(void)`, returns the ROM init result), registered once in sources.json. Standalone and harness-verified against the lowered stock asm; the earlier `opencfw_em9305_controller_init` candidate in `qpc-scheduler/controller_init.c` is a separate copy of the same logic and was left untouched. The stock table in `stock_residual_data.c` still references the symbol `opencfw_em9305_stock_30f4b0`, now the C function.
- Harness (QEMU-ARC, `--handlers --mmio`, `run_pml.sh`, hook `pre_pml.h`: config pointer 0x80fb8c into a random-filled RAM block, mode/flag bytes zero or non-zero, factor set {0,1,2,3,100,0x7fff,0x8000,0xffff,random}, small/random sum words, 0xf00404 random/all-ones/zero): baseline EQUIVALENT on 40 tests (text 212 B orig, 208 B C, 163 stub calls). 30 mutants (sum - instead of +, operand swap, `(int16_t)` factor, every store offset/value, flag/mode byte sources, mode test, +36 values, configure_mode arg, `xbfu` position 4, +37 destination, prepare_timer condition and its source byte, last ROM arg byte, timer_reset/finish_init args 0): 29 killed. The one equivalent mutant, `(uint8_t)(field & 1u)` for the xbfu result, confirms that `xbfu r0,r0,3` yields a single bit (bit 3 of 0xf00404).
- Install: conv.py (one block); chkref `bad 0`; PML_Init.c and stock_residual_code.c compile with -Wall -Wextra -Werror.
- Build w28r (-Os, fresh): 773/773 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,968 B (w28q 238,944 B; stock 210,888 B).
- FLAGS (guesses): `xbfu` kept as inline asm; the mpywhul product is the low 32 bits (settled model); 0xf00404, the parameter record at 0x80fb80 and the power-management record at 0x80fb8c are named by address only (no field names); the stale-register arguments to `timer_reset`/`finish_init` are modelled as the previous return values.

### Step 29 (Wed Oct 28 2026, 3:27 PM CDT): RF_InitHw 0x311d2c (138 B) + RF_TestModeStart 0x312430 (138 B) lifted to C

- New `application/RF_InitHw.c` (`void opencfw_em9305_stock_311d2c(uint32_t incoming)`) and `application/RF_TestModeStart.c` (`uint32_t opencfw_em9305_stock_312430(uint32_t mode)`), each registered once in sources.json. RF_Init (still asm) tail-branches to the first by symbol; `stock_residual_data.c` references it by symbol.
- RF_InitHw: waits for ROM boot-ready when the boot status has bits 0x300 and ready is 0, clears 0x805fe0 and 0xf04404, copies the (index, value) halfword pairs at the pointer in 0x80fd4c into 0xf04800 + ((index << 2) & 0x3fc), writes 0xf04079 = 0, 0xf04078 = 16, 0xf04080 = 1 then 2, and calls RF_IrqConfigure (still asm, 0x311db8). Harness (`run_ihw.sh`, `--handlers --mmio --nor0`, hook `pre_ihw.h`: pair counts {0,1,2,3,4,5,9,255,6,7,16,33}, pointer into RAM, 0xf03838 bits forced set): baseline EQUIVALENT on 40 tests (text 144 B orig, 140 B C). 22 mutants, 20 killed (status mask, status test polarity, wait mask by timeout, 0x805fe0/0xf04404 values, count test, pairs formula, index mask/shift, base, entry[1]->[0], 0xf04079/0xf04078 values, 0xf04080 2->3, call removal, ready arg, RW16->RW32, pointer address). Equivalent (flag): `ready(status) == 0` -> `!= 0` (affects only the 0xf03838 wait, which the hook always satisfies) and the first `0xf04080 = 1` -> 3 (transient, overwritten by the following 2).
- RF_TestModeStart: mode >= 8 returns 0; modes 0/1 write 0xf04040 = 272/0x6000, 0xf04044 = 0xffffffff, 0xf04050 = 16, 0xf040bc = 0x10000; modes 2..7 write 0xf040bc = {0, 0xffff, 0x5555, 0x3333, 0x0f0f, 0xff}, then 0xf04050 = 0, then set bit 16 of 0xf040bc; then call the transmit trigger (0x312390, C) and return 1. Harness (`run_tms.sh`, `--handlers --mmio`, hook `pre_tms.h`: modes 0..9, 255, 0xffffffff, 0x80000000, random): baseline EQUIVALENT on 40 tests (text 140 B orig, 138 B C, 22 stub calls). 19 of 19 compilable mutants killed (bound 7/9, <=1 split, every constant and pattern, `|= 0x10000`, trigger call removed, return 1->0); one mutant (`case 4:` -> `case 5:`) is a duplicate case and does not compile. Not mutated: order of the 0xf040bc / 0xf04050 writes (only the final memory hash is compared).
- Install: conv.py (two blocks); chkref `bad 0`; both new files and stock_residual_code.c compile with -Wall -Wextra -Werror.
- Build w28s (-Os, fresh): 775/775 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,972 B (w28r 238,968 B; stock 210,888 B).
- FLAGS (guesses): register meanings at 0xf04040/0xf04044/0xf04050/0xf040bc/0xf04078..0xf04080/0xf04404/0xf04800 and the table at 0x80fd4c/0x80fd50 are address-only names; `incoming` is the caller's untouched r0 (RF_Init reaches it with 0x3a); the 0xf03838 wait loop is untestable (hook sets both bits); stock RF_TestModeStart keeps blink in r3 across the trigger call and relies on 0x312390 not clobbering r3, the C version has no such dependence (orig harness variant pushes blink instead).

### Step 30 (Wed Oct 28 2026, 9:21 PM CDT): System_Save 0x313880 (130 B) + System_Restore 0x3137fc (130 B) lifted to C

- New `application/System_SaveRestore.c` (`void opencfw_em9305_stock_313880(void)`, `void opencfw_em9305_stock_3137fc(void)`), registered once in sources.json (conv.py ran twice into the same file; duplicate entry removed). `stock_residual_data.c` references both by symbol. The record pointer word at 0x80fd80 is re-read through a volatile access before every record access, as stock does.
- Save: record word 0x4c = (0xf03800 & 1); record offsets 4..0x2c = 0xf03804..0xf0382c (11 words); 0x30 = 0xf03830; 0x34 = 0xf03834; 0x44 = 0xf03844. Restore: passes record word 0x4c to the sleep ROM prepare routine (0x103ab4, `opencfw_em9305_sleep_rom_prepare`), then writes the same registers back (0xf03800 is not rewritten directly).
- Harness (QEMU-ARC, `--handlers --mmio --nor0`, `run_sys.sh` with `SYM=`, hook `pre_sys.h`: record pointer into random-filled RAM, and on every fourth test pointed so a record store overlaps the pointer word at 0x80fd80, offsets {0x4c, 4, 8, 0x2c, 0x30, 0x34, 0x44, 0}): both baselines EQUIVALENT on 40 tests (text 264 B orig for both functions, 184 B C). 24 mutants (12 per function: `& 1`, record offsets, loop bound 10/12, loop start, stride, source/destination register addresses for 0x30/0x34/0x44, prepare argument and call removal): 22 killed. Two equivalent, genuinely so: loop bound `i <= 12` in both functions (the extra iteration copies word 0xf03830 <-> record 0x30, which the next line writes identically).
- Install: chkref `bad 0`; `System_SaveRestore.c` and `stock_residual_code.c` compile with -Wall -Wextra -Werror.
- Build w28t (-Os, fresh): 776/776 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit 350 in-range words, insn hits 4, data-word hits 2; final link g2-em9305 `undef refs: 0`, image 238,892 B (w28s 238,972 B; stock 210,888 B).
- FLAGS (guesses): registers 0xf03800..0xf03844 and the record fields are address-only names; stock leaves the record pointer (Save) and record word 0x44 (Restore) in r0, treated as void; the record at 0x80fd80's target is not allocated by the linker (stock does the same); the aliasing of a record store onto the pointer word is exercised by the hook and matches stock.

### Step 31 (Wed Oct 28 2026, 11:42 PM CDT): AOAD_Init 0x30299c (126 B) + receiverTestCheckParameters 0x3335f4 (128 B) lifted to C

- New `application/AOAD_Init.c` (`void opencfw_em9305_stock_30299c(void)`) and `application/receiverTestCheckParameters.c` (`uint32_t opencfw_em9305_stock_3335f4(const uint8_t *p, uint32_t length, uint32_t mode)`), each registered once in sources.json. New address-only ROM facade `em9305_rom_102b00(index, value)` in `em9305_link_closure.c`. `AOAD_Init_veneer.c` (0x302a1c `b 0x30299c`), `EMSRC_ReceiverTest.c`, `EMSRC_EmCoreReceiverTest.c` and `stock_residual_data.c` already reference the symbols; unchanged.
- AOAD_Init: clears byte 0x8019f1; when the enable byte at 0x80fb60 is non-zero, copies words 0x80fb48/4c/50 to 0xf04c04/08/0c and, for each non-zero flag byte i (0..11) at 0x80fb54.., clears bit i in 0xf0340c/0xf03408/0xf03400, sets bit i in 0xf03404 and calls ROM 0x102b00(i, 0xd). Harness (`run_aoad.sh`, `--handlers --mmio --nor0`, `--rename 0x102b00=em9305_rom_102b00 --arity 2`, hook `pre_aoad.h`: enable byte {0,1,0xff,2}, flag bytes random zero/non-zero plus all-zero and all-one tests): baseline EQUIVALENT on 40 tests (text 128 B orig, 160 B C: the volatile read-modify-writes are larger than stock's). 27 mutants (enable test, enable/clear addresses, each copied word source/destination, loop bound 11/13, start index, flag base, flag test, each register address, set/clear polarity, bit index +1, ROM args): 27 killed.
- receiverTestCheckParameters: mode 0 needs length 6, p[0] < 0x28, p[1]-1 < 5; mode 1 needs length 7, the same, and p[6] < 2; mode 2 (length unchecked) needs p[0] < 0x28, p[1]-1 < 5, p[6] < 2, p[7] == 0 or 2..0x14, p[8] < 3, p[9]-1 < 2 and (uint8_t)(p[10]-76) > 181; other modes return 0. Harness (`run_rtc.sh`, `--handlers --mmio`, hook `pre_rtc.h`: 52 deterministic boundary tests, each field's edge values per mode, wrong lengths, invalid modes 3/0xffffffff/0x80000000, then random-valid tests): baseline EQUIVALENT on 56 tests (text 128 B orig and C). My first hook (random boundaries) left 17 of 27 mutants alive, so it was replaced by the table above. 29 mutants (every limit and constant, the p[7] special cases, the p[10] range, mode and length checks): 29 killed.
- Install: conv.py (two blocks); chkref `bad 0`; new files, `em9305_link_closure.c`, `stock_residual_code.c` and the three referencing files compile with -Wall -Wextra -Werror.
- Build w28u (-Os, fresh): 778/778 compiled, 0 duplicate strong symbols, 12 unresolved in the composed object; audit insn hits 4, data-word hits 2, in-range words checked 349 (was 350: the `ini_record_335820` word that held 0x335fd4 now holds 0x3365a8, i.e. an address that moved past the 0x336000 audit window because the image grew by 36 B; not a stale hard-coded address); final link g2-em9305 `undef refs: 0`, image 238,928 B (w28t 238,892 B; stock 210,888 B).
- FLAGS (guesses): ROM 0x102b00 role unknown (arguments (index, 0xd), named by address only); registers 0xf03400..0xf0340c, 0xf04c04..0xf04c0c and the record at 0x80fb48 are address-only names; stock leaves a stale r0 from AOAD_Init (treated as void); receiverTestCheckParameters field meanings (channel, PHY, etc.) are inferred from the HCI LE receiver-test layout and unverified; the callers seen (EMSRC_ReceiverTest, EMSRC_EmCoreReceiverTest) only pass modes 0 and 1, so the mode-2 branch (and the p[10] test) is verified by the harness only; length is ignored in mode 2 as in stock.

## 2026-10-29 — rescan, untagged upstreams, bootloader SYSPLL from upstream

- Rescan of all seven payloads against every local upstream/vendor tree:
  `g2/docs/reference/untagged-upstream-dependencies.md`. Main finding: the Even
  bootloader links the AmbiqSuite 5.1.0 HAL pinned for apollo-main but built
  none of it from source (64 functions, 16.8 KB mapped in
  `coverage-2.2.6.10/bootloader-ambiq-hal-map.tsv`). Second: 1,182 named
  EM9305 functions exist in open Cordio r20.05c (Apache-2.0) while about 810 are
  being lifted from lowered assembly. The EM SDK v4.6 Packetcraft headers are
  confidential/proprietary and are not used.
- Bootloader now builds `am_hal_syspll.c` from `third-party/upstream/ambiqhal-apollo510`
  (generated copy `ambiqhal-apollo510-boot/am_hal_syspll.c` compiles out
  `am_hal_syspll_mux_select`, absent from stock). New profile
  `g2-apollo-bootloader-6` (bootloader flags plus HAL includes). Removed hand
  copies `clock_pll_math.c`, `syspll_disable_4273dc.c` and the PLL generators in
  `clock_generators.c`. `clock_class_provider6.c` calls the HAL API. New
  `clock-manager/syspll_hal_bindings.c` holds the stock `am_hal_pwrctrl_syspll_*`
  and `am_hal_sysctrl_clkmuxrst_pll_fref_update` bodies until those upstream
  files are built here. `am_hal_delay_us{,_status_check}` are aliases of the
  existing stock implementations. The IAR libm helpers are now `floorf/roundf/ceilf/fmodf`.
- Verification: `g2/evidence/bootloader-syspll-upstream-review.json` — REA/Ghidra
  decompile of stock 0x42740c matches `am_hal_syspll_configure`; Unicorn
  differential of stock bytes against the new C, 3,036 cases (generators,
  configure incl. MMIO write order, enable/disable/deinitialize/lock_wait),
  0 mismatches; a one-operator mutant is caught (25/600).
- Build: `sources.py check` 5,221 units / 4,899 files; bootloader 381/381
  compiled, 0 duplicate strong symbols, 0 unresolved; final link OK, image
  157,636 B (was 157,364 B; stock 148,599 B). Other payloads not rebuilt.
- Hazard recorded, not fixed: bootloader `.bss` (`opencfw_boot_iom_contexts`,
  0x20000000..0x20004540) overlaps 89 hard-coded stock RAM cells.
- Next: `am_hal_queue.c`, `am_hal_cmdq.c`, `am_hal_clkgen.c`, `am_hal_mspi.c`
  (reuse apollo-main's control variant), then SPOTMGR, for the bootloader.

## 2026-10-29 — bootloader RAM layout follows the stock map

- Stock places the IOM contexts at 0x2001455c (literal 0x42cdb4 loaded by the
  claim at 0x42c4c6; 8 x 0x8a8 to 0x20018a9c) and `g_SysPLLState` at
  0x20027010 (literal 0x4275a4, `am_hal_syspll_initialize` 0x4272ac). Both lie in
  the stock zero record 0x2000055c..0x200271c8 that startup clears; stock
  initialized cells are 0x20000000..0x2000055c. UART (0x20024400) and ADC
  (0x20026df0) pools match literals 0x4233e4 and 0x42f150.
- `apollo-bootloader/link/g2-apollo-bootloader.ld` now pins those four objects
  at their stock addresses (with slot-size asserts), places generic
  `.data`/`.bss` in `DTCM_FREE` 0x200271c8..0x2007d000 (between stock zeroed
  cells and the stack limit), and asserts both are empty, because startup only
  runs the stock init records and never copies `.data` or clears `.bss`.
- Verification: fresh `sources.py build` of the bootloader: 381/381, 0
  duplicate strong symbols, 0 unresolved; `.waves/link-final.sh` links,
  image still 157,636 B. `build/check_bootloader_ram_overlap.py` (ignored
  build tree) compares every `0x20xxxxxx` literal in
  `g2/src/apollo-bootloader` (205 distinct) with the ELF's RAM symbols and
  writable sections: 0 overlaps after; 72 before (the old 0x20000000 placement).
  This resolves the hazard in
  `reference/untagged-upstream-dependencies.md`.

## 2026-10-29 — bootloader queue, PRIMASK, CMDQ and CLKGEN from upstream

- The bootloader now builds `am_hal_interrupt.c` and `am_hal_queue.c` verbatim,
  and generated copies of `am_hal_cmdq.c` (`am_hal_cmdq_pause` compiled out)
  and `am_hal_clkgen.c` (only the eight private leaves stock links), from the
  pinned AmbiqSuite 5.1.0 tree, all with profile `g2-apollo-bootloader-6`.
- Removed hand copies: `critical_save.S`, `irq_guard.S`,
  `critical_save_adapter.c` (23 callers renamed to
  `am_hal_interrupt_master_*`), the UART ring functions, the CMDQ bodies in
  `nor_mspi_queue.c`, `queue_descriptors.c/.h`, `resources.c`, two leaves of
  `control_request_helpers.c`, `clock_generators.c/.h`, and the CLKGEN statics
  (with their duplicates) in `clock_class_provider4/5.c` and
  `startup_clock_config.c`. The dead duplicate clock-gate body in
  `nor_mspi_queue.c` went with profile `g2-apollo-bootloader-5`.
- `gAmHalCmdq` is pinned at stock 0x200262f0 in the link script.
- Differential tests of stock bytes against the final linked image (Unicorn;
  PRIMASK and Armv8.1-M CSEL emulated): queue 500 sequences, CMDQ 800
  operation sequences with a CQ hardware model, CLKGEN 4,000 calls; 0
  mismatches; mutants caught. Record:
  `evidence/bootloader-hal-upstream-review.json`; the HAL map marks 36 rows
  Verified.
- Build: `sources.py check` 5,219 units; bootloader 379/379, 0 duplicate
  strong symbols, 0 unresolved; final link OK, image 157,380 B. Other
  payloads not rebuilt (no shared files changed).
- `thread-creation/*.ld` and `nor-mspi-queue/module.ld` are old per-module
  link scripts no build uses; they still name removed symbols.
- Next: `am_hal_mspi.c`. It needs the clock-manager and power-control
  bindings first; see `reference/untagged-upstream-dependencies.md` §1.

## 2026-10-29 — bootloader is AmbiqSuite SDK 5.0.0; MSPI from upstream

- The bootloader HAL is SDK 5.0.0 RTM (ambiqhal_ambiq `392042e`), not 5.1.0:
  stock `am_hal_mspi_device_configure` has the 5.0.0 `bNewDDR` branch, stock
  `am_hal_mspi_control` uses the 5.0.0 request enum (the "stock variant"), and
  the image lacks the aperture table added by the post-RTM fix `9df2220`.
  5.0.0 is pinned as `third-party/upstream/ambiqhal-apollo510-sdk5.0.0`
  (shallow submodule; staged with `.gitmodules`). Profile
  `g2-apollo-bootloader-6` now uses it, plus `-fno-vectorize
  -fno-slp-vectorize` (clang otherwise emits MVE loops; stock has none).
- `am_hal_mspi.c` builds verbatim from 5.0.0, control included. Removed the
  hand split of control (`nor-mspi-init/control_*.c/.h`), `fifo_transfer.c`,
  `blocking_transfer.c`, `nor-mspi-power/device_configure`, `power_control*`,
  `mspi_clockgen_control.c`, `nor-mspi-queue/`, `mspi/`, the MSPI glue in
  `glue/`, the MSPI leaves of `hal_leaves.c` and `am_hal_mspi_initialize` in
  `nor_mspi_init.c`. NOR-driver callers now use the `am_hal_mspi_*` names.
  `g_MSPIState` is pinned at stock 0x2001caa0. The hand clock-manager and
  power-domain functions carry upstream-name aliases for it.
- Differential (Unicorn, final linked image vs stock, callees stubbed equally):
  MSPI 1,500 operation sequences over all 13 public functions, 0 mismatches;
  two mutants caught (244/400, 381/400). Queue, CMDQ and CLKGEN re-run on the
  5.0.0 image: 0 mismatches. Record: `evidence/bootloader-hal-upstream-review.json`.
- Build: `sources.py check` 5,197 units; bootloader 357/357, 0 duplicate
  strong symbols, 0 unresolved; final link OK, image 158,108 B.
- apollo-main's MSPI "stock variant" control also uses the 5.0.0 enum; see
  `reference/untagged-upstream-dependencies.md` §1.

## 2026-10-29 — bootloader status helpers and UART from upstream

- `am_hal_delay_us_status_change/check` (0x41d21c/0x41d246) build from a
  generated 5.0.0 `am_hal_utils.c` that keeps only those two; 17 callers
  renamed, `status_poll.c` and `runtime_wait_adapter.c` removed. Stock
  `am_hal_delay_us` calls the boot-ROM loop at 0x41 rather than the SDK's ITCM
  loop, so it stays hand code. Differential: 3,000 cases, 0 mismatches.
- The UART HAL is the 5.1.0 `am_hal_uart.c` (stock state layout is 5.1.0, not
  RTM), built verbatim from the 5.1.0 pin against the 5.0.0 headers.
  `g_am_hal_uart_states` is pinned at 0x20024400. Removed the hand UART HAL
  (`uart_rx.c/.h`, `uart_irq_dispatch.c`, `uart_irq_status.c`,
  `uart_context.h`, most of `uart_context.c` and `elog_uart_tx.c`,
  `glue/post_configure_alias.c`, the guard in `runtime.c`); Even's IRQ row
  wrapper and log send stay. Differential: 400 sequences, 0 mismatches
  (baud 0 excluded: undefined in the upstream C).
- So the bootloader HAL is a snapshot between 5.0.0 RTM and 5.1.0; choose the
  revision per file by test.
- Build: bootloader 353/353, 0 unresolved, image 157,300 B; `sources.py
  check` 5,193 units.
- Next: the power core, `am_hal_pwrctrl.c` + `am_hal_spotmgr*.c` +
  `am_hal_clkmgr.c`. SPOTMGR alone needs about 55 globals pinned at stock
  addresses and stock init records for 140 B of `.data`.

## 2026-10-29 — bootloader PWRCTRL from upstream; harness IT-state fix

- The stock PWRCTRL block 0x41b8f8..0x41cae8 is SDK 5.0.0 `am_hal_pwrctrl.c`
  in source order with unlinked functions dropped (25 functions). It now builds
  verbatim. Its state is pinned at the stock cells: `g_ui32TrimVer`
  0x20000098, `g_DefaultMcuMemCfg` 0x2000009c, `g_eCurMcuPwrMode` 0x20000552
  (initialized record, which already holds the SDK initializers),
  `g_sINFO1regs` 0x200267f8, five trim snapshots 0x2002704c..0x2002705c, the
  GPU/ROM mode bytes and `g_bOrigTrimsStored` 0x200271a5..0x200271a8, and
  `g_ui8TRCENAcount` 0x200271a3. Clang drops eleven write-only static trim
  snapshots that stock stores at 0x20027060..0x2002708c; nothing reads them.
- Stock `am_hal_pwrctrl_temp_update` takes its float in `s0` (hard-float HAL,
  softfp bootloader). A generated `am_hal_pwrctrl.h` gives it
  `pcs("aapcs-vfp")` and profile -6 searches that copy first.
- Removed 22 hand files (the PWRCTRL halves of `platform-control/`, the
  register-carry startup root, memory-config and TON-gate leaves, query table,
  power guards, GPU mode) and the PWRCTRL functions in eight more. The SPOT
  dispatcher wrappers, INFO1 read, debug trace release and clock-mux reset
  keep their hand bodies under upstream alias names until their files move.
- Linker pins now assert with `ABSOLUTE(.)`. Inside an output section `.` is
  section-relative, so the earlier `. <= limit` checks could never fail.
- Harness defect: a Unicorn memory-write hook that fires inside a Thumb IT
  block leaves IT state set, so later instructions are skipped as if
  conditional. MMIO now uses `mmio_map` callbacks, the PRIMASK/CSEL emulation
  hooks only those instructions, and every module was re-run on the new image:
  queue 500, PRIMASK 4, CMDQ 800, CLKGEN 4,000, MSPI 1,500 (10M budget), status
  polls 3,000, UART 400, PWRCTRL 1,500, all 0 mismatches. PWRCTRL mutants
  caught 37, 43 and 11 of 400.
- Build: bootloader 338/338, 0 unresolved, image 157,012 B; `sources.py
  check` 5,178 units.
- apollo-main's PWRCTRL has the same function sizes and its "older-revision"
  variants describe the 5.0.0 text, so its PWRCTRL and SPOTMGR hand variants
  are 5.0.0 too (see untagged-upstream-dependencies.md).

## 2026-10-29 — bootloader CPDLP duplicates, no MVE, SPOTMGR revision

- `thread-creation/idle_sleep/sleep_helpers.c` held second copies of stock
  0x41c9ca/0x41ca0c (`am_hal_pwrctrl_pwrmodctl_cpdlp_config/get`) and the SPOT
  autoswitch wrappers 0x41ce26/0x41ce3c. The sleep code now calls the upstream
  PWRCTRL functions and the wrappers' upstream names; the file is gone.
- Bootloader hand profiles -1/-3/-4 add `-fno-vectorize -fno-slp-vectorize`
  (as -6 already did): clang had emitted 475 Helium/MVE instructions
  (`dlstp`/`letp` copy loops and others) that the stock image does not
  contain. Image 154,652 B.
- The differential harness now also emulates MRS/MSR for BASEPRI, WFI/WFE,
  Armv8.1-M DLS/WLS/LE, and enables VFP, so whole-image paths (startup init
  records, float SPOT code) run.
- SPOTMGR was swapped to upstream, tested, and reverted: the stock SPOTMGR is
  an unpublished Ambiq revision between `66185cb` and 5.1.0 (see
  untagged-upstream-dependencies.md). The hand SPOTMGR stays; the tested swap
  is in `build/snap-stage2/` and `build/boot-hal-diff/diff_spotmgr.py` is
  ready for the per-context work.
- Harness: VFP is now enabled and VSEL emulated. Before that, both sides
  faulted on their first VFP instruction and the PWRCTRL run counted the
  matching faults as agreement, so `temp_update` was not really tested. Faults
  are now counted separately; the remaining ones are NULL-argument calls that
  fault at address 0 on both sides.
- Final image re-run: queue 500, PRIMASK 4, CMDQ 800, CLKGEN 4,000, MSPI 1,500,
  status polls 3,000, UART 400, PWRCTRL 1,500, all 0 mismatches; PWRCTRL
  mutants caught 39, 58 and 20 of 400. Build 337/337, 0 unresolved,
  154,652 B; `sources.py check` 5,177 units.
- SYSPLL re-verified on the final image (harness ported to the IT-safe base,
  VSEL emulated): 3,036 cases, 0 mismatches, 0 faults.

## 2026-10-30 — apollo-main PWRCTRL from upstream SDK 5.0.0

- apollo-main's PWRCTRL block (0x47ef18..0x4800e4) is the same SDK 5.0.0
  `am_hal_pwrctrl.c` as the bootloader's: equal function sizes in source
  order and the same callee at every one of its call sites. It now builds
  verbatim (profile `g2-apollo-main-108`: 5.0.0 headers, no vectorizer, no
  global merge). Retired: `hal/x-03-pwrctrl/`, `hal/final-r1-pwrctrl/`,
  `drivers/power/power-vendor/`, `runtime/info-memory/memory.c/.h`,
  `ble/ble-flash/display_ble_flash_mode.c`, `system/glue/memory_config_aliases.c`,
  the generated 5.1.0 copy with its 27 replacements, and the duplicate
  `audio_ble_flash_mode` cell (it is `g_eCurROMPwrMode`). Callers keep their
  names through compose aliases.
- Test: the manifest object linked standalone with its globals at the stock
  cells and its callees at the stock addresses, run against the stock OTA
  image (`build/main-pwr/diff_main_pwrctrl.py`): 1,500 cases, 0 mismatches;
  mutants caught 4, 34 and 4 of 400.
- Harness: the PRIMASK trace was shared across a case's steps, and GFX/CRYPTO
  paths were rarely hit; both fixed in the bootloader harness too, which
  re-ran at 1,500 cases, 0 mismatches.
- All apollo-main profiles now use `-mcpu=cortex-m55+nomve`. Stock main has
  no Helium/MVE instructions, but clang lowered memcpy and struct copies to
  MVE (155 `dlstp`/`letp` loops, about 1,000 `vldr*`/`vstr*` across 258
  objects); the vectorizer flags alone did not change that. The composed
  object now has none.
- apollo-main 2,863/2,863 compiled, 0 duplicates, the same 24 unresolved
  names; `sources.py check` 5,170 units.

## 2026-10-30 — apollo-main MSPI from upstream SDK 5.0.0 RTM

- apollo-main's MSPI (0x4bfa10..0x4c2af6) is instruction-for-instruction the
  bootloader's verified SDK 5.0.0 RTM MSPI, plus three functions the
  bootloader does not link. It now builds the 5.0.0 file unchanged (profile
  `g2-apollo-main-108`). Retired: the 12-file hand split of
  `am_hal_mspi_control` under `drivers/flash/mspi/` and the generated 5.1.0
  copy with its 12 replacements; `g2_norflash_config_transfer_4c0f78` is now a
  compose alias of `am_hal_mspi_control`.
- Callers already used the stock (RTM) 24-byte device config and request
  numbers, so the implementation now matches them; the 5.1.0 copy did not.
- Test (`build/main-pwr/diff_main_mspi.py`, standalone link against the stock
  OTA image, stock CMDQ running natively): 1,500 cases, 0 mismatches; mutants
  caught 381, 139 and 13 of 400.
- apollo-main 2,851/2,851 compiled, 0 duplicates, the same 24 unresolved;
  `sources.py check` 5,158 units.

## 2026-10-30 — bootloader SPOTMGR from upstream

- Project goal clarified by the user: a working firmware, not stock identity.
  Newer upstream text is preferred where it does not change how the hardware
  is driven.
- The bootloader builds `am_hal_spotmgr*.c` from SDK 5.0.0 + AmbiqSuite patch
  `66185cb`. On top of that it takes the 5.1.0 hunks stock also has: three in
  PCM2.0, the HFRC2 force in PCM2.2 `SWITCH_TO_HP`, and the PCM2.1 deep-sleep
  override without the TIMER A test. The 78 hand SPOTMGR files are removed;
  the RAM pins and transition-table copy are those from the earlier attempt.
- The earlier "per-sequence" divergence was largely a harness error (`r0`
  compared after void sequences); the real differences were the two hunks
  above.
- Verification: standalone overlay (`build/spot-sa/`) with 27 x 30 direct
  sequence calls, 0 mismatches, and 1,500 cases, 0 mismatches; mutants caught
  53 and 12 of 400. On the linked image (155,064 B) the full suite matches:
  SPOTMGR 1,500, PWRCTRL 1,500, MSPI 1,500, CLKGEN 4,000, CMDQ 800, queue 500,
  UART 400, status polls 3,000, SYSPLL, all 0 mismatches.
- Build: 299/299; the three compose-unresolved names are the transition-table
  linker symbols the final link defines.
- Correction (later the same day): apollo-main SPOTMGR is the same text as
  the bootloader's, and it now builds the same upstream source (see the next
  section).

## 2026-10-30 — remaining assembly to C, case image linked, duplicates removed

Policy as above: a working firmware, not stock identity. Assembly stays only
where the architecture needs it. Scratch work and harnesses for each step are
under `build/` (the directory named in each step).

- **EM9305 lowered units.** All lowered-assembly units under
  `em9305/qpc-scheduler/initializer_lowers/` are now C, along with
  `application/stock_residual_code.c` and `stock_residual_data.c`.
  - Each unit is proven against its stock copy under QEMU-ARC
    (`.waves/qrun.py`, 100 random cases, with a mutant check for branchy
    code).
  - Results: `build/em-lift/results-slice*.tsv` and `results-big-{A,B}.tsv`.
    `311e04` is a partial proof (log2p0/fssub).
  - The four QK context-switch entries stay in assembly
    (`application/qk_port_swi.c`).
  - Fixed while doing this: `__divdi3` (the lowered copy had lost a
    `leave_s`); `32b82c` and `32db0c` each had two copies and now have one.
- **EM9305 `controller_init.c` and inline assembly.** The 10 top-level
  assembly functions and about 230 pinned arithmetic statements are now C;
  hardware statements use `__builtin_arc_*`.
  - 192 changed functions are EQUIVALENT in QEMU, and every mutant is caught.
    Results: `build/em-ctl/results-*.tsv`; harness `build/em-ctl/qm.py`.
  - Bugs fixed:
    - `ll_slot_apply_308708` read r2 after a call had clobbered it;
    - `config_link_has_remainder` read Z without setting it.
  - Still assembly:
    - ILINK accesses (no builtin exists);
    - the calibrated `lp_count` delay;
    - the APEX `bswp8`/`log2p0` instructions.
- **EM9305 profile.** `g2-em9305-1` now adds
  `-mdiv-rem -mbarrel-shifter -mswap -mnorm -mmpy-option=wlh1`, the core
  options listed in `findings-codec-em9305.md`.
  - C division now uses hardware `div`/`rem`; `__divsi3`, `__udivsi3`,
    `__modsi3` and `__umodsi3` are gone from the unresolved list (13 → 9).
  - Stock and our startup both set STATUS32.DZ, so a zero divisor raises
    EV_DivZero and the unused-vector handler resets the chip. The C therefore
    has no zero-divisor guards.
  - Re-proved under the new flags: 192/192, and 39 of 47 sampled slice units.
- **apollo-main naked functions.** 34 functions are now C, including veneers
  turned into typed aliases.
  - Bugs fixed: the `APP_StartServiceDiscovery` log argument; ANCS app IDs of
    62 characters or more now send nothing, where they used to overflow.
- **ARM inline assembly (bootloader, apollo-main, case).**
  - 88 halt loops are now `for (;;) {}`.
  - SDIV/UDIV, VFP arithmetic, converts and compares are C with ARM edge
    semantics: divide by zero gives 0, INT_MIN/−1 gives INT_MIN, VCVT
    saturates, and multiply-adds are not fused.
  - LDREX/STREX use builtins.
  - 26 Unicorn differential tests (`build/arm-pin/pindiff.py`) show 0
    mismatches, and each catches its mutant.
  - Fixed while doing this: LLVM turned `-(a/b)` into `(-a)/b`, which changed
    the sign of NaN results; the `*_neg` helpers are now `noinline`.
- **Codec (C-SKY).**
  - Stage-1 CRT initialisers and the residual `.S` files are now C. The IRQ
    entries use `__attribute__((isr))`, which produces the stock entry.
  - Stage-1 clock helpers rebuilt from stock: rail A/B/C, PLL config and
    module clock rate. Bugs fixed in the rate helper, which had put a wrong
    value in 0xa0400024:
    - DMA was mapped to the wrong clock (SCPU);
    - the 1M/12M case returned 0;
    - the DTO mask was not 25-bit;
    - a missing divider field returned 0.
  - Stage-1 data now lives in named objects in `.stage1.data` at 0x20002004.
    Stage-1 read-only data stays in STAGE1, not XIP flash.
  - Divide, shift and DSP pins are C (`codec/csky_ops.h`). Proven in XuanTie
    QEMU: shifts 810 cases, divides 420, DSP ops about 400k, and the
    inverse-RFFT split 12,700 outputs, all identical.
  - Still assembly: the reset/exception entries, `frecips`, and system-control
    registers.
- **Case firmware linked for the first time.**
  `case/link/g2-case.ld` places `.data`/`.bss` above 0x20002c88, because the
  case C reaches all of its stock RAM state (0x20000000..0x20002c88) by
  absolute address.
  - A 20-byte record at 0x080000b8 gives `case_crt_init_0270` the copy and
    zero ranges.
  - `.waves/link-final.sh` gained a `g2-case` branch.
  - Unicorn boot test (`build/case-link/boot.py`) against `firmware_box.raw.bin`
    on four paths, all identical to stock in peripheral writes and console
    text:
    - reset to first task switch (4,009 writes);
    - about 6 s of tasks (6,570 writes);
    - no devices attached;
    - first-boot option-byte programming.
  - 11 bugs fixed that had stopped it booting. The main ones:
    - RCC_CR `|= 0x1000` written where stock sets FLASH_ACR prefetch;
    - an oscillator-setup loop that never exited;
    - ADC calibration always skipped;
    - six strings one byte early;
    - six log calls missing an argument.
  - Duplicates: 81 stock functions had several implementations; 93 names
    became aliases and 39 units were removed. Where copies differed, the one
    matching stock was kept, which removes:
    - a hang in queue-send-from-ISR;
    - a 3-word timer command where the queue copies 4;
    - a busy-bus read that returned 0.
  - Software-bus timing now matches stock: PMIC/fuel-gauge about 225 kHz;
    2510/4005 single-wire pulses within 1–2 cycles. Measured with
    `build/case-link/timing.py` at 64 MHz with 2 wait states.
  - The unused stock compiler-runtime helpers (Thumb jump-table dispatcher,
    64-bit udivmod) were removed.
  - Image: 60,168 B (stock 55,752 B).
- **Duplicate stock functions in apollo-main and the bootloader**
  (`build/dedup-main/`). An inventory maps every linked function to its stock
  entry, and every candidate pair was reviewed against stock.
  - apollo-main: 198 duplicate bodies removed. The libc cores are shared, WSF
    and SMP now use the Cordio originals, and LVGL callers use upstream names.
    The kept copies now match stock: memcpy/memset return the destination, and
    the 0x43d0ce log gate and log line 306 are corrected.
  - Bootloader: 10 duplicate bodies removed (STIMER/PRIMASK copies, 0x415fae
    printf, 0x417b7c, 0x41d90e, the 0x41560c fill). 82 emptied units removed.
- **Build (`build/final-1030`).** Every payload compiles fully with 0
  duplicate strong symbols:

  | Payload | Units | Unresolved |
  |---|---|---|
  | bootloader | 226 | 3 |
  | apollo-main | 2,771 | 24 |
  | case | 366 | 0 |
  | codec-a | 347 | 0 |
  | codec-b | 332 | 0 |
  | em9305 | 772 | 9 |
  | touch | 101 | 12 |

  - All seven final links (`build/final-1030-link/`) have 0 undefined
    references.
  - `sources.py check`: 4,920 units.
  - Bootloader HAL diffs show 0 mismatches: spotmgr 400, pwrctrl 1,500,
    syspll, utils 3,000, clkgen 4,000, cmdq 600, queue 500, uart 400 and
    mspi 400.
- **Not run on hardware.** These remain unverified:
  - The proofs model the EM9305 APEX/DSP instructions (`mpywhl`, ASLACC) and
    the C-SKY `mulaca` saturation corner rather than running them on silicon.
  - Case clock/PLL, low-power modes, UART receive, OTA flash programming, the
    real tolerance of the 2510/4005 protocol, and the 6% shorter device
    timeouts.
- **Known stale:** `g2/evidence/case-semantic-strings.json` still lists the six
  string addresses that were one byte early.
- **Staged entries:** some codec and EM9305 application files appear in the git
  index. No worker in this pass ran git commands; the index was left as found.

## 2026-10-30 — apollo-main SPOTMGR from upstream; runtime helpers from libgcc

- **SPOTMGR.** Stock apollo-main SPOTMGR is the bootloader's text: SDK 5.0.0,
  patch `66185cb` and the same five 5.1.0 hunks.
  - apollo-main builds the bootloader's generated
    `{gen}/ambiqhal-apollo510-boot/am_hal_spotmgr*.c` with profile `-108`.
    40 hand units are removed, as are 50 compose aliases and the SPOTMGR RAM
    cells.
  - Scored against stock over 300 cases:
    - bootloader text: 0 mismatches;
    - plain `66185cb`: 50;
    - 5.1.0, `48793d7` and 5.2.0: 237 each. They change init register writes,
      simobuck waits and INFO1 reads, so they were rejected.
  - Test: `build/dedup2/spot/diff_main_spotmgr.py`, 1,500 cases, 0
    mismatches. Mutants caught: 3, 28 and 14 of 400. The weakest is the
    rarely reached PCM2.1 TIMER A path.
  - Bugs fixed: the sleep path read override flags and INFO1 from a RAM copy
    nothing wrote.
- **LVGL and ring duplicates moved to upstream:**
  - `_450672` → `lv_anim_path_ease_out`; the ease_in and ease_in_out copies
    too (204k cases);
  - the hand image cache and font LRU → `lv_image_cache`/`lv_cache_lru_rb`
    (20,000 cases); the hand vtables lacked `iter_create_cb`;
  - `audio_uart_lv_free` → `lv_free`;
  - `codec_ring_initialize` → `ring_buffer_init`.
- **Compiler runtime.**
  - `__aeabi_uldivmod` and `__aeabi_ldivmod` now come from libgcc
    (`thumb/v8-m.main+dp/hard`), because only compiler-generated calls used
    them. As a result apollo-main lists 26 unresolved names before the final
    link, where it had 24; the final link resolves them.
  - Removed because nothing called them: the IAR `cdrcmple`/`dcmpgt`/`cdcmple`
    helpers and the bootloader's `double_compare_flags.S`.
  - Test: 6,970 Unicorn edge cases, 0 mismatches. Two differences remain:
    - divide by zero returns all-ones where stock returned the numerator;
      `drv_buzzer.c` has a guard for its one reachable case;
    - NaNs with a zero upper mantissa now compare unordered, as the ABI
      requires.
- **Assembly that remains, all needed by the architecture:**
  - reset entries;
  - exception, context-switch and PendSV entries (FreeRTOS `portasm.c`,
    bootloader `exception_entry.S`/`first_task_transfer.S`, case
    PendSV/context switch, EM9305 `qk_port_swi.c`, codec
    exception/reset);
  - the bootloader handoff to the application;
  - setjmp/longjmp;
  - CmBacktrace's HardFault entry;
  - EM9305 ILINK accesses, the `lp_count` delay and the APEX `bswp8`/`log2p0`;
  - the case single-wire delay counters;
  - the codec `frecips`;
  - the bootloader's fixed-address ITCM helpers and init-record data;
  - single-instruction system intrinsics (CPSID/MSR/MRS/DSB/ISB/WFI, `mfcr`/
    `mtcr`, `kflag`/`sr`).

  Every lowered-assembly unit, naked function and pinned arithmetic statement
  in the reconstruction is now C.
- **Final build** (`build/final2-1030` and `build/final3-main`): every unit
  compiles, with 0 duplicate strong symbols.

  | Payload | Units | Unresolved | Image (B) |
  |---|---|---|---|
  | bootloader | 225 | 3 | 154,224 |
  | apollo-main | 2,717 | 26 | 3,827,387 |
  | case | 366 | 0 | 60,168 |
  | codec-a | 347 | 0 | 2,155,932 |
  | codec-b | 332 | 0 | 81,600 |
  | em9305 | 772 | 9 | 246,768 |
  | touch | 101 | 12 | 28,784 |

  - All seven links have 0 undefined references; images are in
    `build/final2-1030-link/`.
  - `sources.py check`: 4,865 units.
  - `system/glue/i2s_power_aliases.c` `#include`d a retired SPOTMGR file, so it
    was removed too.
- **Needs hardware:** boot, deep sleep and wake, HP/LP switching and GPU
  power under the upstream SPOTMGR on the device's PCM revision; the buzzer
  at frequency 0.

## 2026-10-31 — simulator findings: uncopied initialised data, EM9305 ROM cells, EM9305 stubs

**apollo-main `.data` (fixed).**
- 0x14aa4 bytes of writable named sections (`.g2_locale_data_*`, `.g2_conversate_*_2xxxxxxx`, `.g2_bss_*`, `.g2_pdm_clock_pin_words`) were orphans placed after `__data_end`, so the region-table copy row never loaded them.
- The jimrandomh Renode emulator read the lv_i18n locale tables as 0.
- Fix: `g2-apollo-main.ld` `.data` now collects `INPUT_SECTION_FLAGS (SHF_WRITE) *(.g2_*)`. After the fix the sim reads the ELF initial values; code addresses do not change.
- Evidence: `g2/docs/sim-test-report.md` (2026-10-31).

**EM9305 ROM-owned cells (fixed).**
- `g2_em_qf_next_priority` was `= 16u` in `.sdata` at 0x80fe20, and `g2_em_app_start_callback` was in `.sbss` at 0x80fe24. No EM9305 startup code copies or clears those sections, so on silicon both would hold garbage.
- Stock uses 0x8012bc (read and decremented at 0x30ead6/0x3140ec) and 0x8010a4 (`ld r12,[0x8010a4]` at 0x30ec6c). It never writes either, and the package's four records are NVM-only, so the ROM owns them.
- Both are now NOLOAD pins at the stock addresses (`g2-em9305.ld`, `em9305_link_closure.c`). The externs carry the section so ARC GCC addresses them absolutely, not gp-relative.
- Build: 772/772 compiled; the final link has 0 undefined.

**Correction to the 2026-10-30 entries: the EM9305 image still has empty stubs for eight stock routines** in `em9305_link_closure.c`: `BSP_Init` (0x302e80), `irq_set_user_callback_3069b8`, `wsf_os_init_only_veneer_30460c` (stock `b 0x314068`), `wsf_os_register_start_304610` (stock `bl 0x3140a8; bl 0x3140d0`, WSF active-object ctor/start), `lhciCmdVsExtInterfaceEM`, `wsfOsRunIdleTasks`, `application_startup_hook_30482c` and `volt_monitor_measure_zero_3119a8`. The image compiles and links, but it is not functionally complete, and it must not go to hardware until these have stock bodies.

**EM9305 stubs replaced (same day).**
- New unit `qpc-scheduler/wsf_os_ao.c` implements the WSF OS active object ("WsfOs"):
  - WsfOsInitOnly 0x314068: clears the context at 0x805ff4 (0x7c B), then `QActive_ctor(0x80139c, initial)`.
  - The init-callback store 0x3140a8 (RAM 0x8019e4).
  - WsfOsStartOnly 0x3140d0: assertion 653, priority from 0x8012bc, queue 0x80faac ×16.
  - The initial pseudo-state 0x333db8.
  - The dispatch state 0x333c44: entry runs the init callback; signal 8 services queued messages, expired timers and the 16 per-handler event half-words, using the existing `opencfw_em9305_wsf_*` helpers.
  - `wsfOsRunIdleTasks` 0x333d7c.
  - The two veneers 0x30460c and 0x304610; 0x304610 registers `opencfw_em9305_controller_initialize_stack` 0x302a20.
- `em9305_link_closure.c` now carries the stock bodies of:
  - `BSP_Init` (stores 3 to 0xf00a78, then sync);
  - `irq_set_user_callback_3069b8` (RAM 0x80190c);
  - `lhciCmdVsExtInterfaceEM` 0x32e5a8 (allocate, copy, send at header−2, callback set, return 1);
  - `application_startup_hook_30482c` (`pal_metadata_register(0x8012e4)`);
  - `volt_monitor_measure_zero_3119a8` (`timer_enable(0)` at 0x313ae4).
- Build: 773/773 compiled under -Werror; the final link has 0 undefined; `make sources-check` passes.
- Verification: each body was reviewed instruction by instruction against the corpus disassembly. It is **not** emulator-checked, because no stock-lowered reference unit exists for these routines.
- Still open: about 127 stock call targets in 0x302400..0x3340bc are not named in any EM9305 source (heuristic scan). Each needs to be classified as dead, renamed, or missing.

**apollo-main bond records (fixed, 2026-10-31).** The Cordio app_db bond page (10×256 B at mapped MRAM 0x7ff000) was linked into SSRAM .bss because its `.ld` fragment was never included. The sim OTA round trip showed the retained phone key rejected (HCI 0x06). It is now pinned in `g2-apollo-main.ld` beside the OTA flag page. Evidence: `g2/docs/sim-test-report.md`.

**apollo-main file-API mutex (fixed, 2026-10-31).** Stock RAM 0x200748f4 was split into `g2_codec_redirect_mutex` (created by redirect_init 0x474d9c) and `audio_file_api_mutex` (locked by file_open/read/write/close, never set). Every file-API open therefore failed, including the OTA receiver's filesystem health probe, so OTA START returned status 10. The fix makes them one object (an alias). Evidence: `g2/docs/sim-test-report.md`.

## 2026-11-10 — fresh all-payload compile and strict source linkage

**Codec image-A AOUT SRAM placement (2026-11-10).** The source linker now
places the 52-byte AOUT context at `0x10026b94`, the 84-byte dispatch table at
`0x10026bc8`, and the 88-byte hardware configuration at `0x10026c1c`, with
link-time size assertions. They occupy the stock gap before the UART receive
configuration. The strict seven-payload source link passes without an external
archive; image-A SRAM falls from 14,940 to the locked 14,716 bytes. The hardware
configuration matches stock exactly, while relocation-bearing context and
dispatch words differ. At this placement snapshot, the exception and IRQ
vector targets also differed. Image-A XIP
remains 10,280 bytes over its locked limit. Evidence:
`g2/evidence/codec-a-aout-sram-placement-20261110.json`.

**Codec image-A startup and exception placement (2026-11-10).** The reset,
BSS clear, system initializer, C trap handler, and architectural trap entry
now link at their stock SRAM addresses. The exception vector target at
`0x10023640` is the trap's branch back to its entry, as in the locked image.
The first 32 vector words match stock byte for byte. Reset matches 38/40
bytes; its call to `main` still differs because the source-linked function
is at a different address. The trap matches 75/80 bytes; the assembler
reuses a literal that stock duplicates. The IRQ vector still targets
`0x10025810` rather than `0x10025574`. The final full source gate compiled
4,877/4,877 enabled units without failures or duplicate strong symbols,
and all seven payloads linked strictly. Evidence:
`g2/evidence/codec-a-exception-vector-placement-20261110.json`.

**Codec image-A trap entry converted to C (2026-11-10).** Replaced the
standalone `resident_exception_entry.S` manifest unit with a naked C function
that retains the necessary C-SKY register-save and trap-stack instructions.
The source-linked codec A flat binary, SRAM, XIP, and BINH stage-1 outputs are
byte for byte unchanged. The final all-payload source gate compiled 4,877
enabled units and linked seven payloads without an external archive. Six
build-enabled assembler units remain in the G2 manifest. Evidence:
`g2/evidence/codec-a-trap-c-conversion-20261110.json`.

**Bootloader transitions converted to C (2026-11-10).** Replaced the vector
handoff and first-task transfer assembler units with naked C functions that
retain their required Thumb instructions. The handoff conversion preserves
the full bootloader binary. The first-task `.text` body remains byte-identical
at 32 bytes, while the compiler adds unwind coverage that changes one
`.ARM.exidx` byte in the linked bootloader. The final full G2 gate compiles
4,877 enabled units and strictly links all seven payloads. Four enabled
assembler units remain. Evidence:
`g2/evidence/boot-transfer-c-conversion-20261110.json`.

**All build-enabled G2 translation units now compile as C (2026-11-10).**
Converted the bootloader reset and stack entry, its fixed 24-byte ITCM helper
image, the SVC/first-task/PendSV exception entries, and Apollo-main's
CmBacktrace HardFault entry from standalone assembler units to naked C
functions with explicit architecture instructions. The reset/stack and ITCM
code bytes, the three exception bodies, and the HardFault body match their
prior linked forms. The manifest has 4,877 build-enabled `.c` units and no
build-enabled `.S` units; one upstream touch `.S` unit remains disabled and
unlinked. `sources-check`, the 4,877-unit full build, and the strict seven
payload links pass with zero compilation failures or duplicate strong symbols.
This is a C compilation milestone, not source completeness, byte identity,
or hardware qualification. Evidence:
`g2/evidence/g2-c-entry-source-gate-20261110.json`.

**Codec image-A vectors fully placed (2026-11-10).** The source linker now
pins the compact IRQ entry at `0x10025574` after pre-IRQ resident functions
and their source-owned literal data. All 64 vector words match the locked
firmware byte for byte. The 14,716-byte source SRAM image still fits the
locked span and its matching byte count rises from 2,655 to 2,857; most code
and data remain different. The XIP image is still 10,280 bytes over its
locked limit, and NPU command/weight source and full BINH A packaging remain
unresolved. The source linker now rejects a changed SRAM length or vector
hash. The strict seven-payload source link passes without an external
archive. Evidence: `g2/evidence/codec-a-full-vector-placement-20261110.json`.

- `./g2/make.sh sources-check`: 4,867 registered units, 4,527 source files,
  one documented not-built link helper.
- `tools/build/sources.py build --device g2 --out build/g2-current-20261110`:
  all 4,862 build-enabled units compiled, zero failed and zero duplicate strong
  symbols. The seven relocatable link groups composed. Full receipt:
  `build/g2-current-20261110/report.json` (SHA-256
  `deb032fb83f0d61c68a6fa26ac16d450ddc1fba6be584e700c83c72e3aa186ae`).
- Added `tools/build/link_g2_sources.py` and `make -C g2 source-link`. The
  linker checks that the compiled inputs have not changed, fails on link
  errors, and writes ELF and binary hashes. Six payloads link without an
  external binary archive: `build/g2-source-only-six-20261110/link-report.json`
  (SHA-256 `2d5e46c4c89343a513d20e6e491a4800d0f00d987167fde6b0ddf293040b92de`).
- Apollo main still imports Nordic `nrf_fuel_gauge` from an untracked `.a`.
  The default strict all-payload link therefore fails at this dependency.
  With the explicit `--allow-binary-fuel-gauge` baseline flag, all seven
  link with zero undefined references. Receipt:
  `build/g2-source-images-with-nordic-20261110/link-report.json` (SHA-256
  `9c099355ad6b46632a86c6bf457818685c5da46dc237a78c707159410b96652a`).
  Its seven binaries are byte-for-byte identical to the prior ad hoc final-link
  outputs made from this same build. A compact durable summary is in
  `g2/evidence/g2-source-link-20261110.json`.
- This is compilation and linkage evidence only. Ten manifest units are
  assembly; inline architecture instructions remain in C, source coverage
  is not frozen, and the physical Apollo-main boot failure remains unresolved.
  No new image was installed or marked hardware-ready.
- The freshly linked Apollo-main binary ran for 2 virtual seconds in the
  existing lenient Renode profile and emitted 56 HCI host packets, including
  advertising enable `010A200101`. The simulator has known gaps in real
  peripheral responses and timing; this result does not resolve the hardware
  boot failure. Log hash and run parameters are in the durable evidence record.

## 2026-11-10 — bootloader init-record table moved from assembly to C

- Replaced `startup/init_records.S` with read-only C descriptors in
  `startup/record_dispatch.c`. The dispatcher calls the same zero and expand
  adapters with the four stock descriptors in their original order. The table
  resides in ROM, so it is available before writable memory is initialized.
- `sources-check` passes: 4,866 registered units. The bootloader-only build
  compiled 224/224 units, composed without duplicate strong symbols, and
  linked a final ELF with zero undefined symbols.
- A Unicorn comparison of the old and new linked dispatcher functions
  captured identical adapter call kinds and descriptor words for all four
  records. The adapter bodies were intercepted, so this comparison does not
  itself verify downstream memory writes. Unicorn cannot run the M55 `LE`
  instruction in the zero adapter; a full memory comparison was not claimed.
  In Renode, both linked bootloaders ran for 2 virtual seconds through the
  same application and emitted an identical sequence of 56 HCI host packets,
  including advertising enable. These are simulator fixtures, not a physical
  boot proof. Evidence:
  `g2/evidence/boot-init-records-c-review-20261110.json`.
- The removed file was data-only assembly. Architecture entry and context
  assembly remain; this change does not establish an all-C bootloader.
