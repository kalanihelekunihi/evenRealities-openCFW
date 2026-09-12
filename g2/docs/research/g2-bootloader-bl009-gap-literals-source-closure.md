# G2 bootloader BL-009 gap-literal source closure (partial)

Status: 14 in-place data groups landed, 334 bytes production-routed;
remainder triaged below. No hardware operation. Hardware qualification
stays blocked by unavailable physical evidence.

## Scope

BL-009 assigns 25 disjoint `official_blob` spans totalling 5,978 bytes in
`0x0042B9BA..0x00430470` (flash-plan of 2026-09-11, re-confirmed
2026-09-12: all 25 still `official_blob`). The prior census
(`g2-bootloader-gap-census-42b9ba-430470.md`) classified 7 spans as real
Thumb code, 16 as data, 2 as zero-fill alignment.

This pass routes every span cell that satisfies all three of:

1. the value is an identified scalar (exact integer, float, peripheral
   address, clock, bitmask, sentinel, or zero alignment);
2. at least one original Thumb literal load (`ldr`/`ldr.w`/`vldr`,
   found by sync-proof byte-pattern scan of the whole stock image)
   consumes the cell from an already source-routed neighbour; and
3. the value is not a pointer into still-opaque code (BL-005/BL-011/
   BL-012 ranges or other retained spans).

Cells failing (3) stay retained even when understood: a reconstructed
pointer table into opaque code would move ledger bytes without reducing
opaque functionality, which the source-only goal explicitly excludes.
Cells failing (1)/(2) (unattributed SRAM addresses, unreferenced words)
stay retained as unattributed.

## Routed (322 bytes, 14 groups)

All payloads compile with the component toolchain pins
(`arm-none-eabi`, `-mcpu=cortex-m55 -mthumb -Oz -ffreestanding
-fno-builtin -ffunction-sections -fdata-sections ... -Werror`) and
reproduce the stock bytes exactly; the component build additionally
enforces per-placement `stock_sha256` and `expected` pins.

| Group (symbol suffix) | Span cells routed | Bytes | Key values / consumers |
| --- | --- | ---: | --- |
| `gap_42bf4e` | `0x42BF4E..0x42BF54` all | 6 | pad + SCB->CCR `0xE000ED14`; orig `ldr.w` at `0x42B4D4` polls CCR bit 17 (IC) in routed SPOT-mgr transition code |
| `gap_42c6e4` | `0x42C6E4..0x42C6F8` all | 20 | zero head; reg-block base `0x40050000` (indexed field loads, e.g. orig `0x42C034`); read-path words `0x08000001/2` (orig `0x42C098/0x42C0A2` select); sentinel `0xDEADBEEF` (orig `0x42C0E6`) |
| `gap_42c980` | `0x42C980..0x42C988` all | 8 | `0x05B8D800` = 96 MHz dividend (orig `0x42C278` `udiv`), `0x0003D090` = 250 000 (orig `0x42C39A/0x42C3AA`); routed clock successor embeds 96000000/250000 |
| `gap_42d0f2` | `0x42D0F2..0x42D104` all | 18 | pad + 35.0f (`vldr` `0x42CEE0`), -273.0f, 50.0f, 1000.0f (orig `0x42CF7C/0x42CFAA/0x42CFCE`) |
| `gap_42e50e` | `0x42E50E..0x42E514` all | 6 | pad + fallback dispatch address `0x08000140` returned in r0 by orig `0x42E4B2/0x42E504` on dispatcher slow paths |
| `gap_42e534` | `0x42E534..0x42E53C` all | 8 | MMIO store targets `0x40000008` (mode 0 stores `0xD4`, orig `0x42E522`) / `0x40000004` (mode 1 stores `0x1B`, orig `0x42E52A`) |
| `gap_42e8c8` | `0x42E8C8..0x42E8D0` | 8 | MMIO stores `0x40014008` (`str 0xC3`, orig `0x42E8B0`) / `0x40014024` (`str 0`, orig `0x42E8B8`); span head (pad + `0x00433120` indirect-call pointer into BL-012) stays retained |
| `gap_42edf6` | pad + `0x42EDFC` | 6 | pad + 290.0f (`vldr` `0x42ECCC`); middle word `0xC2F6E979` unreferenced here, stays retained |
| `gap_42f014` | `0x42F014..0x42F018` | 4 | -1000.0f (`vldr` `0x42EE3C`); 4096.0f/1190.0f words unreferenced, stay retained |
| `gap_42cdb0` | `0x42CDB0..0x42CDB4`, `0x42CDB8..0x42CDD4`, `0x42CDD8..0x42CDE0` | 40 | masked-ID compare `0x01123456` (orig `0x42C548`, BIC+CMP); revision OR `0x00123456` (orig `0x42C51C`); config store `0x00800040` (orig `0x42C592`); reg-block base `0x40050000` x2; field mask `0xFFFFFBFE` (orig `0x42C800` RMW AND); range bound `0x02DC6C01` (orig `0x42CC9C`); divisors 1 000 000 / 100 000 / 400 000 (orig `0x42CCCE` `udiv`, `0x42CD4C`); SRAM base `0x2001455C`, bound `0x20080000`, and three `0x2301`-tagged records stay retained |
| `gap_42bfa4` | 6 runs, `0x42BFAC..0x42C030` minus holes | 96 | bitmask/config words, 6 peripheral addresses, floats -273/-20/-22/50/48/1000; pool head `0xC2200000`, BL-012 pointer `0x00434164`, 10 SRAM addresses stay retained; live reader is partly the retained `0x42BA00` function (data reuse, no functionality claimed) |
| `gap_42f14e` | 8 runs, `0x42F14E..0x42F1C8` minus 7 SRAM cells | 94 | pad, pack `0x1F01600D`, floats 299.5/1.02809/-0.004281, cfg `0x4002010C`, masked-ID compare `0x01AFAFAF` (orig `0x42EA42`, BIC+CMP), `0x40038000`-block and `0x40038200` register addresses, -290.0f bound |
| `gap_4301f4` | 4 cells | 16 | align zero `0x4301F4`; +0.0f `0x4301F8` (`vldr` `0x430024`); cal `-123.456f` `0x430210`; status reg `0x40038038` `0x430230` (orig `0x430126` poll + `ubfx` spin); all pointer cells and unreferenced floats stay retained |
| `gap_align` | `0x42E642`, `0x42FFFE` | 4 | two `00 00` inter-function alignment pads, no referents by design |

