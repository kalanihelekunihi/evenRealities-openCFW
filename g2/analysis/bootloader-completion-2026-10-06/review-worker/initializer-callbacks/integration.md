# Initializer callback shared-image integration boundary

This note records the source link inputs and fixtures prepared for the shared
reset-to-callback image. It does not claim a full bootloader source closure,
hardware equivalence, or byte identity. The combined shared-image run remains
the authority for execution coverage and will supersede the separate component
receipts only for the cases it actually reaches.

## Source-owned callback table

`initializer_callbacks/callback_table.S` defines the 32-byte table at
`0x433440`. Its records are `(source callback pointer, priority)`:

| Callback | Stock table entry | Priority |
|---|---:|---:|
| `opencfw_boot_init_callback_platform_sequence` | `0x4301d6` | 1 |
| `opencfw_boot_init_callback_services` | `0x43194c` | 1 |
| `opencfw_boot_init_callback_redirect` | `0x415590` | 25 |
| `opencfw_boot_allocator_init` | `0x41fd70` | 26 |

The source table uses ARM relocations to the compiled source functions. The
locked side keeps its original four pointers. `callback_table.ld` places the
table at `0x433440` and the source-defined 64-byte platform-context records at
`0x433d58`; include its section fragment from the shared linker script.

The new `.boot_context_config` records at `0x433d58`, `0x433d68`, `0x433d78`,
and `0x433d88` each contain four 32-bit values. Those values were read from
the pinned image and are recorded as data in `callback_table.S`, not executable
bytes. The three post-setup config records at `0x433d98`, `0x433da8`, and
`0x433db8` are source ELF data; `integration.py` compares each 16-byte range
against the pinned input and does not overwrite it.

The context rows at `0x20000374` and post-setup rows at `0x20000454` come from
the existing 625-byte authenticated compressed stream expanded to
`0x20000000`. Their pointers select the records above. The integration helper
does not fabricate these RAM rows. The startup profile separately compares the
entire initialized `0x20000000..0x2000055b` region between stock and source.

## Native object set

The callback implementation and required sources are:

| Source | Native body or role |
|---|---|
| `initializer_callbacks/initializer_callbacks.c` | Three callback bodies and service state transitions |
| `initializer_callbacks/mode_register.c` | Mode-register update at stock `0x41d9aa` |
| `initializer_callbacks/platform_bringup.c` | ADC bringup at `0x430000` |
| `initializer_callbacks/post_bringup.c` | Four-row post-setup dispatcher at `0x41f612` |
| `initializer_callbacks/platform_finish.c` | Eight-row platform finish at `0x430502` |
| `initializer_callbacks/callback_table.S` | Relocated callback records and 64 bytes of config data |
| `init_table/init_table.c`, `init_table/qsort.c` | Table runner, comparator, and recovered sorter |
| `clock_manager/clock_class_providers.c` | Source power-register helper at `0x41d92c` |
| `allocator/allocator.c`, `allocator/upstream/tlsf.c`, `filesystem/runtime_memory.c` | Actual priority-26 allocator callback |

The existing callback component uses Cortex-M4 soft-float flags except for
`platform_bringup.c`, which uses FPv4-SP-D16/softfp. The callback and table
source bodies must remain in the source ELF's executable or read-only segments;
the source machine must not map the original callback code as executable donor
bytes.

## Native instruction entries and child cuts

Source and stock native entries are bound by `integration.py`. The core
callback entries are `0x41f9f8` (table default), `0x423d08` (sort), `0x423a48`
(priority comparator), callbacks `0x4301d6`, `0x43194c`, `0x415590`, allocator
`0x41fd70`, mode update `0x41d9aa`, power update `0x41d92c`, ADC body
`0x430000`, post-setup `0x41f612`, and platform finish `0x430502`. Each source
entry must resolve inside a source executable segment. Entry visits are
counted individually; duplicate addresses are not added for an inlined or
absent body.

The following children remain named providers. `integration.py` reuses the
separate component's exact callback leaf semantics and records ordered events;
it does not replace callback entry functions with success returns.

| Child | Stock instruction PC |
|---|---:|
| Descriptor registration | `0x430280` |
| ADC context init/configure/profile/channel/activate | `0x42e8d0`, `0x42eb74`, `0x42f020`, `0x42eaf6`, `0x42ed60` |
| ADC configure/apply/enable/command/enumerate/disable/normalize/reset | `0x42ec0c`, `0x42ea68`, `0x42ebaa`, `0x42eff4`, `0x42ee70`, `0x42ebe2`, `0x42eda0`, `0x42ea32` |
| Generic log | `0x415fae` |
| Post context/config/validate/activate/enable/precommit/finish/record | `0x422ad4`, `0x422ba8`, `0x42308e`, `0x422dc6`, `0x41f512`, `0x41f4f4`, `0x4236ce`, `0x41f8ba` |
| Context claim/config transaction/instance configure/enable/retry/interrupt/NVIC | `0x42c4c6`, `0x42c988`, `0x42cc34`, `0x42c538`, `0x43048e`, `0x42c63a`, `0x430470` |
| Semaphore create; service guard/commit/wake/sleep | `0x416762`; `0x41a684`, `0x4175b4`, `0x41a69a`, `0x41a6a2` |
| Invalid pin configure; mutex create; logger | `0x4174a6`, `0x416610`, `0x4176ce` |

Service-enable `0x417438` and service-configure `0x417510` are conditional
invalid-argument edges, not providers for the valid fixed-table callback path.
The stock bodies execute on stock branches; source invalid-argument handling
remains outside the exercised contract.

## Synthetic inputs and limitations

The callback provider fixture supplies a ready value at `0x40038038`, samples
`0, 0, 3200`, deterministic mutex return addresses (enough for eight platform
rows followed by redirect mutexes), a nonzero semaphore handle, and zero
statuses for successful child calls. These values make deterministic source
and stock tests possible; they do not describe physical ADC readiness, RTOS
mutex allocation, or peripheral timing.

Unicorn cannot execute six stock FP64 instruction slots at `0x430048`,
`0x43004c`, `0x430054`, `0x430058`, `0x43019e`, and `0x4301a2`. The original
machine replaces only those in-memory instructions with NOPs and the hook
emulates their register/store effects; pinned original bytes remain in the
instruction trace. Source code executes its compiled FP32 comparisons and
software conversion logic.

The table callbacks and their native bodies have separate positive
differential coverage. Remaining providers include descriptor registration,
ADC APIs, post APIs, platform HAL operations, service guard/commit/wake/sleep,
mutex, and logger. Peripheral MMIO and ADC values are synthetic. No hardware
reset, scheduler timing, logger formatting, complete source closure, or byte
identity is established by this integration note.

Current integration inputs hash:

| File | SHA256 |
|---|---|
| `initializer_callbacks/integration.py` | `15adf2b507d49a5ecd8d5d9c081ca4ff5ad0d453095bddff0157af6358acc159` |
| `initializer_callbacks/callback_table.S` | `f77a549db497b12c9ccb6a022bbfeb69d13d854464efda383359cb9cbe6a63dd` |
| `initializer_callbacks/callback_table.ld` | `96c755a2e5a192c5748e5a9b9718e33d18bd1f806f19d562efd790ec5fb34af0` |

The helper's `normalize_initializer_event(s)` drops only the descriptor
registrar's caller-saved r2/r3 and the zero-argument service-guard's
caller-saved entry registers. Context-interrupt arguments remain compared.
`split_initializer_native_visits` reports the priority comparator call count
separately because exact comparator invocation count is algorithm-specific;
the sorted callback table remains directly compared.
