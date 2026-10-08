# Runtime action: release-storage allocator closure

This isolated fixture joins the source ownership logic at `418ae8` with the
already reconstructed RTOS heap implementation. It runs the stock release
body plus stock allocator on one side and `opencfw_boot_thread_release_storage`
plus `opencfw_bl_rtos_free` / `opencfw_bl_rtos_allocate` on the source side.

`make test` uses a synthetic but structurally valid initialized heap. For
ownership flag 0 it allocates both stack and TCB from the heap; flag 1 allocates
only the TCB and points to an external static stack; flag 2 uses external
static TCB and stack storage. It compares allocator return addresses, all
81,920 heap bytes, allocator globals, scheduler suspend/resume counts, and
post-release TCB/stack contents.

This is a direct source/stock test profile, not a firmware integration. Heap
memory is synthetic and scheduler suspend/resume are no-op providers. It does
not test heap exhaustion, invalid or repeated frees, concurrency, or hardware.

The standalone ELF, three objects, copied inputs, test receipt and freeze
manifest are preserved under the ignored path
`g2/build/bootloader-completion/runtime-action-allocator/addon/`. The rebuilt
ELF hash is `fdbf915b9a4c4182e66de2d265bc3478bfcc74b01f52b21646fe9682cfdd1943`,
matching the previously tested add-on.

The same fixture is also run against the immutable whole-runtime successor
ELF using [verify_integrated.py](verify_integrated.py). Its receipt is
[comparison-whole-runtime.json](comparison-whole-runtime.json). The candidate
hash is `602cccc4975862a379b89d5747df0b5f8cc5b2cd56e808c5e78482ee6ebf0210`;
the exact candidate copy and receipt inputs are frozen under
`g2/build/bootloader-completion/runtime-action-allocator/whole-runtime/`.
The fixed RTOS arena `[0x2000055c,0x2001455c)` is 81,920 bytes and does not
overlap candidate PT_LOAD memory. The candidate's `.boot_iom_context_pool`
begins at the arena's exclusive end. Its allocator performs RTOS heap
initialization inline; the separate TLSF/source allocator initializer is not
part of this fixture.
