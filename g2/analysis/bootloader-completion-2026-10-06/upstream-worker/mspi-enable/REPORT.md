# Stock MSPI enable leaf

`am_hal_mspi_enable.c` is a readable reconstruction of the locked bootloader's
138-byte function at `0x00425066..0x004250f0`. It is grounded in the
authenticated `g2-2.2.6.10/ota_s200_bootloader.bin` image (SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`); the
function bytes hash to
`3e8eafec68e5f33ec128fd64c1386692323e9b175993c267d6a2bb7ec3ac155c`, matching
the exact symbol interval in `g2/symbols/bootloader.tsv`. Raw Thumb
disassembly and literal-pool reads are recorded in `stock-disassembly.txt`.

The function validates a non-NULL handle and the masked prefix
`(word0 & 0x01ffffff) == 0x01bebebe`, returning2 on failure. It returns7 if
the configured byte at handle+8 is zero. With nonzero queue context at+0x18,
it clears words at+0x1c and+0x20, calls
`mspi_cq_init(module@+4, word@+0x14, queue_context@+0x18)`, writes
`0x00400080` to `0x40060000 + module*0x1000 + 0x2b4`, then resets the following
per-handle fields:

| Offset | Store |
|---:|---|
| `0x82c` | byte `0` |
| `0x82d` | byte `1` |
| `0x830` | word `0` |
| `0x838` | word `0` |
| `0x83c` | byte `0` |
| `0x840` | word `0` |
| `0x844` | word `0` |
| `0x854` | word `0` |
| `0x85c` | word `0` |

Whether or not queue context is present, it ORs enable bit25 into word0 and
returns0. The source uses the existing sparse compatibility type only for the
already recovered state extent and asserted `pTCB` / CQ-counter offsets. New
field meanings remain opaque; their names in C denote recovered byte offsets,
not claims about the full HAL state model. Handle+0x14 is passed through to the
queue initializer without interpretation.

## Build and source/original check

`make` builds an ARM Cortex-M55/Thumb/soft-float ELF. `make
PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python test` executes the
original body from the authenticated blob against the compiled source in
Unicorn. The test intercepts only `mspi_cq_init`, recording its three arguments
while implementing no queue behavior. Synthetic RAM stands in for the MSPI
register window.

Result: PASS, nine cases, all138 distinct stock instruction bytes reached.
Cases cover null/invalid/uninitialized/unconfigured handles, configured
handles with and without queue context, already-enabled state, modules0..2,
and distinct queue-argument/context values. For every case the test compares
return value, provider calls, the entire0x8d0-byte state view, and the full
0x4000-byte synthetic MSPI window. Held-out evidence is `out/comparison.json`.

This closes the source body for `am_hal_mspi_enable` and leaves one explicit
provider boundary: `mspi_cq_init` at stock address `0x00423f28`. The provider's
work, physical CQ state, real MMIO, timing, startup, and whole-image rebuild
are outside this test. This does not claim byte-identical compiled code.
