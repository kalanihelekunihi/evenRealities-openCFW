# Full flash interface initializer

Candidate source at runtime_gx8002_flash_interface_initialize.c reconstructs
package0x16450/runtime0x1002443c. It compiles to428/436 bytes. Both original
and source use48-byte frames:20 saved-register bytes plus28 local bytes.

Full decoded comparison passes35,328 cases across all256 status bytes, the
named device families, discovery success/failure and two caller-clobber seeds.
Checks include initial zero configuration, ordered controller setup, IRQ15
registration, conditional profile initialization, single/pair quad paths,
C22017 status-bit6 command sequence, callback writes, all nine XIP arguments,
return values and preserved registers. Separate dispatch qualification covers
4150 identifiers, including adjacent values and signed boundaries. Five
rejection tests check frames, saved-register writes, XIP initialization,
command buffer pointer and unknown helper calls.

The initializer keeps the selected ID across configuration calls; the resume
initializer instead reloads it. That distinction is preserved. Helpers are
modeled as returning services and caller-clobbering their ABI registers; this
is not whole-device runtime qualification. Interface table/BSS ownership,
physical startup and the IRQ signature provenance integration rebuild remain
outstanding. Candidate admission adapter and package integration are next.

Now integrated through the reviewed admission adapter. Native macOS codec
build passes164 tests and revalidates corrected IRQ signature provenance.
Full package assembly and artifact verification pass. This replaces436
retained bytes with428 compiled bytes and eight fill bytes. Full hardware
startup and interface/device-table/BSS ownership remain unqualified.
