# G2 Apollo peripheral-register cluster attribution audit

Status: fail-closed attribution triage of the census's peripheral-register frontier
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The [unanchored-function provenance census](g2-apollo-unanchored-census.md)
flags 30 no-evidence functions with hardware hints: 22 whose decompiled text
contains tokens in the `0x40000000` peripheral range ("Ambiq HAL/driver
candidates") and 8 with SRAM-range tokens only.  The census hint is a raw
hex-token match; it cannot tell a peripheral address from a float or bitmask
constant.  This audit re-derives the register evidence from the authenticated
image, the 64-shard Ghidra corpus, and the vendored AmbiqSuite Apollo510
5.1.0 register headers on every run:

- **9 of the 22 register-hint functions have validated register evidence** —
  69 register references resolved to named Apollo510 registers.
- **1 is an SRAM-indirect register-write candidate** (`0x0052262E`): a
  bit-30 constant staged in a local and stored through a pointer held in
  SRAM; the runtime register target is not statically recoverable.
- **2 have call-topology evidence only** (`0x004C2AE8`, `0x005202EC`): no
  register reference of their own, but each calls a cluster function with
  register evidence.
- **10 hints are constant collisions**: the `0x4xxxxxxx` tokens are float or
  bitmask constants that fail register-map validation.  This includes the
  census's largest named start point, `0x005202EC` (8,374 bytes — an
  8 KB floating-point routine whose `0x40000000` tokens are comparisons
  against `±0x40000000`, not addresses).
- **All 8 SRAM-only functions** likewise show no validated SRAM *address*
  reference: their `0x20000000` tokens are bit/region-tag constants
  (for example `(param & 0x60000000) == 0x20000000` region checks), not
  SRAM-global accesses.

Attribution of the 22 register-hint functions (triage, not ownership):

| Family | Functions | Envelope bytes | Official bytes | Confidence |
|---|---:|---:|---:|---|
| AmbiqSuite HAL | 6 | 7,478 | 6,604 | 3 medium, 3 low |
| G2 board-support first-party | 3 | 1,044 | 976 | 3 low |
| investigation required | 13 | 12,454 | 12,414 | 3 low, 10 none |

## Method

Evidence channels, all re-derived per run; anything that fails validation
against the register map is discarded.

1. **Machine-code constants.** Each function's body bytes from the
   authenticated image are swept at every even offset for Thumb-2
   `LDR`-literal encodings (16-bit `0x4800` class; 32-bit `0xF85F`/`0xF8DF`
   classes with Rt ≠ PC) and for `MOVW`/`MOVT` synthesis pairs.  Literal
   pool targets are dereferenced against the image.  A flat sweep cannot be
   desynchronized by inline literal pools (the 8 KB function has them);
   false encodings are filtered by the register map.
2. **Decompiled-text evidence.** The authenticated corpus text is scanned
   for absolute-address dereferences (`*(type *)(... 0xADDR ...)`), for
   `DAT_xxxxxxxx` cell references whose image content validates as a
   peripheral base (one-hop chase), and for instance-strided register
   expressions (`DAT_cell + module * 0x1000 + 0xOFF`) on those cells.
3. **Call topology.** Closed-world callers/callees from corpus tokens,
   exactly like the census; anchored callers are labelled with their
   retained source path.

