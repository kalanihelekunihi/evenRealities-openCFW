# G2 findings: GX8002 codec, EM9305, and C-reconstruction status

This file was distilled on 2026-10-21 from analysis experiments that were
then removed from `g2/analysis/`. The originals are kept in the Git tag
`pre-consolidation`. To recover one, run
`git show pre-consolidation:g2/analysis/<dir>/<file>`; `git ls-tree -r pre-consolidation g2/analysis/<dir>` lists a directory.

The file adds to [toolchains.md](toolchains.md), [memory-map.md](memory-map.md),
[firmware-formats.md](firmware-formats.md) and [libraries.md](libraries.md),
and does not repeat what they already cover. Citations use two short
prefixes:

- `PC:` means `pre-consolidation:g2/analysis/`.
- `CSC/` means `pre-consolidation:g2/analysis/c-source-completion-20261011/`.

The stock locked target is `official-s200-v2.2.6.10`.

Status words follow the source experiments:

- **static** means read from the stock bytes or disassembly only;
- **QEMU** means it was run in the pinned XuanTie QEMU model;
- **host** means a host C harness.

None of these was checked on G2 hardware.

---

## 1. GX8002 codec (C-SKY CK804EF)

### 1.1 Images and loaders

Package-level layout (FWPK, BINH A/B, UART boot stages) is in
[firmware-formats.md §7](firmware-formats.md). The new facts are below.

**Stock BINH headers** (static):

- magic `BINH`, then `0x55aa55aa`, version `0x203`, and stage-1 size `0x3000`;
- the stage-2 length word at `+0x0c` is `0xc800` for A (51,200 B) and
  `0x1408c` for B (82,060 B);
- A's 4-byte stage-2 XIP-length word is `0x8e84` (36,484 B).

Source: `CSC/codec/scatter-loader-evidence.md`.

**Image-A stage-1 loader** (static):

- `0x10000a9e` reads the XIP length;
- `0x10000aa4..ab8` computes the SRAM length `0x397c` (14,716 B);
- it reads flash into IRAM `0x10023400`, then jumps to `0x10023500`.

Source: `CSC/codec/scatter-loader-evidence.md`.

**Image-A loaded intervals** (static):

| Region | Range | Size |
|---|---|---|
| XIP | `[0x10203004,0x1020be88)` | 36,484 B |
| SRAM text+data | `[0x10023400,0x10026d7c)` | 14,716 B (package bytes `[87060,101776)`) |
| Initialized tail | `[0x100264e4,0x10026d7c)` | 2,200 B |
| Stack top | `0x2002f7fc` | — |

Source: `CSC/codec/image-a-layout-obligations.md`,
`CSC/codec/final-imports-and-layout-audit.md`.

**Image-A reset sequence** (static):

- `0x10023500` calls sysinit `0x1002354c`, then `main`, then loops forever.
- sysinit calls clock init, queries the start mode, and clears BSS **only
  when mode = 0**. It then initializes the board and writes the VIC.
- The BSS clear `0x10023528` stores one word per iteration over
  `[0x20026d80,0x2002ecec)` (32,620 B).
- The console port word at `0x2002731c` lies inside that conditional clear.

Source: `CSC/codec/final-imports-and-layout-audit.md`.

**Image-B stage-1** (`binh_b_stage1`). The 24-byte BINH header is
file-only, so runtime PC = file offset + `0x0fffffe8`. Static facts:

- Reset `0x10000100` sets SP `0x20002ffc` and calls `0x10000df0`.
  - If `*(u32*)0x20001720 == 2`, it runs the loader `0x10000d4c`.
- **Normal branch:**
  - takes the package offset from `0x20001724` and adds `0x3000`;
  - reads a 4-byte word via the flash reader `0x10000fdc`;
  - copies `0x1408c` bytes from `pkg+0x3000+word+4` to `0x10003000`;
  - writes the boot state and jumps to `0x10003100`.
- **Alternate branch:** it is selected by the retained marker `0xaabbccdd`
  at `0x20033ffc` (`0x10000d9a`):
  - it reads 4 bytes at `pkg+0x323b0`;
  - it then reads 0 bytes at `word+0x323b4` into `0x20000000`;
  - it stores `0x10000100` at `0x2002d3e4` and re-enters stage-1 reset.
- The flash-reader prologue saves r0/r1/r2 as (flash address, destination,
  count).
- Stock vectors are at `0x10000000`; the default loop is at `0x10000130`.
- Twenty register-branch sites exist: 12 returns, 6 table dispatches, and 2
  computed calls (to `0x10003100` and `0x10000100`).

Source: `CSC/codec/image_b_sram_candidate/stock-stage1-loader-contract.md`,
`CSC/codec/image_b_stage1_candidate/README.md`.

**IRAM/DRAM alias.** Image B has no stage-2 data-copy loop. Its last 300
bytes at `0x10016f60..0x1001708c` are consumed as DRAM
`0x20016f60..0x2001708c`. Image-A XIP code likewise names its data at
`0x2002xxxx`, while the data loads at `0x1002xxxx`. This matches the
SDK linker's paired `stage2_iram`/`stage2_dram` dummy-section model
(`lvp_kws arch/soc/grus/link.ld:239-359`; `spl/spl.c:218-254`).

Whether the hardware actually aliases the two windows is **unproven**.
That is the main open SoC question for any rebuilt codec image.

Source: `CSC/codec/scatter-loader-evidence.md`,
`PC:csky-board-layout-binding-2026-10-09/REPORT.md`.

**Image-B BSS clear.** The stage-2 sysinit `0x1000314c` clears BSS only if
`preserve_memory_10003ffc()` returns 0. RAM can therefore persist across
the alternate boot path. Source:
`CSC/codec/image_b_sram_candidate/four-component-completion-audit.md`.

### 1.2 UART boot stages (stage 1 at `0x10000000`, stage 2 at `0x10002800`)

**Stage 1 (static).**

- UART base word: SRAM `0x20002014` holds the UART base.
  - Bring-up `0x100005c4` writes `0xa0100000` or `0xa0200000` into it,
    chosen by the mode word `0x2000200c`.
  - The status register is word 5; TX/RX is word 0.
  - I/O routines: put `0x10000584`, put_sync `0x100005a0`, try_get
    `0x10000620`, get_char `0x10000640`.
- PMU:
  - The PMU register is `0xa0010030`. Its bit setters `0x10000374..3b0` do
    clear-then-set as two volatile writes.
  - A 26-entry PMU descriptor table sits at `0x20002018` (416 B). Lookup is
    `0x10000780`, giving a six-word output.
  - A 72-byte auxiliary block sits at `0x20002228`.
  - Rails: A `0x10000860` (special peer test for selectors 7/8), B
    `0x10000a30`, C `0x10000b90`.
  - PMU dispatch `0x10000d98` uses jump tables `0x10001e60` and
    `0x10001ea8`.
- Clock rate `0x10000ea0..0x1000107f`:
  - jump table `0x10001ef4`;
  - UART PLL at `0xa0005000`;
  - a 64-bit calibration multiply;
  - `divu` with undefined divide-by-zero behaviour.
  - Ghidra's `0x10000eb8` is a false split inside this function.
- UART config `0x10000c9c` uses MMIO `0xa0005000`/`0xa0005080`.
- XIP routines `0x100018c0`/`0x10001940` write to `0xa2000000`.
- Transfer `0x10001bf8` splits data into 4095-byte chunks.
- Stock `0x10000138` is an **empty** clear-BSS routine; `0x10000130` is a
  trap loop.

Source: `CSC/codec/uart-stage1-source-round.md`.

**Stage 2 (static).**

- Reset is `0x10002900`.
- Init `0x10005100` does a BSS clear `0x1000292c` and four NVIC pairs.
- Clock sub-init `0x100052c4` uses a revision-selected 10-entry table at
  `0x2000949c` or `0x200094ec`.
- Analog-voltage setter `0x10004408` uses a `0xffffffff` sentinel and byte
  truncation.
- UART descriptors are at `0x2000908c`; the active port is at `0x20009840`.
  - The console byte output converts LF to CRLF.

Source: `CSC/codec/uart-stage1-source-round.md`.

> **Stock quirk.** `0x10004428` (called with r0 = 0) leaves a 4-byte stack slot uninitialized.
> Request dispatcher `0x10004db8` (10-way table `0x1000820c`) then reads the
> whole word in case 8, so 3 ambient stack bytes leak into a request.
> Source: `CSC/codec/uart-stage1-source-round.md`.

