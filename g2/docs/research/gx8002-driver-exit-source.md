# GX8002 driver-exit reconstruction

`runtime_gx8002_driver_exit.c` reconstructs observed firmware control flow.
Authenticated NationalChip driver objects at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` identify helper symbols and
relocations. Those objects are only identity/comparison evidence. The linked
candidate contains only the newly compiled C object; it does not pull bytes
from the SDK objects. The IRQ declarations are exact upstream header excerpts.

`gx_snpu_exit` at `0x10205d40` / package `0xf2cc` occupies 32 bytes,
exactly matching stock. It masks IRQ12, calls SNPU suspend, saves the result,
unmasks IRQ12, calls device exit only for a zero result, and returns the saved
result. Its frame is eight bytes. Preserving this order matters: unmasking
occurs even when suspend fails, and the device-exit result is ignored.

`gx_audio_in_exit` at `0x10204984` / package `0xdf10` uses 42 of 44 bytes.
It calls audio reset, then the independently source-qualified clock gate with
module/enable pairs (3,0), (2,0), (8,0), (7,0), and returns zero. Frame: four
bytes. Internal helper declarations express the observed call contract;
they are not claimed to reconstruct original private C prototypes.

Decoded candidate and stock instructions match an independent call-sequence,
return and frame oracle in 3,384 cases. Register seeds and suspend results
include high-bit and negative encodings; all caller-saved registers are
clobbered at helper boundaries. Eight regression tests cover successful and
failed suspension, return preservation, IRQ number, branch target, gate
selection, and frame restoration.

The IRQ wrappers, suspend/device-exit and audio-reset bodies remain retained.
No physical hardware or asynchronous timing qualification is claimed. These
routines and audio reset are now registered in the integrated codec builder;
all 375 integration tests pass.

```sh
python3 g2/tools/verify_gx8002_driver_exit.py
python3 -m unittest discover -s g2/tests -p test_gx8002_driver_exit.py
```

Evidence: [gx8002-driver-exit-verification.json](gx8002-driver-exit-verification.json)
and [gx8002-driver-exit-identification.json](gx8002-driver-exit-identification.json).

Next implementation candidate: `runtime_gx8002_audio_reset.c` reconstructs
`_ain_reset` as individually ordered volatile 32-bit register accesses.
Authenticated SDK section `.text._ain_reset` is 320 bytes and matches stock
at package `0xd214` / runtime `0x10203c88` exactly, with no relocations.
See `gx8002-audio-reset-identification.json` and
`build/gx8002-board/audio-reset-oracle.disassembly.txt`.
The C object builds to 240 text bytes with native C-SKY GCC and the usual
`-Os` flags. It is not linked, qualified or integrated yet. Build a reproducible
candidate linker/verifier next. Check every read/modify/write independently,
including changes in register values between reads; verify bit8 polling at
`0xa0a00104`, delayed completion, and nontermination prefixes. Do not replace
the original unbounded hardware wait with a timeout. The driver-exit candidate
now declares this reset helper's observed integer return correctly and ignores
it as stock does; its qualification was rerun after that declaration change.

The audio-reset candidate described above has since been linked, qualified
and integrated. See gx8002-audio-reset-source.md for the current evidence.
