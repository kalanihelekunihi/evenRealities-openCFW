# G2 bootloader MX25U25643G address-mode source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated function `[0x00420800,0x0042086C)` is now routed
to compilable clean-room C as `open_cfw_bootloader_mspi_4byte_mode_420800`.
The 108-byte stock body has SHA-256
`717b79259ef6b857ffeb0d87f6488ad7616de5e478960b5f311963b989fc9cee`;
its sole direct caller is the authenticated call at `0x00420926`.

The implementation zero-initializes five bytes, performs the source-routed
one-byte `0x15` read, preserves the stock raw nonzero transport status and
read-failure diagnostic, tests configuration bit 5, returns one when four-byte
addressing is active, and otherwise emits the stock three-byte-mode diagnostic
and returns zero. Host tests pin command, length, initialization, bit decoding,
both diagnostics, and the raw-error quirk.

Apple Clang 21.0.0 emits a relocation-free 124-byte leaf at `0x004375FC`
with SHA-256
`39be5e62d485cd317fc91cb56ead2101d297d71c0e9af887cc33034e81d28979`.
Linux Clang 22.1.8 emits a relocation-free 124-byte leaf at `0x004375EC`
with SHA-256
`d801f6a6a2f483a2fcd48a134d303cb1483dadb52434466ff72efd70051d4599`.
The canonical provider is 161,400 bytes with SHA-256
`51c6301d8f00efa146e7b4b80931429c276277d7e4bacf7345f6ce3b901b2a19`;
the Linux replay is 161,384 bytes with SHA-256
`94907e475bec4511f9478f2f79ed076e1eec750f8bfc96bd2f8c2e2db39b768f`.

No hardware operation was performed. Live command/register semantics, MSPI
transport, external-flash behavior, and cold boot remain explicitly blocked by
the absence of an authorized responsive right-temple G2. Executable bodies at
and after `0x0042086C` remain software gaps, so this is not a functional
completeness claim.