### 1.3 Image A application (XIP + SRAM)

**Board/audio configuration (static).** The board configuration is a
240-byte structure:

- XIP getter `0x10203004` returns `0x200269a4`;
- its bytes load at `0x100269a4` (payload offset `0x189b8`).

| Off | Field |
|---:|---|
| 0 | input source = PDM (enum 2) |
| 4 / 32 / 60 | three 28-byte input configs, flags `0x498` / `0xc98` / `0x498` (PGA 24, gain enum 2 = 12 dB, stereo tracking) |
| 88 | output mask = 6 (PCM1 \| LOGFBANK; the I2S bit 8 is **off**) |
| 92 / 96 | SADC / PDM config words |
| 100 | I2S-in, 24 B |
| 124 / 148 | PCM0 / PCM1, 6 words each (PCM1 selects PDM) |
| 172 | LOGFBANK, 5 words (PDM left) |
| 192 | I2S-out, 7 words |
| 220 | spectrum, 5 words |

How the audio-output consumer and the I2S defaults use this:

- The consumer `0x10207070`:
  - reads track bits at offsets 5 and 33;
  - passes I2S-out by value to `0x10204228` (four registers, then three
    stack words);
  - then calls `0x10204340(mode 0)`.
- The diagnostic gain lookup `0x1020300c` maps enum 2 to 12.
- Prepared I2S fields: 16-bit, master, 64FS, 16 kHz, L = PDM-L, R = PDM-R.
- The L/R values 1/2 match the KWS DMIC initializer (`lvp_kws` `8bf9ee5c`)
  rather than lvp_aiot `d4aa0094`.

Source: `PC:csky-board-layout-binding-2026-10-09/REPORT.md`,
`PC:csky-board-queue-audit-integration-2026-10-09/REPORT.md`.

**App event queue** (static; public 20-byte `Queue` schema). Placement:

- `QueuePut` is in SRAM at `[0x100261b8,0x10026212)`
  (`DRAM0_STAGE2_SRAM_ATTR`);
- `QueueGet` is in XIP at `[0x10206fb0,0x10206ffa)`.

This split matches lvp_kws and not lvp_aiot, which marks both functions as
SRAM.

Get reads head +4, tail +0, item size +16, buffer +8 and size +12. It uses
signed div/rem and returns 0 when the queue is empty.

App init `0x10208cd4` creates the queue as 64 B of 8-B items, which gives
8 slots of which 7 are usable. `TriggerAppEvent` `0x10208cc0` ignores the
`Put` result and always returns 0, so the caller gets no backpressure.

Source: `PC:csky-queue-placement-binding-2026-10-09/REPORT.md`.

**NPU descriptor initializer `0x102058d4..0x10205950`** (static):

- table `0x20027350`: 10 rows of 144 B, each with 8 descriptors of 12 B;
- each descriptor gets `+32 = 0x10000|(128+slot)`;
- each also gets `+36 = (next & 0x0fffffff)`, a self-linked chain;
- each row gets `+128 = 0x10088` and `+16 = 0x004100ff`.

The only caller is `0x10205cf4`. It first sets the global fields
`+0x5c4=0xa0c00000`, `+0x5c8=0xa0300000` and `+0x5cc=0xa0c00190`, and clears
`+0x5b4` and `+0x5b0`. It then registers callback `0x10205ce0` via
`0x102055b0`.

Source: `PC:csky-descriptor-initializer-2026-10-09/pseudocode.md`, `SEMANTICS.md`.

**NPU accessors** (static):

- `0x102058b4` returns `*(base + idx*4)` into the output pointer.
- `0x102058c4` returns `*(base+256)` into the output pointer.
- Both go through the 2-instruction load helper `0x102055ec`.
- Their callers at `0x10205b2a` and `0x10205b34` take the base from
  `[0x20027350+0x5cc]` and `[+0x5c4]`.

Source: `PC:csky-indexed-word-accessor-2026-10-09/pseudocode.md`,
`PC:csky-offset256-accessor-2026-10-09/pseudocode.md`.

> **Stock quirk: the KWS task built at `0x10206cb0` contains uninitialized words.**
> - The function builds an 8-word SNPU task on its own stack but writes only
>   words 1, 2, 5, 6 and 7.
> - It copies all 32 B via `0x10208c14` (resident memcpy `0x10025738`) to
>   `0x2002e85c`. Words 0, 3 and 4 are therefore stale stack contents.
> - Its sole caller is `0x10206d90`.
>
> A faithful C rebuild must reproduce the stack frame. It must not zero those
> three words.
>
> Source: `CSC/codec/kws-ambient-task-words-boundary.md`, `CSC/codec/kws-ambient-asm-probe/REPORT.md`.

**XIP data tail from `0x1020a8aa`.** Ghidra labels 23 data items here as
"functions" (static):

| Address | Content |
|---|---|
| `0x1020a8aa` | 9 signed gains |
| `0x1020a8ee` | 5 PGA corrections |
| `0x1020a910` | 37 AOUT code/dB pairs |
| `0x1020a9a4` | 12 channel selectors |
| `0x1020acc4` | 64-byte padmux |
| `0x1020ad30` | 26 board pins |
| `0x1020aea2` | 12 LDO trims |
| `0x1020afd2` / `0x1020afd6` | `ESMT` / `ZBIT` flash vendor strings |
| `0x1020b1c4` / `0x1020b204` | idle/TWS mode descriptors |
| `0x1020b908` | standard reflected CRC-32 table (NationalChip `base/src/crc32.c`) |
| `0x1020bd08` | fp-add NaN parts |
| `0x1020bd1c` | 256-byte `bit_length` table used by udiv |
| `0x1020be1c` | 14-case flash-info dispatch |
| `0x1020be54..7e` | six flash product names |

Also, `0x10209c74` is an interior fall-through label inside unsigned
division, not a function.

Source: `CSC/codec/data-tail-ownership.md`, `CSC/codec/xip-link-eligibility-summary.md`.

**Clock records (static):**

- Image A has fixed records at `0x10025cd0..0x10025d04`.
- The start-mode-1 branch (`0x10025aee`) copies 16 B from `0x10025cf4`
  (words `{16,0,0,1}`), which is distinct from the low-power pair at
  `0x10025cd0`.
- Image B's clock table, copied from the Grus SDK, has 26 module records,
  17 dividers and 3 DTO records.

Source: `CSC/codec/excluded-section-eligibility/REPORT.md`,
`CSC/codec/image_b_sram_candidate/integration-note.md`.

### 1.4 Image B (backup, SRAM-only, base `0x10003000`)

**Q15 FFT chain.** This is a prepared 512-point real FFT and its inverse
(static).

Real wrapper `0x1000ef64`:

- takes a 20-byte instance: `fftLenReal`+0, inverse+4, bitrev+5,
  modifier+8, twiddle+12, CFFT instance pointer;
- the forward path is CFFT, then the real split;
- the inverse path is the inverse split, then the inverse CFFT;
- the inverse suffix doubles 512 halfwords with truncating stores.

Complex dispatcher `0x1000f1d4`:

- for fftLen 256 it selects radix-4 butterfly forward `0x1000f3fc` or
  inverse `0x1000f610` (530 B each);
- then it optionally calls bitreversal `0x1000f824`.

Other kernels: `csky_split_rifft_q15` is at `0x1000f068` (86 B).

Tables and descriptors:

| Item | Address | Contents |
|---|---|---|
| Complex descriptor | `0x100143e4` | len 256, twiddle `0x100145d4`, bitrev `0x100143f4`, bitrev length 240 |
| Real coefficient table | `0x100150d8` | `realCoefAQ15_512` |
| Forward / inverse descriptors | IRAM `0x10017020` / `0x1001700c` | callers name them by DRAM `0x2001xxxx` addresses |

The three tables match `libcsky_dsp.a` byte-for-byte (2,272 B):
`cskyBitRevIndexTable_fixed_256`, `twiddleCoef_256_q15` and
`realCoefAQ15_512`.

Callers:

- `0x1000d3dc` (window × Q15, then forward);
- `0x1000dc72` (inverse into the `state_r17+84` buffer);
- DSP transform `0x1000d2a4..0x1000d467` (phase modulo, 15-bit peak shift,
  RFFT).

