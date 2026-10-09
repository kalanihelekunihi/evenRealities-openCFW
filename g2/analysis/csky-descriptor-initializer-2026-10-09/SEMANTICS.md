# Initializer instruction semantics and caller contract

Pinned operational decoder sources resolve the two model operations:

- `third-party/tools/ghidra-csky/C-SKY/data/languages/32b_dsp.sinc:43–46`,
  SHA-256 `be0cd035c6574e0fddcac4d0740367b67bd4921e0033bea21e580f5e9484e490`,
  defines MULA.32.L as destination plus unsigned 64-bit product, truncated to
  the low 32 bits. Thus r13 becomes `row*144 + slot*12` here.
- `32b_branch.sinc:24–26`, SHA-256
  `0dfe9d60290555f94f2cc1496ad07d7ddf2f7c2d96bf6e145ea86906c80df49b`,
  subtracts one from BNEZAD's register before testing for nonzero. Starting r18
  at eight therefore produces eight inner iterations, not nine.
- Primary Linux C-SKY ABI assembly in
  `https://raw.githubusercontent.com/torvalds/linux/master/arch/csky/abiv2/sysdep.h`
  independently corroborates the decrement-branch equivalence: CK860 uses
  BNEZAD directly; other paths expand it to SUBI one followed by BNEZ. This
  does not establish CK804 physical instruction support/execution.

These are source-grounded software semantics, not an executed target trace.
The existing 2014 ISA PDF is pinned, but the earlier recovery notes report no
BNEZAD entry. Local PDF extraction tools were unavailable in this follow-up;
no new PDF-content claim is made. Discovery can supply the official CK804 DSP
instruction manual covering MULA.32.L and the v2 BNEZAD instruction definition
for a stronger manufacturer-document cross-check. Local SLEIGH definitions are
an operational reference and must not be mislabeled as that manufacturer manual.

## Observed machine ABI

The body reads no incoming argument register before defining its own working
values. It never adjusts SP, touches r4–r11/r16–r17 or changes LR; it has no
calls and returns with JMP r15. It clobbers r0–r3/r12–r13/r18–r25 and comparison
condition state. These effects agree with the generic cspec's preserved set,
but do not authenticate a source signature. In particular r0 ends at eight;
that residual value must not be named a success return.

The observed caller at `0x10205CF4` saves r4/r5/LR. Before BSR `0x10205D20`
it sets global fields `+0x5C4=0xA0C00000`, `+0x5C8=0xA0300000`,
`+0x5CC=0xA0C00190`, and clears `+0x5B4/+0x5B0` with r5=0. No caller argument
is consumed by the initializer. After return it uses preserved r5 as r1,
overwrites r0 with callback address `0x10205CE0`, calls `0x102055B0`, sets the
global state word to two and explicitly returns r5 (zero). The initializer's
r0 residue is not consumed by this caller. It touches the table's first 1440
bytes, leaving the nearby fields at `+0x5B0` and above outside its stores.

This closes the local caller register contract and software loop model.
Physical memory identity, mapping activation, callback-registration semantics,
global source-level type and formal campaign review/admission remain open.

## Additive manufacturer-manual correction

Discovery's `CSKY-DESCRIPTOR-REFERENCES.md` supplies official ABI documents
at `9f7121f7d40970ba5cc0f15716da033db2bb9d07`, plus the manufacturer-origin
E804 manual already present in the registered decoder dependency. Its exact
manufacturer distribution URL is unverified; translations are not official
English editions. E804 manual section14.25 states
BNEZAD decrements unconditionally and branches if the result is greater than
zero. The local decoder's general nonzero condition is therefore broader than
this manufacturer definition. The initializer's positive countdown8..0 is
unchanged under both models; no generalized nonzero semantics should be
exported from this packet. MULA.32.L section14.93 corroborates low32
multiply-add. Official V2 ABI preserves r4–r11/r16–r17/SP/LR and requires
8-byte stack alignment, consistent with the observed unchanged-SP body.

This manufacturer-origin formula supersedes the generic branch wording above where
it differs. E804 documentation does not prove every CK803/CK804 variant or
physical target configuration; the discovery report retains that uncertainty.
Twelve bytes is descriptor stride, not a proven complete source structure size.
