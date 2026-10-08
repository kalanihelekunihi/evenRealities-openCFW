# Source-image provider checklist

Mode publication41fadc now has native source and563 isolated tests; it is linked in the current candidate image under test.

This lists every current numerical linker binding, including duplicate names for a shared address. It is a dependency checklist, not proof each path is executed. Source may exist without being linked; a numerical alias never counts as source closure.

| Binding | Address | Boundary |
| --- | --- | --- |
| `opencfw_boot_platform_terminal` | `0x4329c5` | Terminal/task lifecycle path; source integration remains |
| `opencfw_provider_41f9f8` | `0x41f9f9` | Initializer runner/sorter source work active; not yet linked |
| `opencfw_provider_41fa50` | `0x41fa51` | Platform startup orchestration41fa50 and callees; not reconstructed/shared linked |
| `opencfw_provider_41ba80` | `0x41ba81` | Recovered runtime/platform candidates; bind exact ABI and validate |
| `opencfw_provider_415fae` | `0x415faf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_fs_mutex_acquire` | `0x4166ab` | Filesystem mutex currently intercepted; underlying source integration needed |
| `opencfw_boot_fs_mutex_release` | `0x416711` | Filesystem mutex currently intercepted; underlying source integration needed |
| `opencfw_boot_allocator_log` | `0x08002101` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `printf` | `0x08002111` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_provider_4176ce` | `0x4176cf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_bl_task_return` | `0x41b391` | Terminal/task lifecycle path; source integration remains |
| `opencfw_bl_stack_overflow` | `0x41b601` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_provider_4201ba` | `0x4201bb` | NOR timing/XIP provider; source recovery active |
| `opencfw_provider_420890` | `0x420891` | NOR timing/XIP provider; source recovery active |
| `opencfw_provider_420c5c` | `0x420c5d` | NOR timing/XIP provider; source recovery active |
| `opencfw_bl_status_transfer_error` | `0x415faf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_bl_log` | `0x4176cf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_bl_transfer_error` | `0x415faf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_provider_416200` | `0x416201` | Terminal/task lifecycle path; source integration remains |
| `opencfw_boot_dfu_log` | `0x08002121` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_bl_kernel_queue_put_from_isr` | `0x41a025` | ISR queue/notification/event integration remains |
| `opencfw_bl_kernel_queue_get_from_isr` | `0x41a3b1` | ISR queue/notification/event integration remains |
| `opencfw_bl_malloc_failed` | `0x41b5f7` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_dfu_terminal` | `0x42e1db` | Terminal/task lifecycle path; source integration remains |
| `opencfw_boot_log` | `0x4176cf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_isr_thread_notify` | `0x418fe9` | ISR queue/notification/event integration remains |
| `opencfw_bl_event_flags_set_isr` | `0x419bd3` | ISR queue/notification/event integration remains |
| `opencfw_boot_control_log` | `0x08002131` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_control_power_apply_configure` | `0x08002211` | Accepted non-NULL power configuration422ba8; explicit failing fixture |
| `opencfw_boot_fs_error` | `0x415faf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_bl_kernel_state` | `0x416089` | Recovered runtime/platform candidates; bind exact ABI and validate |
| `opencfw_bl_task_delay` | `0x416379` | Recovered runtime/platform candidates; bind exact ABI and validate |
| `opencfw_hal_mspi_control_unrecovered_request` | `0x08002221` | HAL30/34 remain;26/27/29 newly routed and direct-tested172 cases, shared-image verification underway |
| `opencfw_bl_printf` | `0x415faf` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_power_special_mode` | `0x41bae9` | Logging/error/fatal or runtime fixture/alternative; resolve exact original behavior before source closure |
| `opencfw_boot_rom_mram_program` | `0x0200ff21` | Resident ROM outside OTA; source caller can be closed, ROM internals need external evidence |
| `opencfw_boot_rom48` | `0x00000049` | Resident ROM outside OTA; source caller can be closed, ROM internals need external evidence |
| `opencfw_boot_rom_delay_cycles` | `0x00000041` | Resident ROM outside OTA; source caller can be closed, ROM internals need external evidence |

Also unfinished: full vectors, initializer/assets/data source definition, initializer callbacks4301d6/43194c/415590, asynchronous termination/deferred runtime integration, complete payload layout and exact compiler reproduction. These are source/build work rather than inherent hardware blockers. Physical IRQ/cache/peripheral timing, actual partial-ROM-write recovery and hardware boot require suitable external evidence; no device operations were performed.