The register map is rebuilt from the vendored closure
(`third_party/ambiqsuite-apollo510/`, PROVENANCE.json): 49 peripheral bases
and 30 `_Type` struct layouts from `CMSIS/AmbiqMicro/Include/apollo510.h`,
the five INFO/OTP-INFO windows from `regs/am_reg_base_addresses.h`, and the
`SYNC_READ` barrier address (`0x47FF0000`) from `hal/am_hal_sysctrl.h`.  All
three headers are SHA-256 pinned; the parsed map is locked by structural
constants and reviewed register offsets (`MSPI0.INTSTAT == 0x204`,
`MSPI0.INTCLR == 0x208` are independently static-asserted by the MSPI
source-boundary audit's compile proof).  A candidate address is accepted
only when 4-byte-aligned and inside a block below its parsed struct size,
inside an INFO/OTP window, or equal to `SYNC_READ`.

The MSPI attribution is anchored by the reviewed
[MSPI interrupt-clear source-boundary audit](ambiqsuite-mspi-interrupt-clear-source-boundary-audit.md):
its private cells — MSPI base `0x40060000` at `0x004C26DC`, handle magic
`0x01BEBEBE` at `0x004C2ADC` — and the proven `am_hal_mspi_interrupt_clear`
span `[0x004C23DE,0x004C240E)` are re-validated from the image and corpus on
every run.

## Per-function register map and attribution (22 register-hint functions)

### AmbiqSuite HAL

| Entry | Bytes (env/off) | Validated register references | Conf |
|---|---:|---|---|
| `0x004C0F78` | 4,384 / 4,384 | MSPI: CTRL, MSPICFG, DEV0CFG, DEV0DDR, DEV0CFG1, DEV0XIP, DEV0SCRAMBLING, DEV0XIPMISC, DEV0XIPCPURQ, DMABCOUNT, CQSETCLEAR | medium |
| `0x004C099C` | 1,154 / 1,154 | MSPI: CTRL, DEV0CFG, DEV0CFG1 | medium |
| `0x004C240E` | 712 / 712 | MSPI: CTRL, DMACFG, DMASTAT, INTSTAT | medium |
| `0x0047FAE8` | 810 / 0 | MCUCTRL CHIPREV/VREFGEN2/VREFGEN4/LDOREG1/LDOREG2/D2ASPARE/SHADOWVALID/WICCONTROL/DBGCTRL/SIMOBUCK2/4/6/7/12/14/PWRSW0/PWRSW1/AUDADCPWRDLY, PWRCTRL VRSTATUS/MRAMEXTCTRL, CLKGEN MISC/CLKCTRL, STIMER+0x05C | medium |
| `0x0048009E` | 64 / 0 | MCUCTRL CHIPREV, D2ASPARE, PLLCTL0 | low |
| `0x004D3DDA` | 354 / 354 | INFO1, OTP_INFO0, OTP_INFO1 bases; MCUCTRL SHADOWVALID; PWRCTRL DEVPWRSTATUS | low |

The MSPI triplet (`0x004C099C`, `0x004C0F78`, `0x004C240E`) occupies the
same link-order region as the proven `am_hal_mspi_interrupt_clear` leaf
(`0x004C23DE`–`0x004C240E`), shares its private literal cells (MSPI base
`0x40060000`, handle magic `0x01BEBEBE`), validates the Ambiq handle prefix
(`*handle & 0x1FFFFFF == 0x01BEBEBE`, module at handle `+4`, base computed
as `0x40060000 + module * 0x1000`), returns Ambiq status codes, and is
called by the anchored first-party MSPI consumers `driver\flash\drv_mx25u25643g.c`
and `driver\uled\drv_mspi_uled_common.c`.  `0x004C0F78` — the census's named
start point — is a 41-case control dispatcher over device-config/XIP/DMA/CQ
registers, the structural shape of `am_hal_mspi_control`.  Confidence is
medium: distinctive structural evidence, but no byte/source match was
performed; the vendored closure contains the full `am_hal_mspi.c`, so a
bounded source-boundary audit per leaf is the natural follow-up.

`0x0047FAE8` writes the SIMOBUCK/LDOREG/VREFGEN/PWRSW voltage-sequencer
register set with `VRSTATUS` polling — the Ambiq power-on/ton-config
signature (domains: `am_hal_pwrctrl`, `am_hal_spotmgr`,
`am_hal_sysctrl_ton_config`; only the headers are vendored, the
implementation `.c` is not in the closure, hence medium not high).
`0x0048009E` is a 64-byte MCUCTRL PLL/chip-revision helper called by
`0x0044B158`.  `0x004D3DDA` reads OTP-INFO/INFO1 trim words with
`SHADOWVALID`/`DEVPWRSTATUS` status checks (am_hal infoc/mram-trim domain);
its only caller is the unanchored `0x004D3F3C`.

### G2 board-support first-party (candidates)

| Entry | Bytes (env/off) | Validated register references | Conf |
|---|---:|---|---|
| `0x0044B158` | 922 / 922 | CLKGEN CLOCKENSTAT/MISC, STIMER HALSTATES/+0x05C, MCUCTRL+0x0C0/PLLCTL0/PLLMUXCTL, USB CLKCTRL, PDM0 CTRL, I2S0/I2S1 CLKCFG, AUDADC CFG, SYNC_READ barrier | low |
| `0x004801FC` | 68 / 0 | TIMER INTEN/INTCLR, CTRL15, TMR15CMP0, TMR15CMP1, MODE15 | low |
| `0x0051381A` | 54 / 54 | OTP_INFOC base (decompiled deref only) | low |

`0x0044B158` sweeps clock-configuration registers across the audio/USB
peripherals with `SYNC_READ` barriers — a cross-domain pattern consistent
with board clock-tree configuration; an Ambiq clock-manager origin is not
excludable.  `0x004801FC` loads absolute TIMER15 addresses; a generic
`am_hal_timer` translation unit computes bases from a runtime instance, so
baked-in timer-15 literals indicate board-specific code (callers are
census-first-party `0x5Axxxx` functions).  `0x0051381A` reads the customer
OTP_INFOC window via a modified-immediate address and is called by the
anchored first-party `platform\service\flashDB\NV\service_nvdb_sys_dt.c`.

### Investigation required

| Entry | Bytes (env/off) | Evidence | Note |
|---|---:|---|---|
| `0x0052262E` | 32 / 32 | sram-indirect-register-candidate (low) | stages `0x40000000` in a local, stores it through `*DAT_00522F18` (SRAM pointer `0x20074EFC`); runtime register target unknown; called by census-first-party/LVGL functions and `0x005202EC` |
| `0x004C2AE8` | 72 / 72 | call-topology-into-cluster (low) | calls `0x0047FAE8` (power sequencer) and `0x004C2B30`; its `0x41C80000` token is the float `25.0f` argument |
| `0x005202EC` | 8,374 / 8,374 | call-topology-into-cluster (low) | no register reference; calls `0x0052262E`; `0x40000000` tokens are comparisons in float code |
| `0x0043A1B0` | 1,006 / 1,006 | no-register-evidence | float constant writes (`0x40000000` = 2.0f) |
| `0x0043C0E4` | 8 / 8 | no-register-evidence | byte-fill (memset-family) routine |
| `0x0043C0EC` | 94 / 94 | no-register-evidence | byte-fill (memset-family) routine |
| `0x004C3750` | 42 / 42 | no-register-evidence | popcount (`0x55555555`/`0x33333333` masks) |
| `0x004CA78A` | 40 / 0 | no-register-evidence | bitfield extract/insert helper |
| `0x00515304` | 722 / 722 | no-register-evidence | SRAM struct initializer (stores `0x40800000` = 4.0f) |
| `0x00528DB8` | 96 / 96 | no-register-evidence | float/bit-math helper |
| `0x0059BAE4` | 1,666 / 1,666 | no-register-evidence | float math (`0x41200000` = 10.0f) |
| `0x0059C7AC` | 84 / 84 | no-register-evidence | CLZ/bit-manipulation helper |
| `0x005FA13C` | 218 / 218 | no-register-evidence | float constant collision (`0x40800000` = 4.0f) |

### SRAM-globals-only secondary listing (8 functions)

`0x004408D6`, `0x00440968`, `0x00440DDA`, `0x00472C84`, `0x0052DC98`,
`0x0052DCDE`, `0x005392D4`, `0x00539994` (1,120 envelope / 932 official
bytes).  None yields a validated SRAM *address* reference under the same
channels; the `0x20000000` tokens are bit/region-tag constants.  They stay
`investigation-required` with evidence `sram-globals-only-listing`.

## Reconciliation with the census frontier

- The analyzer re-derives the frontier from
  `tools/manifests/g2-apollo-unanchored-census-functions.tsv` and pins it:
  exactly the 22 register-hint entries and the 8 SRAM-only entries above,
  all still in the census's `investigation-required-no-evidence` bucket.
  The 30-function hardware-hint total matches the census prose
  ("thirty no-evidence functions carry hardware hints").
- Wording discrepancy noted: the census doc says "11 reference SRAM globals
  only", but the census manifest has 11 SRAM-referencing rows of which 3
  also carry the register hint (`0x0043C0E4`, `0x0043C0EC`, `0x0044B158`),
  leaving **8** SRAM-only.  This audit pins the machine-readable manifest
  (22 + 8 = 30); the doc sentence should read "11 reference SRAM globals,
  8 of them SRAM-only".
- Byte totals: 22 register-hint functions carry 20,976 envelope / 19,994
  official bytes; families split them 7,478/6,604 (AmbiqSuite HAL),
  1,044/976 (board support), 12,454/12,414 (investigation required).
- The run used the local-replay corpus whose `SHA256SUMS` hashes to
  `87d0befa…c6404e` (accepted alongside the primary Lorelei hash by the
  path-census authenticator); the image is the authenticated
  `36c5b0e4…78a27863` payload.

## Reproduction

```sh
python3 tools/analyze_g2_peripheral_register_cluster.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-peripheral-register-cluster-map.tsv` — all 30 rows:
  per-function validated registers (block, offset, CMSIS register name,
  evidence kind), callers with labels, family, evidence, confidence, detail.
- `tools/manifests/g2-peripheral-register-cluster-summary.json` — input
  hashes, reconciliation counters, family totals.

The fail-closed guard is
[`../../tests/test_analyze_g2_peripheral_register_cluster.py`](../../tests/test_analyze_g2_peripheral_register_cluster.py):
21 tests covering register-map totality and mutation rejection, the
LDR/MOVW-MOVT decoders, census-manifest mutation rejection, the exact
attribution pins, family byte totals, and byte-for-byte manifest
regeneration.

## Limitations

- Attribution is provider-family triage, not source ownership; `low`
  confidence labels are queue-ordering hypotheses.  Only the MSPI triplet
  and the power sequencer carry distinctive structural evidence (medium).
- The constant sweep is a flat even-offset scan with map validation;
  `MOVW`/`MOVT` pairing is heuristic.  Both are fail-closed (rejected
  candidates are dropped, never guessed), but a register reference formed
  purely from modified-immediate `ADD`/`MOV` chains without a pool entry is
  only visible through the decompiled-text channel (`0x0051381A` is the
  example in this cluster).
- Register offsets beyond a block's parsed CMSIS struct size are rejected;
  accesses to undocumented/reserved offsets (e.g. STIMER `+0x05C`,
  MCUCTRL `+0x0C0`) resolve to the block but not to a register name.
- `0x0052262E`'s runtime register base lives in SRAM and is not statically
  recoverable from the image; its bit-30 write target is unknown.
- The MSPI medium-confidence attributions would become high only through a
  per-leaf source-boundary audit against the vendored `am_hal_mspi.c`,
  matching the standard set by the interrupt-clear audit.