Source: `PC:codec-q15-fft-caller-tables-20261009T193547Z/REPORT.md`,
`CSC/codec/image_b_sram_candidate/rfft-entry-and-vector-evidence.md`, `dsp-transform-evidence.md`.

**fdlibm float maths from glibc-2.3** (`451c8c22`; static constant match plus
host):

- powf core `0x100100bc`, with entry `0x100100a4` as a call-through;
- logf `0x10010768`, with entry `0x100100ac`;
- sqrtf `0x10010bcc`;
- scalbnf `0x10011194`;
- fixed quiet NaN `0x7fc00000` at `0x10011298`;
- fabsf `0x100112c4`.

Native code keeps fdlibm constants such as `cp_h=0x3f763800` and
`ln2_hi=0x3f317180`.

The binary64 soft-float runtime occupies `0x1000fb14..0x1001283c`. Its
roles match LLVM compiler-rt `adddf3`/`muldf3`/`divdf3`/compare/convert.
The formatter chain `0x10008aa0..0x10008e20` is NationalChip
`utility/libc/printf.c`.

Source: `CSC/codec/image_b_sram_candidate/power-core-provenance.md`, `remaining-51-audit.md`.

**IMCRA noise estimator (static/QEMU).**

- State init `0x1000e384` and its size helper `0x1000e314`: two 257-word
  initializers and a 512-sample window.
- Allocation size `0x1000c6a4`: `(2,3,512,256)` → 17,088.
- Block scale `0x1000e28c` / `0x1000e2c4`.
- Cosine lookup `0x1000ee64` uses a 513-float `sin(2πi/512)` table. 511
  words are exact; two zero-crossing residuals differ.

Ghidra's "bad data" stop at `0x1000e384` is false.

Source: `CSC/codec/image_b_sram_candidate/integration-note.md`, `imcra-*-evidence.md`.

**UART/DMA (static).**

| Address | Role |
|---|---|
| `0x1000afc4` | TX-complete state machine (header → payload → CRC → six 16-B callback records at `0x2002d148`) |
| `0x100047a4` / `0x10004188` | RX DMA submit / apply |
| `0x1000ad60` | RX packet handler |
| `0xaf94` | RX DMA callback |
| `0xb198` | RX IRQ parser |
| `0x1000b5f8`, `0x1000b6f0`, `0x1000451c`, `0x100043a4` | lifecycle, register apply, IRQ source |

The DMA completion `0x1000acbc` re-enters the segment sender with a NULL
availability pointer. Callback `0xaf94` passes NULL pointers, which
leads to a native read of address 0 at `0x1000ada6`.

Fixed RAM:

| Address | Object |
|---|---|
| `0x2002cb80` | heap end |
| `0x2002cb84` | mode |
| `0x2002cf30` | callback table |
| `0x20017398` | platform shadow |
| `0x2002d2b4` / `0x2002d2b8` | mode loop / mode index |
| `0x2002d3e0` | tokenizer cursor |

Source: `CSC/codec/image_b_sram_candidate/integration-note.md`, `four-component-completion-audit.md`.

> **Stock quirks in image B:**
> - `0x1000c5d0` executes `divu` *before* its zero-divisor check whenever
>   hi ≥ divisor. Its only caller passes 1024.
> - The compact-IRQ entry `0x10004880` needs the C-SKY `FREGLIST` assembler
>   form.
>
> Source: `CSC/codec/image_b_sram_candidate/remaining-51-audit.md`, `stage2-entry-source-audit.md`.

### 1.5 DSP kernels: source, ISA semantics and the C/asm difference

**Assembly reproduction.** Nine stock DSP bodies (1,606 B) reproduce
**byte-exact** from the unchanged `lvp_kws` `utility/libdsp/Source.asm`
assembly. The recipe is Clang as the preprocessor only, then the pinned
C-SKY `as -mcpu=ck804ef -mhard-float -EL`.

| Function | Bytes |
|---|---:|
| radix4 butterfly forward | 530 |
| radix4 butterfly inverse | 530 |
| split rfft | 146 |
| split rifft | 86 |
| shift | 116 |
| abs_max | 76 |
| copy | 44 |
| fill | 40 |
| bitreversal_16 | 38 |

Source: `PC:nationalchip-dsp-source-rebuild-20261009T194601Z/REPORT.md`.

**The SDK chooses assembly on purpose.** `utility/libdsp/Makefile` lines
310/321 comment out the C butterfly/split objects, and lines 326–327
select the `Source.asm` versions. Lines 263/340 do the same for
copy/shift/fill. This was already present at the single public import
`a4707698` (2025-04-27, from upstream `ec66ba4f`).

The C files do exist:

- `csky_radix4_butterfly_q15.c` (forward L91, inverse L1005);
- `csky_split_rfft_q15.c` (L95/L261).

They are CMSIS 1.5.1 derived and Apache-2.0. The top Makefile spells the
macro `-DCSKY_SIMID`, while the C code tests `CSKY_SIMD`.

Source: `PC:nationalchip-dsp-kernel-lineage-2026-10-09-source-track/REPORT.md`,
`PC:gx8002-copy-source-attribution-20261010/REPORT.md`.

**The C alternative builds but does not match.** Using the authentic GCC
6.3 with
`-mcpu=ck804ef -mhard-float -O2 -g -fno-builtin -fstrict-volatile-bitfields -ffunction-sections -fdata-sections`:

- ten C units link with no undefined symbols (bitreversal_16 needs
  `-DFOR_X86_64=1`);
- **no** section byte-matches stock: shift is 368 vs 116, copy 84 vs 44,
  fill 70 vs 40.

Source: `PC:nationalchip-dsp-c-compiler-successor-20261009T195245Z/REPORT.md`,
`PC:nationalchip-dsp-complete-c-alternative-20261009T200634Z/REPORT.md`.

**The C version is numerically different (QEMU).** Inverse split imaginary
lane:

- assembly uses `pneg.s16.s`, a lane-wise saturating negate of two
  int16 lanes, on the MULCAX cross product;
- C uses scalar `-cross`.

Example: cross `0x1fffc000` becomes `0xe0014000` packed but `0xe0004000`
scalar. After the next MAC that gives `0x00010000` vs 0, so the emitted
halfword is 1 vs 0. The full 512-point inverse of a constant 32767
differs by 2 (−20868 vs −20866).

Mod-4 rule for DC/Nyquist amplitude *a*, with A=(16384,−16384) and
B=(16384,16384): residues 1 and 3 give imag 1 in assembly and 0 in C.
Residues 0 and 2 give 0 in both; the packed accumulator for residue 2 is
`0xffff`.

The **arithmetic contract** for split-rifft:

