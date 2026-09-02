# G2 bootloader `memmove` source closure at `0x004276BC`

## Result

The complete authenticated bootloader body `[0x004276BC,0x00427752)` is an
overlap-safe byte move and is now production-routed to reviewable MIT C. The
following `[0x00427752,0x00427754)` halfword is zero alignment, not part of the
function. This is a software-only admission; no target hardware was accessed.

## Authenticated boundaries and topology

- Stock body: 150 bytes, SHA-256
  `7ef3c825f46fa907a46b09880629b6ae49eace45319bd4beb74b9ff70d136137`.
- Alignment halfword: `0000`, SHA-256
  `96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7`.
- The sole direct caller is `0x0042395A`, in the production front-rotation
  path, and no interior halfword has a direct caller or stored entry pointer.
- The entry compares unsigned source and destination addresses. A destructive
  overlap selects the backward loop; all other cases select the forward path.
  The non-overlap entry path tail-branches at body offset `0x08` to the
  source-owned byte-copy provider at `0x0041568C`.
- Apollo-main has an independent 150-byte analogue at `0x00439710`, SHA-256
  `31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28`.
  It is identical in 146 of 150 bytes. Its only difference run is the
  address-coupled wide branch to its local copy provider at `0x00439BE4`.

## Production realization

`runtime_memmove_4276bc.c` implements the recovered three-argument ABI using
unsigned integer address comparison, a backward byte loop for destructive
overlap, a forward byte loop otherwise, and returns the original destination.
It contains no inline assembly or raw executable encoding.

Both reviewed compiler profiles emit the same 50-byte, relocation-free leaf:

- Apple clang 21.0.0: SHA-256
  `22a53bbac7dcb82baafe7b2907d4d94b2e4135eccb0395c9b83e37dbf79916db`.
- Homebrew clang 22.1.8: the same size and digest.

The leaf occupies reclaimed stock body space at `[0x004276C0,0x004276F2)`.
The generated entry redirect occupies four bytes and the remaining 96 bytes
are deterministic NOP fill. Host tests cover backward overlap, forward
overlap, non-overlap, aliasing, zero length, destination return, and source
reviewability.

## Hardware boundary

Target execution, timing, cache/bus interaction, and the production caller on
physical G2 hardware are **blocked by unavailable physical evidence**. No
flash, signing, reset, live MMIO, or hardware mutation was performed.
