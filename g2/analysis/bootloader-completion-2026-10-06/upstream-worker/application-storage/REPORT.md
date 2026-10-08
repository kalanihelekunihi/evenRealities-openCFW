# Application-storage descriptor callbacks

The stock scatter startup publishes the 64-byte descriptor at `0x200001e8`.
Its callback fields remain Thumb pointers `0x430a9d`, `0x430ac5`, and
`0x430aed`. `storage_callback_veneers.S` keeps those exact entry addresses and
branches to readable C implementations at `0x430a9c`, `0x430ac4`, and
`0x430aec`.

The source interfaces are in `g2/components/bootloader/application_storage/`:

* `opencfw_boot_storage_read_impl(dst, src, size)` validates the source range,
  copies bytes, and returns `0`; validation failure returns `UINT32_MAX`.
* `opencfw_boot_storage_program_impl(dst, src, size)` validates the destination,
  rounds size to 32-bit words, saves/restores PRIMASK, and invokes the existing
  MRAM bridge with key `0x12344321`. It ignores the MRAM status and returns `0`
  for any range that passes its first validation.
* `opencfw_boot_storage_erase_validate_impl(address)` validates four bytes and
  returns `0` or `UINT32_MAX`. The descriptor's `+0x20` callback does not erase.

The validator caches a mode-selected size limit at `0x200270c8`. Mode comes
from selector-1 device info record's word 11. A cache miss now calls
`opencfw_boot_device_info_query(1, temporary_record)`, executing the source
`0x41d792` dispatcher and full `0x41d294` snapshot before storing that word.
The snapshot selects bits `[3:2]` of `0x40020014`; the halfword table at
`0x43401c` yields 1, 2, 3, or 4 MiB after shifting by 10. The stock comparison accepts only an
address at or above `0x4000` and a size strictly below this limit. It computes
32-bit `address + size - 1` but discards the result, so it does not bound the
end address. The MRAM provider may reject a destination later; that status is
ignored by the descriptor callback.

The earlier 19-case callback receipt in `out/comparison.json` predates the
cache-miss source change above and must not be cited as a test of the current
`storage_callbacks.c` hash. The current cache-miss behavior is tested directly
by the separate `device-info-dispatch/` profile, which compares original
`0x430a60` with source `opencfw_boot_storage_range_valid` over 112 cache/mode/
address/size fixtures, including the live selector-1 query and its 10 delay
callbacks.

The earlier callback test runs stock and compiled source through the actual startup/scatter
path, reads the callback pointers from the resulting descriptor, and invokes
those pointers. `make verify PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python`
passed 19 cases and compared 976 distinct stock instruction bytes for its then-current source revision. Cases cover
all four size modes, threshold boundaries, copy, zero size, exact size limits,
word alignment, and MRAM success/error returns. The focused Cortex-M4 profile
executes source code and stock bridge cleanup in Unicorn with synthetic RAM and
MMIO. For stock-only execution, `0x41d792` is cut to populate only the stack
field at `+0x2c` consumed by the range helper, using the mapped register and
table; its other status fields and delay effects are not reproduced. The source
path computes that selected field directly. The test also links fixture power
providers but asserts neither is called. The ROM service at `0x0200ff20` is
stubbed with controlled status. No physical MRAM access, power acknowledgement,
or timing behavior is established.

For source linkage, include `storage_callbacks.c` and
`storage_callback_veneers.S`; provide the existing `opencfw_boot_control_critical_save`
and `opencfw_boot_mram_dispatch` symbols from platform-control/MRAM providers.
The updated callback also requires `device_info_dispatch.c`, `device_info.c`,
and the native mode-0 plus selector-gate providers. The build recipe and exact
earlier source/ELF/image hashes are recorded in
`out/comparison.json`. This bounded provider does not establish whole-image
source completion or byte identity.