- B' = `0x00008000` − A lane-wise;
- B = (sat_abs16(B'lo), B'hi);
- real = SAT32(Rlo·Blo − Rhi·Bhi + Flo·Alo + Fhi·Ahi);
- imag = SAT32(PNEG16(SAT32(Rlo·Bhi + Rhi·Blo)) + Alo·Fhi − Ahi·Flo);
- output = high16 of each accumulator (floor).

**Rebuild guidance: keep the assembly.**

Source: `PC:xuantie-csky-dsp-execution-20261009T201800Z/REPORT.md`,
`PC:csky-inverse-split-negation-diagnostic-20261009T203251Z/REPORT.md`,
`PC:csky-inverse-split-discriminator-20261009T204649Z/ARITHMETIC-CONTRACT.md`.

**ISA semantics** (E804 manual 2.0, sections listed; QEMU `op_dspv2.c`):

| Instruction | Semantics | Manual | QEMU |
|---|---|---|---|
| PNEG.S16.S | per-lane saturating negate (`8000` → `7fff`) | §15.79 | agrees |
| MULCA / MULCAX | special-case x=y=`80008000` → `7fffffff` | §15.125/126 | agrees |
| MULACA / MULACAX | saturate the whole `z + p1 + p2` | §15.130/131 | **wrong**: wraps p1+p2 in int32 first, giving `80000000` at z=0 where the manual gives `7fffffff` (also z=−1 → `7fffffff`, z=INT32_MIN → 0) |
| BNEZAD | decrement, then branch if result > 0 | §14.25 | the Ghidra SLEIGH uses ≠ 0 |
| MULA.32.L | low-32 multiply-add | §14.93 | — |

The all-minimum MAC case cannot occur at the three table-bound split MAC
sites.

Encodings were checked against the vendor assembler: MULA.32.L
r13,r0,r23 = `FAE0844D`, and BNEZAD r18,−17 = `E832FFEF`.

Source: `PC:csky-dsp-negation-semantics-2026-10-09-source-track/REPORT.md`,
`PC:csky-descriptor-initializer-2026-10-09/SEMANTICS.md`, `PC:csky-toolchain-correction-2026-10-09/REPORT.md`.

### 1.6 C-SKY toolchain and simulator identification

**Producing-candidate compiler.** C-SKY Tools **V3.10.15 Minilibc abiv2
B20190929, GCC 6.3.0** (GDB 7.12, target `csky-elfabiv2`).

- The archive is held locally and runs offline in the amd64 container
  `opencfw/iar-base:10.10.2-local`.
- NationalChip's setup documentation names this release.
- The recipe `-mcpu=ck804ef -mhard-float -O2 -g ...` comes from DWARF in
  the stock archive objects.
- The archived GDB has **no simulator target**: `target sim` is
  undefined. It also needs `libncurses5`/`libtinfo5`.

Source: `PC:nationalchip-dsp-c-compiler-successor-20261009T195245Z/REPORT.md`,
`PC:nationalchip-dsp-simulator-probe-20261009T201200Z/REPORT.md`,
`PC:nationalchip-dsp-source-rebuild-20261009T194601Z/REPORT.md`.

**ABI.**

- The vendor GCC (`1e9b7044`) sets `STACK_BOUNDARY` = 32 bits (4 B),
  overriding the V2 ABI document's 8 B.
- r4–r11, r16–r17, SP and LR are callee-saved.
- An SDK runtime directory named CK803 does not identify the CPU; the
  Makefile requests ck804ef.

Source: `PC:csky-toolchain-correction-2026-10-09/REPORT.md`, `PC:csky-descriptor-initializer-2026-10-09/SEMANTICS.md`.

**Simulator.** Use XuanTie QEMU `github.com/XUANTIE-RV/qemu` at
`3287d345` (branch xuantie-qemu-9.0; reports version 8.2.94).

- It is registered at `third-party/tools/xuantie-qemu-csky`.
- Build only `cskyv2-softmmu` and run
  `qemu-system-cskyv2 -M smartl -cpu ck804ef`.
- ck804ef maps to e804df with DSP2 and single-precision FPU.
- smartl has 16 MiB RAM at 0, `0x20000000`, `0x50000000` and `0x60000000`.
- Its UART crashes because of a missing `get_pc`; use the smartl memlog
  instead.
- Upstream `c-sky/qemu` master has no C-SKY target, and Unicorn has none
  either.

Source: `PC:csky-simulator-provenance-2026-10-09-source-track/REPORT.md`,
`PC:xuantie-csky-dsp-execution-20261009T201800Z/REPORT.md`.

**Upstream comparators.**

- `lvp_kws` `8bf9ee5c` is the closest to stock (DMIC init, queue placement).
- `lvp_aiot` `d4aa0094` differs. It contains a different
  `grus_gx8002b_dev_1v` board header, and its I2S five-wire C is absent.
- No G2-specific `.config` or link map is public.

Source: `PC:gx8002-copy-source-attribution-20261010/REPORT.md`, `PC:gx8002-compile-feasibility-20261010/REPORT.md`.

---

## 2. EM9305 (ARCv2 EM, QP/C v6.5.1 QK)

Record layout, the SDK v4.2 archive census and the QP/C configuration are in
[firmware-formats.md §8](firmware-formats.md) and
[libraries.md §3](libraries.md).

Native listings came from objdump with cpu=em,dsp. Payload file offset maps
to address with base `0x301fdc`.

### 2.1 QP/C kernel (static plus host)

| Function | Address | Semantics |
|---|---|---|
| `QEQueue_init` | `0x310f5c..f74` (24 B) | Fields: front event +0, ring +4, end +8 (low byte of qLen), head +9, tail +10, nFree +11, nMin +12, all u8 counters. nFree is qLen+1 truncated to a byte (`nFree = (u8)(qLen+1)`); qLen = 255 wraps it to 0. When qLen = 0 it skips clearing head/tail. Matches `qf_qeq.c` exactly; no assertion. |
| `QK_sched_` | `0x311634..66c` | Root `0x801394`: actPrio +0, nextPrio +1, lockPrio +2, ready set (u16) +6. Computes p = `(u8)log2p1(ready)` with `extb_s` at `0x311644`. Returns 0 if p ≤ act or p ≤ lock. If p ≥ 17, asserts ID 410 at `0x3117d8`, and the assert can return. Otherwise publishes nextPrio. |
| `QK_activate_` | `0x311554..5e4` (144 B) | Active table at `0x80131c`. Takes SETI around get/dispatch/GC, then CLRI and SYNC. Removes ready bits with hardware BCLR. Asserts 500 and 510. Restores the previous priority. |
| QF event alloc | `0x311060` | First-fit pool search; asserts 310/320. |
| Pool get / init / put | `0x31166c` / `0x3116f4` / `0x311798` | Pool-get asserts 310/320/330. Pool-init asserts 100/110, rounds to 4 bytes and uses DIVU. |
| Other | — | Event GC `0x310fb8`; active-get `0x310d38`; framework init `0x311014` (active 0, lock 16); `QF_run` `0x311230`; `QK_onIdle` `0x3115e4` (the caller uses its R0 as the SETI state); `QF_onStartup` `0x311154` (callback slots `0x80fe10`/`0x80fe0c`); wake dispatcher `0x333d18`. |

**Custom APEX instruction.** The stock word `0x3D2F1000` at `0x31163e` is
`log2p1 r13,r0`: opcode 7, sub-opcode 0, two operands, no flags. Its sibling
`log2p0` is 7/1.

- It is declared in SDK `apexextensions.h`, identically in v4.2 and v4.6.
  In the v4.6 port, `QF_LOG2` maps to it.
- The GNU assembler spelling is
  `.extInstruction log2p1,7,0,SUFFIX_NONE,SYNTAX_2OP`.
- Standard `arc-tbl.h` has no entry for it, so plain objdump prints `.word`.
- Its zero-input behaviour has not been verified.

Source: `PC:em9305-qpc-source-binding-2026-10-09/REPORT.md`,
`PC:em9305-qpc-byte-narrowing-successor-2026-10-09/REPORT.md`, `PC:em9305-qpc-opcode-boundary-2026-10-09/REPORT.md`,
`CSC/em9305/REPORT.md`, `CSC/REPORT.md`.

### 2.2 Startup, sleep, WSF and PAL (static; envelopes from `CSC/em9305/body-coverage-boundary.json`)

**Startup:**

- construction `0x302a20` (20-byte descriptor; reserved byte 7 is never
  written);
- startup `0x302ae8` (`BOOT_BootUp`);
- cold `0x302be4`, warm `0x302c30`, lock prep `0x302e14`;
- `BOOT_IRQHandlerPMLHFColdStart` `0x302d40`; `BOOT_IrqActionRoutine`
  `0x302d84`;
- early IRQ `0x3068c8`; architecture restore `0x30690c`;
- timer IRQ registration `0x313904`;
- controller init `0x30f4b0..568`, which calls ROM `0x103c40`.

**Sleep:**

- sleep `0x3126e0..8e4`; metadata `0x3125a4`; timer callback `0x3128e4`;
- registry head `0x3108f4`; finalizer `0x3117f8`; registrar `0x311848`;
- resume hook `0x3110f4`; resume `0x311218`.

**WSF:**

- Buffer pool:
  - pool init `0x313dfc`;
  - first-fit alloc `0x313ce0`: 16-bit header, optional histogram and miss
    statistics;
  - free `0x313d98`: marker `0xfaabd00d`.
- Messages:
  - message alloc `0x313fd8` / `0x32e454`: the handler byte is at msg−4
    and the next pointer at msg−8;
  - queue enqueue `0x314008`, append `0x31416c`, remove `0x313ff0`, peek
    `0x31403c`, post `0x314210`.
- Critical section enter/exit `0x313f54`/`0x313f6c`.
- Tasks and timers:
  - task table `0x314250`; the event post `0x314258` wakes the task only
    if its prior events were 0;
  - `WsfTimerInit` `0x314280`; sorted start `0x333dcc` (equal ticks keep
    FIFO order); stop `0x333e24`; periodic `0x333e4c`;
  - `WsfOsSetNextHandler` `0x3140b4`; `wsfDispatcherThread` `0x333c44`.

**PAL:**

- critical section `0x310678`/`0x31069c`: CLRI/SYNC/SETI with a mod-256
  depth counter;
- `PalSysInit` `0x3106e4`; baseband init `0x310088` (ROM call; TRAP0 on
  error); timer init `0x310128`; current time `0x310104`;
- random `0x310814`/`0x310850`/`0x310894`;
- empty hooks `0x3101e4`/`e8`/`ec`.

Source: `CSC/REPORT.md` (sections "WSF ...", "PAL ...", "Startup/IRQ registration", "Warm startup").

**Auxiliary timer/event object** (not a firmware record):

- installer `0x304360`;
- init `0x312d80` clears 36 B at `0x805f04` and installs a callback at
  `0x801640`;
- handler `0x312ca0` services a 4-entry event ring and tracks the maximum
  elapsed time as a halfword.

Source: `CSC/em9305/auxiliary-record-source-round.md`.

**Radio and HCI transport:**

- Radio hardware init `0x31028c`.
- Activation `0x310580` writes AUX register 1666 = 4, then 8.
- Calibration `0x311ffc` uses `XBFU`/`VPACK2HL`. Mode apply `0x3120a0`.
- Tables:
  - revision table at `0x333ff0` (204 B);
  - 20-byte descriptor templates at `0x3343a8`/`f8`/`0c`/`34`;
  - PHY table `0x334488` = `[2,1,3,1,1,1,4]`;
  - packet defaults at `0x3344e0`;
  - CRC-32 table (reflected `0xedb88320`) at `0x334550`, used by
    `0x304678`.
- `0x314fa4` deliberately reads absolute address `0x2c`.
- HCI transport (the bus is probably UART, given the `EMSG_SetUartBaudRate`
  label):
  - configure `0x304764`; PAL transport init `0x310730`;
  - RX state machine `0x3156cc` (signed minimum-header check; errors
    A0/A1/A2);
  - TX poll `0x304698`: 5 attempts, round-robin, 255-byte cap;
  - delivery `0x31588c`.

Source: `CSC/em9305/auxiliary-record-source-round.md`, `CSC/REPORT.md` ("Transport ...").

### 2.3 Link layer and HCI command handling (static)

**LL setup:**

- LL init `0x30c098`. A BL delay slot at `0x30c0aa` provides the first
  transport halfword.
- Defaults `0x30bc60`.
- 24-provider construction `0x30c0e8`.
- Command/event dispatcher `0x30a930`: a 35-provider scan with a rejected
  command event.
- Routers `0x30cd6c`/`0x30cd80`; `LlSetBdAddr` `0x30cf2c`; `PalBbLoadCfg`
  `0x30fd3c`.

**Command handlers:**

| Opcode | Handler |
|---|---|
| `0x2019` (LE Enable Encryption) | `0x330568`. It decodes two LE16 values, calls controller op `0x30e054`, and emits status via `0x331bf8`. Any other opcode goes to the five-command dispatcher `0x332278`. |
| Private `0xfff7` | `0x332490` |
| `0xfff8` response | `0x33052c` |
| Vendor dispatcher (FFF3 formats) | `0x32eb34` |
| Primary handler | `0x32e5d4` |
| `0x2030` | `0x3316e0` |
| `0x2033` / `0x2034` | `0x30cba0` / `0x30e120` (PN9 generator `0x332c50`) |
| `0x2035–0x2040`, `0x207f` | `0x3324e0` |
| `0x2083` / `0x2084` / `0x2086` (PAwR) | `0x331204` |
| `0x2076` | `0x331074` |
| `0x2027–0x202e`, `0x204e`, `0x207c` | `0x331868` |
| `0x2066–0x2067` | `0x332194` |
| `0x2068–0x206a` | `0x332038` |

The names in brackets come from standard HCI opcode numbering. They are
inferred, not stated in the source experiments.

**Internal command types:** `0x1801` (`0x30e054`, 30 B), `0x1a01`
(`0x30c2e0`, 4 B), `0x1501`, `0x1701`, `0x1b01`, `0x1c01`, `0x1f01`,
`0x2101`, `0x2301`, `0x2801`.

**Feature-gated event maps** `0x332394..48e`:

- they cover types 11/12/13/17;
- extended type 11 changes byte +9 of the request;
- type 13 falls back when the feature is off or allocation fails.

**Connection slots:**

- Slot accessors `0x306fdc`/`0x30731c`/`0x307480` index a 912-byte slot
  with `mpyuw r0,r0,912` (`209f 040e`).
- The pending map at ROM `0x334479..488` is checked by `0x307434`: valid
  ops 21..35 under sparse mask `0x7ccf`.
- Optional slot callback `0x3072f0` reads word 204, which is byte 816.

**Periodic advertising:** enable `0x30daf8`/`0x309244`; data
`0x30904c`/`0x30dac8`. The PAwR units are at `0x3227a4`, `0x3227e0`,
`0x322834`, `0x31694c`, `0x316984`, `0x3169b4`, `0x31e84c` and `0x3228a8`
(`BbPawrCentralInit` and `LlSetPeriodicAdvSubeventData` appear in
`g2/symbols/ble_em9305.tsv`).

Source: `CSC/em9305/REPORT.md`, `CSC/REPORT.md`.

> **Stock quirks to keep in a faithful rebuild:**
> - **Status ignored or misreported:**
>   - `0x30c2e0` returns 0 even when its allocation fails.
>   - `0x330ce0` type-2 rejection paths return 1 and emit no event.
>   - `0x303fb8` returns 0 on some success paths.
>   - `0x309910` and `0x309aa4` ignore the result of their apply child.
>   - `0x30ff0c` returns an incidental stack-relative R0.
> - **Uninitialized data, or reliance on register side effects:**
>   - `0x30fdb8` leaves scratch undefined for lengths above 4 that are not 16.
>   - `0x2086` scratch byte 11 is never written.
>   - `0x3319bc` relies on memcpy leaving R1 advanced.
>   - `0x326b00` passes a limit byte as a pointer.
>   - `0x312918` leaks live R2/R3 into its callbacks.
> - **Unbounded loops and unchecked arithmetic:**
>   - `0x302748` returns `0x7fffffff:ffffffff` when dividing by zero.
>   - `0x30c3a4` never terminates when the divisor is 0.
>   - Sampler `0x3259fc` loops forever on an empty mask.
>   - `0x3096a8` can underflow its unsigned budget.
>   - `0x310038` does not bound the length.
>   - `0x325740` advances 48 B on every iteration.
> - **Branch delay slots:** many `BL.D` delay-slot stores execute before
>   the call.
>
> Source: `CSC/em9305/REPORT.md`.

### 2.4 Resident ROM interface (12 imports of the current C graph)

The ABIs below were taken from call sites in
`g2/components/em9305/qpc_scheduler_candidate/controller_init.c`:

| ROM address | Role and ABI |
|---|---|
| `0x1030e8` | allocator capacity `u32(u32)`; `0x313fa8` returns capacity − query |
| `0x1009c0` | AES key install `(key, 0)` |
| `0x10090c` | AES block `(in, out, 0)`. Both AES calls run inside the PAL critical section at `0x30ff0c`, with byte-reversed 16-B key/in/out. |
| `0x108178` | P-256 base-point multiply `(scalar, out64)`; returns 0 = OK |
| `0x1081e8` | point multiply `(pt64, scalar, out32)`; returns 0 = OK. Wrappers `0x30ff70`/`0x30ffbc` reverse words and bytes. |
| `0x108260` | point validate `(pt64)`; returns 0 = valid (`0x3100c8`) |
| `0x100dd4`, `0x100ddc`, `0x100fc0`, `0x101038`, `0x101054` | radio sequence used by the channel-3/2 schedulers `0x311e60`/`0x311ef0`: `dd4(1)`, `ddc(ch,0)`, `1038(ch,5\|6,0)`, `fc0(ch,desc[4],0)`, `1054(ch,1)`, `ddc(ch,1)`. Descriptor = `{enc, 0xf04068, end, 0}`. |
| `0x10a7f8` | TRNG `(0x805e40, 2, buf8)`; a nonzero result causes `TRAP_S 0` (`0x310038`) |

Other ROM calls are made through cast pointers:
`0x101d50`, `0x103b0c`, `0x103c40` and `0x10aa8c`
(`sleep_rom_bindings.c`).

**How binding works.** It runs `arc-elf32-ld -r --defsym=<name>_<addr>=<addr>`
over `candidate.o`, driven by `resident_rom_bindings.json`. Each address
must appear in the native listing as `bl …;0x<addr>`. The binding script
`CSC/em9305/verify_resident_rom_bindings_20261014.py` lived in the deleted
tree.

Source: `CSC/six-current-20261014.json`, `CSC/em9305/REPORT.md`.

### 2.5 Provenance, SDK and toolchain (EM7D)

**SDK v4.2 attribution:**

- The v4.2 mirror (`C0R3YY2/em9305_original` at `e4412bc9`) gives 40 named
  bodies or objects with unique matches.
  - 35 of them sit on canonical symbol boundaries.
  - `RF_RfChannel2BleChannel` coincides with `llConvertRfChanToChanIdx`.
  - `cRF_MacTiming`, `cRF_config`, `cRF_powerLevelConfig` and
    `gIRQ_PRIORITY` are data.
- 18 bodies distinguish v4.2 from v4.6. Seven have the same size but
  different bytes:
  - `IRQ_Cleaning`;
  - `NVM_BeforeOperation`;
  - `PML_Dbm2PmlRfPower`;
  - `RF_Ln`;
  - `RF_RfChannel2BleChannel`;
  - `RF_TestModeStart`;
  - `gIRQ_PRIORITY`.
- Eleven differ in size, including `NVMEntry_CopyJLITable`,
  `RF_SetMacTiming`, `SleepTimer_SetWakeupTime` and
  `scan15_4CheckParameters`.
- A relocation-masked Thumb-style scan found no further matches.
- The stock timers Timer0 `[0x305b1c,0x305bde)` and Timer1
  `[0x305be0,0x305ca2)` (194 B each) do **not** match the v4.6 bodies.
- The v4.2 release notes cite EMB Mango 2.2.0 and qualification Q338654 /
  design 244581.

Source: `PC:em9305-v42-reloc-independent-20261010-daybreak-low/REPORT.md`,
`PC:em9305-timer-version-comparison-2026-10-09/REPORT.md`, `PC:em9305-v42-provenance-config-20261010-daybreak/REPORT.md`.

**What the mirror contains.** It is a personal snapshot with no licence: v4.2
EM-Core images, maps and headers, but **no EM-Core source**. It has two
compile profiles:

- `common/9305/tool_config/compile.arg`: ARCv2 EM core4, code density,
  LPC16, PC24, radix-4 div/rem, swap, bitscan, mpyd, shift-assist, barrel
  shifter, DSP2/complex/divsqrt/ITU/accshift, SP-FPU, timers 0/1, RTC,
  stack check, CCM, DMA.
- `compile_mw_for_em.arg`: the narrower `em9305` TCF.

Two CMake files go with them:

- `arcv2em.cmake` uses `ccac`/`arac`.
- `build_configs.cmake` defines ASIC and DI03/04/05, with empty CFLAGS.

The selected files are stored in ignored storage at
`third-party/local-vendor/sources/em9305-v4.2-public-mirror/`.

Source: `PC:em9305-v42-provenance-config-20261010-daybreak/REPORT.md`.

**Open-toolchain build.** ARC GNU **2026.03**:

- `third-party/tools/arc-gnu-release` at `18942eae`, SHA-verified;
- flags:
  `arc-elf32-gcc -mcpu=arcem -mcode-density -std=c11 -ffreestanding -fno-builtin -O2 -fno-strict-aliasing`;
- the build checks ELF machine 195 and `Tag_ARC_CPU_base: ARCEM`.

This is a modelling compiler, not MetaWare. Example difference: GNU emits
full-width LD/ADD where stock uses CD2 compact forms, so `0x312918` is
630 B against stock's 622 B.

Source: `CSC/REPORT.md` ("Tools, provenance"), `CSC/em9305/REPORT.md`.

**ISA notes:**

- Encodings seen:
  - MPYUW (major 4/0x1f);
  - private major-6 minor `0x1e`/`0x1c` products (compact `7a6a`/`7a2c`);
  - MPYWHL `311c0000`, MACWHL `341d1083`, MPYWHUL `321e004d`, MACWHUL
    `311f03fe`, ASLACC `282f0fbf`, MPYWHL.EQ `30dc0081`.
- Still undecoded: `382f000e` at `0x312344`, plus `301c0040`, `311c0001`
  and `321c0302`.
- GNU `as` quirks:
  - it rejects positive ASLACC immediates (use a register);
  - CS and LO share condition code 5;
  - the BBIT `.t`/`.nt` Y bit is inverted relative to the disassembler.
- DIVU by zero leaves the destination unchanged when DZ = 0 and traps when
  DZ = 1.
- The default objdump and Ghidra's ARCompact module mis-decode this code.

Source: `CSC/em9305/REPORT.md`, `CSC/em9305/auxiliary-record-source-round.md`.

**Still missing for a real build:**

- the producing ARC port (`qf_port.h`/`qk_port.h`);
- the QP configuration;
- the EM-Core/Packetcraft controller source;
- the product callbacks;
- the linker script and RAM map;
- the MetaWare runtime;
- the four-record placement inputs.

Source: `PC:em9305-source-compile-feasibility-20261010/REPORT.md`.

---

## 3. C reconstruction status by image (final state 2026-10-14..17)

The aggregate audit is `PASS_EXPERIMENTAL_SIX_CURRENT_C_EVIDENCE_AUDIT`, with
**0 of 6 payloads source-complete** and no full-payload link. Each row is a
separately qualified candidate object, not one unified build. The C
sources live under `g2/components/`, which was not deleted.

Source: `CSC/six-current-20261014.json`, `CSC/all-six-current-build-checkpoint.json`.

| Image | What compiles/links | Imports left | Main blockers |
|---|---|---|---|
| Codec A | 233 C-SKY units. Source-only EXEC ELF has entry `0x10023500` and XIP ending at `0x1020be3c`. | 0 undefined | Holes of 76 B (XIP) and 104 / 674 B (SRAM) have no authenticated fill. 25 GC-discarded helpers need an indirect-root proof. Alias, runtime and hardware are unproven. |
| Codec B | 316-object source-fit stage-2 ELF of exactly 82,060 B; separate 11-unit stage-1 (`0x1734` B load) | 3 data contracts (earlier: BSS bounds, product/IMCRA config, FP environment, word at address 0, ambient UART direction) | Stage-1 loader trace, alias, retained-RAM values |
| EM9305 | QP/C + WSF + LL + PAL graph (1,485 definitions / 67 imports on 10-12) | 12 ROM, bound to 0 | MetaWare EM7D config, QP port, EM-Core source, product config, 4-record layout |
| Apollo Boot | 374 units, 1,012 providers; bounded link at `0x410000` = 159,180 B (4,628 B headroom under `0x437fe0`) | 3 ROM | Indirect roots, final placement, M55 execution |
| Apollo Main (incl. Audio) | Peripherals link: 2,932 definitions / 757 unresolved (82 called, 675 address-only); combined audit: 83 unresolved | 83–132 | Product RAM initializers, FAL/FlashDB, logger, LVGL/fonts, Cordio, ROM data |
| CASE | 108-unit command archive; command+startup absolute ELF with 0 undefined | 0 (graph) | Text overflows stock by +1,520 B (−Oz GC) to +8,104 B (with strings); only the first 2 vector words match |
| Touch | 58/58 units | 4 generated-data imports (+4 weak ITM/frame) | Missing product `cycfg_capsense.c/.h`; LP-history array size |

### 3.1 Codec details

**Compiler and options.** Pinned GCC 13 C-SKY, `ck804ef`, hard float.

- `-O2` is the default. `-Os` is applied per file only when the file's hash
  matches the qualified list.
- With that setting, 249 of 339 XIP slots fit the stock function sizes and
  62 still overflow, by 1,150 B in total. The largest overflows are:
  - formatter `0x10206a84` (+164 B);
  - AOUT `0x10207070` (+150 B);
  - UART RX callback `0x10208098` (+116 B).

Source: `CSC/codec/xip-link-eligibility-summary.md`.

**Imports that remain genuine:**

- `__fe_getround` and `__fe_raise_inexact`, pulled in by compiler-rt
  20.1.8 `adddf3`. No GX8002 FPU-mode evidence exists.
- The three KWS ambient task words (§1.3).

Source: `CSC/codec/final-imports-and-layout-audit.md`.

**Size reductions used for image B:**

- the 1 KiB CRC table is replaced by 62 B of generator code;
- the 2,052-B IMCRA cosine table becomes 129 quarter-wave words;
- four BSS objects are pinned to fixed addresses (§1.4).

Source: `CSC/codec/image_b_sram_candidate/four-component-completion-audit.md`.

### 3.2 EM9305 details

See §2.4 for the ROM imports. The scheduler candidate keeps `log2p1` and
`mpyuw` as named inline ISA instructions; it does not approximate them with
ordinary arithmetic.

Source: `CSC/em9305/REPORT.md`.

### 3.3 Apollo Bootloader (image base `0x410000`, stock 148,599 B)

**Resident ROM imports:**

- `0x00000049` INFO read (`opencfw_boot_rom48`). It is an
  ambient-register thunk with no C prototype.
- `0x00000041` cycle delay (R0 = cycles).
- `0x0200ff21` MRAM program, with 5 arguments. It is reached through
  `0x42e4a0` → `0x42e4f4`, inside a critical section.

**Layout:**

- MSP `0x2007fb00`, VTOR `0x410000`, reset stack limit `0x2007d000`.
- The image must end at or below `0x437fe0`.
- Scatter loading:
  - Four 18-word records live at `0x4330d8..0x43311f`.
  - Walker `0x43299c` stops when its cursor equals the end record.
  - The records unpack 22 B into 24 B of ITCM helpers at `0x40`, and 625 B
    into 1,371 B at `0x20000000`.
  - They zero `0x2000055c..0x200271c8` and 4,096 B at `0x20080000`.
- The 1,371-B initialized object holds:

  | Offset | Contents |
  |---|---|
  | +0x158 | 27 SPOT transition callbacks |
  | +0x200 / +0x204 / +0x208 | storage read / prog / erase callbacks |
  | +0x244 | 216-B profile table |
  | +0x31c / +0x334 | logger pointer arrays |

  It contains 34 Thumb pointers in all.

Source: `CSC/apollo/REPORT.md`, `CSC/apollo/BOOT_GC_PLACEMENT_ROUND.md`, `CSC/apollo/BOOT_WHOLE_BODY_AUDIT_20261011.md`.

**IAR DLIB runtime:**

| Address | Function |
|---|---|
| `0x422874` | TLS leaf, returns anchor `0x20000518`; decimal-point pointer at +0x24 |
| `0x422590` | C11 constraint handler `(msg, NULL, 34)` via `0x20027190` |
| `0x41560c` / `0x4156ac` | fill / aligned copy (callers ignore R0) |
| `0x41e47a` | formatter (`strchr("hjltzL")`; hex-float uses scale2 `0x422700`) |
| `0x41f15c` | integer renderer |
| `0x41f2c8` | stream put |
| `0x422698` / `0x4226cc` | binary64 compares that return their result in **APSR flags** |
| `0x42287c` | u64 divide |
| `0x4276bc` | memmove |

The Boot formatter `0x41e47a` and Main's `0x481836` are the same IAR
printf core. They differ only in 23 relocated BLs.

Boot's `__aeabi_d2f` in the rebuild comes from LLVM compiler-rt 20.1.8
`truncdfsf2`. That is a stand-in, not the stock IAR code.

Source: `CSC/apollo/BOOT_TLS_READINESS_AND_CAPACITY_ROUND.md`, `CSC/peripherals/REPORT.md`.

**Third-party code and logging:**

- LittleFS sits at `0x410000–0x416000`.
- TLSF v3.1: FFS `0x4169e2`; control block 0xC74 B; arena `0x70800`.
- FreeRTOS: TCB 112 B, state at +0x6c, name at +0x34.
- Ambiq HAL 5.1.0 (MSPI) and EasyLogger are present.
- EasyLogger tables:
  - level labels at `0x434178`; colours at `0x43403c`;
  - mount logs `ensure_directories` `0x4210c8` call EasyLogger `0x4176ce`
    with tag `file_system`.
- LittleFS and TLSF errors go to the plain printf `0x415fae` (buffer
  `0x20024cd0`, sink `0x200270cc`).

Source: `CSC/apollo/BOOT_FOUR_LINKED_FRONTIER_REVIEW.md`, `CSC/apollo/REPORT.md`.

**Semantics of key functions:**

- Startup power root `0x41c4b4` (810 B). It is called with no arguments
  by `0x41fa50`. It uses the caller's live R5/R7 and restores R1–R3.
- Startup info cache `0x41c320`.
- Readiness gate `0x42bf54`:
  - reads `0x40021008` and `0x40021010`;
  - enters mode 29;
  - calls the temperature provider with −40.0f;
  - polls `0x400083e0` for 2,500 ticks.
- Clocks:
  - SYSPLL postdivider `0x427160`: VCO minimum 60 or 240 MHz, and a tie
    picks 240.
  - VCO limits `0x426f6c`: `<60`, `>960`, `>=240`.
  - PLL coefficient tables at `0x433cb8` and `0x433cc8`.
  - SYSPLL disable token `0x01504c30` → register `0x400204d8`.
- STIMER:
  - the ISR `0x41b670` reads the interval four times;
  - `0x41b6e2` tests raw status `0x40008904` without the enable mask.
- MSPI ISR `0x426536` expects handle magic `0x01bebebe`.
- GPIO descriptors `0x42f674`: 97 rows; none installs a callback.
- SPOT hook table `0x20026e38`: 15 slots. Installer `0x41ce52` handles
  revision 33–36 × variant 0–3.
- Ambient-register ABIs (Ghidra shows them as 64-bit returns):
  - `0x414948`, `0x41b854`, `0x422ba8`, `0x42a43a`, `0x416088`;
  - PCM2.2 selectors 11/12/13 pack four 7-bit fields from base+0x64;
  - selectors 24/25/26 are three separate `BX LR` stubs.

Source: `CSC/apollo/BOOT_*_ROUND.md`.

> **Stock Boot bugs and quirks:**
> - `pow10` `0x41f270` shifts a signed exponent with `asrs`, so a negative
>   exponent never terminates (`CSC/apollo/BOOT_POW10_SIGNED_ROUND.md`).
> - If the INFO1 read of word `0x244` fails on the `0x41d792` → `0x41d69c`
>   path, the record pointer's low byte leaks into record word 3
>   (`BOOT_DEVICE_MODE_AMBIENT_ROUND.md`).
> - INFO dispatcher `0x4213e6`:
>   - it bounds `offset+count` with a wrapped 32-bit check;
>   - its fallbacks `0x42149c` and `0x421532` are unreachable;
>   - `0x4213da` maps offsets ≥ `0x200` by adding `0x280`.
> - Missing NULL checks and an over-read:
>   - ADC `0x42ea6e` reads ctx+4 before its NULL check;
>   - UART `0x42372a` reads the module word before its NULL check;
>   - GPIO IRQ lookup `0x43409c` over-reads when `pin>>5 > 3`.
> - Queue reset `0x419be8` divides by the item count without checking it.
> - Unicorn cannot execute M55 MVE/LE/cset/cinc, so the oracles recompiled
>   for M4/M33.

### 3.4 Apollo Main (incl. "Audio") (image base `0x438000`; file offset = address − `0x437fe0`)

**Startup:**

- SP `0x2007fb00`; Thumb reset entry `0x005e4233`.
- Zero-init constructor `0x5fa01e`; low-RAM decompressor `0x43a11e`.
- The compressed init descriptor at `0x75d3f4` produces the Cordio WSF pool
  table at `0x200003b0`: `{16,8},{32,4},{64,10},{480,20}`.
- The startup function `0x4b7f64` uses a `0x2940`-byte arena.

Source: `CSC/peripherals/REPORT.md`.

**Runtime helpers:**

| Address | Function |
|---|---|
| `0x481836` | IAR printf core |
| `0x44b76c` | bounded vformat |
| `0x473036..3ee` | Ambiq-utility formatter |
| `0x47cc60` | u64 divmod; divide-by-zero returns the dividend with remainder 0 |
| `0x43c0e4` | memset with ABI `(dst, len, val)` |
| `0x5fa0a4` / `0x5fa0ba` | BASEPRI mask/restore (`0x30`) |
| `0x4d09b4` | semihosting `BKPT 0xAB` (file error) |
| `0x541b74` → `0x585120` | fatal path, ends in a `SYS_EXIT` loop |

`format.c` needs `-mfpu=fpv5-d16 -mfloat-abi=softfp`; otherwise the
compiler pulls in `__aeabi_d2f`.

Source: `CSC/peripherals/REPORT.md`.

**Libraries:**

- FreeRTOS + CMSIS-RTOS2:
  - `osMutexNew` `0x44971c`, `xTaskGenericNotify` `0x455c48`;
  - TCB 0x70 B with stack fill `0xa5`;
  - initial frame `0x44215a`.
- TLSF: alloc `0x4d0722`, free `0x4d0808`.
- LittleFS: sync `0x4cdf74`, close `0x4cdce4`.
- TinyFrame:
  - `TF_AddIdListener` `0x4918c2` (128 entries of 24 B);
  - parser `0x491be4`.
- nanopb 0.4.9:
  - decode `0x490120` → `0x48fe98`;
  - ring descriptor root `0x7766dc` (20 messages / 71 fields);
  - EvenAI descriptor root `0x777144`.
- LVGL 9.3 with FreeType (`FT_DivFix` `0x524754` wraps 32-bit quotients).

Source: `CSC/peripherals/REPORT.md`, `CSC/apollo/even-ai-frame-process-4e31cc-gate-20261016.md`.

**Display, LVGL and fonts:**

- The framebuffer is at `0x20080000`.
- Driver `0x473782` sets up a 576×288 display.
- Queues and tasks:
  - `DispQueue` holds 96 × 12 B;
  - `ui_task` has a `0xc000` stack and priority `0x2c`.
- LVGL state:
  - LV root is at `0x2006f548`;
  - `lv_init` is `0x473548`;
  - the functions called `theme` at `0x48ba64`/`0x48ca26` are really the
    flex/grid layout installers.
- Fonts:
  - The symbols named `audio_uart_display_ring_*` are really the font
    manager: create chain `0x46cae0`, init `0x46d464`.
  - Font descriptor tables are at `0x20002c48`/`0x20002c78`.
  - The glyph cache holds 512 entries of 40 B at `0x20324600`.

Source: `CSC/peripherals/REPORT.md`.

> **LVGL quirk.** When render-invalidate `0x4534be` reaches 32 areas, it
> stores the full-screen rectangle instead of the clipped input.

**Audio hardware:**

- I2S:
  - MMIO base `0x40208000` + n·`0x1000`; handle magic `0x01125125`;
  - `DRV_Gx8002_I2SInit` is at `0x57a65c`;
  - two handle rows of 100 B at `0x20071114`;
  - configuration at `0x20000000`, DMA descriptor at `0x20000740`.
- PDM:
  - init `0x57b4a8` (production) and `0x57b770` (alternate);
  - four handle rows at `0x200718c8`.
- Codec power control:
  - PowerOn `0x57a508` and PowerOff `0x57a5bc` drive GPIO 6, 7 and 8;
  - Reboot `0x57a816` powers off, waits 100 ticks, powers on, then
    optionally waits 1,500 ticks.
- UART HAL: magic `0x1ea9e06`, base `0x40039000`.
- Logger transport nodes are 269 B.

Source: `CSC/peripherals/REPORT.md`.

> **Main stock quirks:**
> - I2S prepare dereferences handle+4 before checking for NULL.
> - Power enable `0x47f5b8` and disable `0x47f7ae` ignore the SPOT/GPU
>   callback result.
> - Several routines return a stale R7 or R3 (clock enable `0x4c3074`,
>   `DmDevVsInit` `0x4b308c`).
> - Fault lookup `0x509b48` truncates its index to u8, so it wraps at 256.
> - Terminal FSM `0x5e7b74`: its callbacks receive `(old_state, payload)`,
>   and the state byte is at obj+0x275.
>
> Source: `CSC/peripherals/REPORT.md`, `CSC/apollo/terminal_fsm_callback_payload_20261016.md`.

**Blockers:**

- FAL/NOR product tables and the 256-row FlashDB initializer;
- the extended logger `0x43d574` (category mask at byte 216 + 4·level);
- product RAM initializers and placement (no linker map);
- remaining LVGL style, font and timer callbacks;
- Cordio security;
- ROM data ownership.

The OTA bootloader flag is a 16-B NOLOAD page at `0x7fe000`.

Source: `CSC/apollo/REPORT.md`, `CSC/six-current-20261014.json`.

### 3.5 CASE (STM32G0)

**Image and memory:**

- `firmware_box.bin` = 55,784 B: a 32-B `EVEN` header plus a 55,752-B
  payload. Header word `0xd9c8` is the stock image length.
- Vectors:
  - SP `0x20002c88`, reset `0x08000145`;
  - NMI `0x08006d70` and HardFault `0x08006778` are infinite loops;
  - SVC is a bare `bx lr`.
- CRT:
  - 104 compressed bytes at `0x0800d95c` expand to 420 B at
    `0x20000000`;
  - zero-fill runs to `0x20002c88`;
  - app entry is `0x0800a598`.

Source: `CSC/m0/WHOLE_IMAGE_GAPS.md`, `CSC/m0/CASE_FLASH_CAPACITY_AUDIT.md`.

**Peripherals:**

- CW221X fuel gauge at I2C `0x64`:
  - chip ID `0xa0`;
  - 80-B profile at register `0x10`, also held in RAM at `0x2000002a`.
- The PMIC is bit-banged on GPIO `0x50000400`.
- The clock runs at 16 MHz (`0x20000124`).

**OTA:**

- Writer `0x2e04` stores data to `0x08040000+off` in 8-B doublewords.
- Erase `0x2d48` covers 128 pages.
- `0x1574` reads at most 240 B per packet and **has no maximum-size
  check**.
- The checksum `0x2cc0` is a big-endian word sum.

**Protocol:**

- Legacy switch `0x08000928`: 254 routes; `0xee` is standby and `0xff` is
  reset.
- Binary switch `0x08000e1c`.
- Record parser `0x08001e94` handles cmd/sub `0x58`/`0x20`, which carries
  the size.

**Formatter `0x08009210`:**

- `%p` prints 8 hex digits with no `0x`;
- `%#x` of zero has no prefix;
- a NULL `%s` faults.

Source: `CSC/m0/REPORT.md`, `CSC/m0/WHOLE_IMAGE_GAPS.md`.

> **CASE stock quirks:**
> - `0x38e0` never initializes selector word 1 before `0x4a00` reads it.
> - `0x18e4` passes `%d` with no argument.
> - The final timeout in OTA TX `0x2744` returns without logging anything.
>
> Source: `CSC/m0/WHOLE_IMAGE_GAPS.md`.

**Rebuild toolchain.** Apple clang
`--target=arm-none-eabi -mcpu=cortex-m0plus -Os/-Oz -ffreestanding`.

- No libgcc is used: memcpy is in source, and the formatter uses 32-bit
  limb division.
- `-Oz` on two of the files pulls in `__aeabi_uidivmod`.
- The stock compiler is not identified. [toolchains.md](toolchains.md)
  §6 says GNU/newlib, and `decompilation-status.md` says Keil AC6.

Source: `CSC/m0/CASE_LAYOUT_SIZE_ROUND.md`.

### 3.6 Touch (PSoC 4000T)

**Reset copy and RAM:**

- Reset copies 964 B from ROM `0xb58c` to `0x200004c0`.
- It zeroes `0x200008a8..0x20000f57`.
- `system_reset` `0x7e14` writes AIRCR = `0x05fa0004`.
- The CapSense context table at `0x200004ec` holds 15 pointers in v6
  order.
- LP history at `0x2000065e` is an array of u16 entries, up to 212.
- The internal context at `0x20000c50` is written up to offset +117.

**ROM data:**

- Widget configs at `0xb0f8`/`0xb188`/`0xb218`, with a 144-B stride.
- Common config at `0xb2a8`.

**CapSense version.** The 144-B ROM widget stride matches only the **v5
LP** typedef (`FIFTH_GEN_LP=1`, commit `a4aa9306f7`). The 60-B widget
context matches v6. Versions 6.10 (148 B) and 11 (152 B) do not match.

**Compiler.** The GCC crtstuff CRT matches stock. The rebuild uses GCC
14.2 with `-fno-short-enums`.

Source: `CSC/touch/REPORT.md`.
