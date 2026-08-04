# AmbiqSuite 5.1.0 Apollo510 source closure

This subtree contains the unmodified public Apollo510 source/header closure
needed to compile `am_hal_mspi.c` from
[`AmbiqMicro/ambiqhal_ambiq`](https://github.com/AmbiqMicro/ambiqhal_ambiq)
at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. That commit imports the
Apollo510 HAL from AmbiqSuite SDK 5.1.0 and declares BSD-3-Clause licensing.

The snapshot is deliberately dependency-minimal rather than a full SDK:

- the complete, unmodified `mcu/apollo510/hal/mcu/am_hal_mspi.c`
  translation unit;
- the Apollo510 HAL and register headers reached while compiling that unit;
- the Ambiq CMSIS device and system headers; and
- the SDK version header.

No proprietary prebuilt library, board support package, programmer, binary
firmware, or hardware operation is included. The standard Arm CMSIS Core
headers are kept in the sibling `third_party/cmsis-core` snapshot.

OpenCFW compiles the complete Ambiq translation unit with function/data
sections. A section-garbage-collection proof roots only
`am_hal_mspi_interrupt_clear` and verifies a 48-byte linked leaf with no
undefined symbol, private state, data dependency, or text relocation. This
avoids copying Ambiq's private MSPI handle layout into handwritten source.

The exact file inventory, sizes, Git blob identities, and SHA-256 values are
recorded in `PROVENANCE.json` and checked offline by `verify_snapshot.py`.
This source snapshot does not itself authorize a flash, program, erase, or
MSPI transaction.

## License

The imported Ambiq files retain their complete BSD-3-Clause notices. The
license text is reproduced in `LICENSE`.
