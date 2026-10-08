# Apollo510 startup leaf correspondence

## Locked input and pinned source family

The stock input is `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`,
SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`,
mapped at `0x410000` in Thumb state. Both extracts below are bound to that
whole-file digest by `stock_extract.py`.

The relevant public-source replay is
`g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/`,
commit `5efc0228528a8adce5eae0d226fac85d2551eb3b` (Apollo510 HAL 5.1.0
lineage, BSD-3-Clause notices retained). I verified that the replay contains
`ambiqhal/mcu/apollo510/hal/am_hal_pwrctrl.c` and `am_hal_adc.h`, but no
`am_hal_adc.c`. Its relevant files are located under
`ambiqhal/mcu/apollo510/hal/`, not at the replay root. It is not the Apollo3/3P
HAL 3.2.0.

## Stock instruction evidence

`0x41583c` is an 8-byte veneer-like setter:

```text
41583c  ldr.w r1, [pc, #1948] ; literal at 0x415fdc
415840  str   r0, [r1]
415842  bx    lr
```

The word at `0x415fdc` is `0x200270cc`. The source candidate
[`native/external_mode_setter.c`](native/external_mode_setter.c) writes its
32-bit argument to that volatile address and returns. It compiles for
Cortex-M55 Thumb with Clang 21 (`-Oz -ffreestanding -fno-builtin`) to:

```text
ldr r1, [pc, #4] ; literal 0x200270cc
str r0, [r1]
bx  lr
nop
.word 0x200270cc
```

The instruction-level register/memory contract matches: input `r0` is stored
to `0x200270cc`, then control returns through `lr`. The generated object is
not byte-identical to the stock range because it uses a nearby literal and
contains alignment padding. This implementation is a bounded native C
candidate; the current verified ledger still labels address `0x41583c` as a
numeric alias, so this report does not claim ledger integration or source
closure.

`0x41ca2c` is 48 bytes. Its extracted Thumb instructions establish this
request/response layout and call contract:

```text
push {r0-r4, lr}; r4 = r0; vstr s0, [sp]
r0 = 2; r1 = 0; r2 = sp; bl 0x41cd1a
if return == 0: out[0] = [sp+4]; out[1] = [sp+8]; return 0
else:           out[0] = 0;      out[1] = 0;      return 1
```

The local request occupies at least 12 bytes: the incoming single-precision
value is stored at offset 0; two response words are consumed at offsets 4 and
8. The branch target is a private stock helper, not an Apollo HAL API. The HAL
header confirms ADC API declarations, but the local replay lacks the ADC
implementation; that supports contextual identification only. No HAL source
match or complete behavioral equivalence is claimed for `0x41ca2c`.

The following remain mapping hypotheses pending stock contract closure:

| Child | Size | Evidence and limit |
|---|---:|---|
| `0x41c4b4` | 810 B | Stock traverses board/OTP/version conditionals, private helpers, and register accesses. Public power-control source/header are relevant references, but no same-signature correspondence is established. |
| `0x41c86c` | 282 B | Stock dispatches operation values through private helpers and status/delay paths. Apollo510 register headers provide context; no aggregate HAL implementation match is established. |
| `0x41ca2c` | 48 B | Exact input/output and call contract above is extracted from stock bytes; relationship to public ADC APIs remains hypothetical. |
| `0x41583c` | 8 B | Native C source candidate and compiled register/memory contract above; still a numeric alias in the current verified ledger. |

Do not count already sourced orchestration/descriptor/selector/clock/mode/
shutdown children again. `0x41583c` was not source-closed in the ledger when
this report was prepared.

## Reproducible checks

```sh
python3 g2/analysis/rescan-2026-10-07/implemented/apollo510-hal/stock_extract.py
python3 g2/analysis/rescan-2026-10-07/implemented/apollo510-hal/verify_setter.py
clang --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -std=c11 -Oz \
  -ffreestanding -fno-builtin -fomit-frame-pointer -c \
  g2/analysis/rescan-2026-10-07/implemented/apollo510-hal/native/external_mode_setter.c \
  -o /tmp/apollo510_external_mode_setter.o
arm-none-eabi-objdump -dr /tmp/apollo510_external_mode_setter.o
```

These checks establish source compilation, stock-image identity, literal
resolution, and the extracted leaf contracts. They do not establish equality
to a private producing source tree, byte equality, or source completeness.