Byte math: 6+20+8+18+6+8+8+6+4+40+96+94+16+4 = 334 across
34 placements (multi-placement groups for the pools with holes;
single placements for fully-routed spans).

## Deliberately not routed (5,644 bytes remain `official_blob`)

- Seven code spans (`0x42B9BA` 1078B, `0x42BFA4` is data, `0x42D5C2`
  650B, `0x42E6F2` 434B, `0x42F3DA` 2854B, `0x4303DE` 146B, plus the
  `0x42BFA4`-adjacent code): each needs per-function clean-room
  reconstruction; five call into BL-005 (failed, still opaque) and the
  wrappers at `0x4303DE` call BL-005 targets, so they cannot close as
  typed providers either.
- Pointer tables into opaque code: `0x42E104` (192B, 44 entries into
  BL-012), `0x42E458` (72B, `0x0043xxxx` entries), `0x42E220`
  (`0x0042FB00` into retained `0x42F3DA`), `0x42E8C2` head cell,
  `0x4301F4` pointer cells.
- Unattributed cells: `0x42DAD0` (24B, zero referents, `w/a/r`
  fragments), `0x42EE6C` (4B, zero referents), unreferenced float words
  (`0x42EDF8`, `0x42F018`, `0x42F01C`, `0x4301FC`, `0x430200`),
  unattributed SRAM addresses in the `0x42BFA4`/`0x42CDB0`/`0x42F14E`
  pools, and the `0x42CDE0..0x42CDF8` records.
- `0x42BFA4` span as a whole stays open (48B of 144B retained).

## Method notes

- Byte-pattern scan (16-bit `ldr`/`adr`, 32-bit literal `ldr` family,
  `vldr` F32) over the whole stock image maps every routed word cell
  to original consumers; absolute-word search finds no other
  references to gap starts. Scan script kept at `/tmp/bl009_patscan.py`
  (scratch, not committed); the committed host test
  (`g2/tests/test_bootloader_bl009_gap_literals.py`) re-implements the
  scan and asserts per-cell referents, value decodes, stock bytes, and
  overlay pins.
- No live referents exist in the source build: every consumer above is
  an original-stock instruction inside an already source-compiled
  region whose clean-room successor carries equivalent constants in
  its own pool (spot-checked: clock successor embeds 96000000/250000;
  no successor source names any gap address).
- First multi-placement `in_place_data` groups in this component
  (payload concatenates routed runs in runtime order; holes stay
  `official_blob`): `gap_42cdb0` (3), `gap_42bfa4` (6), `gap_42f14e`
  (9), `gap_4301f4` (4), `gap_42edf6` (2), `gap_align` (2).

## Follow-ups for a re-run of BL-009

1. Close the seven code spans (needs BL-005/BL-011/BL-012 landed
   first for 5 of them; `0x42F3DA` additionally needs its sparse
   index table and trailing block classified).
2. Attribute the SRAM addresses left in the three pools (then route
   the remaining 48+28+28 bytes) and the `0x2301` records.
3. Revisit pointer tables once BL-012 (and BL-005 for `0x4303DE`)
   land; classify the `0x42DAD0` fragments and `0x42EE6C` word.
