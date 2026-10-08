# Filesystem mutex linkage prerequisite — candidate 4083142f

The pinned `bootloader-source-test.elf` is `4083142fce6a0a8ecbc5d3d1a9a224ee475479676d2aa3e8b8bd402ee9144007`. Its global symbols show `opencfw_boot_fs_mutex_acquire = 0x4166ab` and `opencfw_boot_fs_mutex_release = 0x416711` as absolute aliases. It does not export `opencfw_boot_mutex_acquire` or `opencfw_boot_mutex_release`, so the 288-case mutex differential cannot be retargeted to this ELF as-is.

The selected source object was built privately with Cortex-M4 flags at `/tmp/bootloader-mutex-4083142f-m4/mutex.o` (SHA-256 `c7e2c412e5a1096c329dc0e6f011102c1d6712f7a312d055a34d7352fdcb5523`). It exports exactly `opencfw_boot_mutex_acquire` and `opencfw_boot_mutex_release`. Its undefined symbols are:

- `opencfw_bl_queue_is_nonblocking_context`
- `opencfw_bl_kernel_mutex_take_tagged`
- `opencfw_bl_kernel_mutex_take_plain`
- `opencfw_bl_kernel_mutex_give_tagged`
- `opencfw_bl_kernel_queue_put_blocking`

The candidate already defines the context predicate (`opencfw_bl_queue_is_nonblocking_context`, `0x14e7c`) and queue-put implementation (`opencfw_bl_kernel_queue_put_blocking`, `0x14b84`). The queue runtime mode is already source-defined at `0x108dc`, reached through the predicate; do not add `queue_wrappers.o` or `runtime_mode.o`, which would duplicate those symbols and unrelated queue wrappers. The remaining three mutex operations must stay explicit kernel boundaries unless separately recovered: the current standalone mutex linker maps them to stock Thumb entries `0x419e23` (tagged take), `0x41a24f` (plain take), and `0x419de3` (tagged give). Plain release reuses the candidate's queue-put implementation.

The existing standalone comparison was rebuilt and run as Cortex-M4: `verify_mutex.py` PASS, 288 cases, 258 distinct original instruction bytes. Its kernel take/give responses are injected; it does not establish scheduling, blocking-time, ownership, recursion, or priority-inheritance behavior. Replacing the filesystem aliases only after mapping the two source entrypoints to the filesystem ABI is the minimal candidate edit; avoid linking the duplicate queue/runtime objects.
