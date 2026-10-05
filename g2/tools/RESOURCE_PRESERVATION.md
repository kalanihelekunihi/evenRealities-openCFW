# Optional local L8 resource preservation

`make -C g2 resource-export resource-verify resource-repack` uses the six
authenticated L8 descriptors from the shortcut batch. It requires an authorized
local original Apollo payload at `RESOURCE_PAYLOAD` and fails closed if missing
or mismatched. It exports exact `.l8` pixels, standalone binary grayscale PGM
images and provenance into ignored `RESOURCE_DIR` (default `build/resources/l8`).
`RESOURCE_REPACK` is a new output file; the original input is never overwritten.

The repack path accepts only original pixel identities, rechecks descriptor
geometry/pointers and reconstructs the identical original Apollo payload. It
does not insert modified artwork, build an EVENOTA bundle, change official
manifest providers or establish source reconstruction. PGM is an inspection
format, not a target decoder input. Root MIT covers the tool, not the extracted
vendor pixels; their redistribution permission is not established (root NOTICE).

Export and repack refuse existing outputs. If a filesystem failure interrupts
the transfer into a newly created export directory, a partial directory may
remain; verification rejects incomplete output. Use a new destination for retry
and inspect partial output before any cleanup. No automatic cleanup removes
preexisting output or unrelated files.

Run `make -C g2 foundation-test` for synthetic resource rejection/roundtrip and
host/ARM compilation checks of the callback-based touch SCB component. The tool
also offers `make -C g2 foundation-object` to compile a reusable Cortex-M0+
freestanding object into ignored `build/foundation/`; no firmware link is added.
The resource path
requires only the Python standard library; it does not initialize upstreams or
fetch firmware. The map is hash-pinned and contains addresses/checksums, not
vendor pixel data. Six proven assets are supported; other formats, font/NOR
resources and the 422 unresolved candidates are excluded.
