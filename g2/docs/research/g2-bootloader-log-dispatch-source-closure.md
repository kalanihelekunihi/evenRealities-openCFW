# G2 bootloader logging-dispatch source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

The aggregate identities below are the logging-dispatch promotion checkpoint;
the later substring-search promotion supersedes them. Current aggregate pins
are in `g2-bootloader-strstr-source-closure.md`.

## Authenticated stock boundary

The S200 bootloader function at `[0x00415FAE,0x00415FDA)` is 44 bytes with
SHA-256 `4dd35a80dd88663be85e71c3b7e3bf5409c1e4e2150ec3fd1d66133b6d2ad0ea`.
A whole-image Thumb-call scan finds 57 direct callers. The function reads the
callback word at `0x200270CC`; a null callback returns zero without formatting.
Otherwise it passes the fixed context at `0x20024CD0`, the format string, and
the raw AAPCS variadic cursor to the formatter at `0x00415BF6`, reloads the
callback after formatting, invokes it with the fixed context, and returns the
formatter count. The reload is observable behavior and is covered by a test
that changes the callback during formatting.

The words at `[0x00415FDA,0x00415FF4)` are literal-pool/data entries used by
this logging cluster, not part of the replaced executable body. They remain
authenticated official bytes.

## Compilable source and production route

`components/bootloader/core_overlay/runtime_log_dispatch.c` is a freestanding
clean-room C implementation of that contract. Host tests cover the null
short-circuit, fixed context, variadic cursor forwarding, return value, handler
invocation, and post-format handler reload. An isolated Cortex-M55 compile is
also required.

The Apple Clang 21 leaf is 60 bytes at overlay offset 2,824/runtime
`0x00434F80`, with final SHA-256
`1921c9add6eed99c1e44847059898c6780b92a3e36fa654221f125bfa1e0fde5`
and unrelocated SHA-256
`1c131865831ebb63012868697aa0337598712d770513bfc6dc7ea949893a9943`.
Its sole strict relocation is an `R_ARM_THM_CALL` at leaf offset 26 to
`open_cfw_bootloader_format_core`. The stock body is replaced by
`1ef0e7bf` followed by twenty Thumb NOPs. The independent Homebrew Clang
22.1.8 leaf has the same raw bytes and size, is placed at offset 2,816, and has
final SHA-256
`3d2dbd29118802e8d28c4a445aa66ead3429ea324e4778d8b0e82b15f633ff36`.

The canonical bootloader provider is 151,484 bytes with SHA-256
`1900350a9485344c10d4038b158e06caeb4720e2f57dc33ce33abffc4cdc8b99`.
It accounts for 2,877 source-owned bytes, 3,394 generated patch bytes, eight
alignment bytes, and 145,205 byte-identical authenticated official bytes. The
overlay ends at `0x00434FBC`, leaving 12,356 bytes before the protected main
image boundary.

The canonical unsigned package is 4,733,062 bytes with SHA-256
`c041de99fdd608b08e78aa98fcc4108f00816b2265d86086dec23691cf31c44d`;
its flash plan contains 6,240 placed regions, two unresolved physical-only
regions, five container-only regions, and six protected regions. The Linux
profile package is 4,509,064 bytes with SHA-256
`0dd0f069832e22dff07b48e2ebeb57e2c514843a200a35fd850aaaa51aa613f5`.

## Physical evidence block

No signing, transmission, flashing, erasing, or reset was performed. Runtime
validation requires an authorized responsive G2 right temple demonstrating
boot progression and emitted logging through one or more authenticated caller
paths. The available authorized right temple is nonresponsive and the left
temple is intentionally retained on stock firmware, so physical validation is
explicitly blocked. This tranche therefore does not establish total firmware
functional completeness.
