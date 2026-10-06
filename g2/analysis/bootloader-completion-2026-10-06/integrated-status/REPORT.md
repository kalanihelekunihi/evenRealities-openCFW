# Bootloader functional completion status

The strongest passing source-linked image currently runs reset → scheduler/tasks → source littlefs mount → normal or synthetic update → application reset entry. It is a bounded test ELF, not a complete bootable payload or a byte-identical reconstruction. No stock executable image is loaded on its source side.

## Current functional evidence

- Native NOR read/program/erase, MSPI power/domain control, device configuration and clockgen integration: PASS two reset/update cases, 28,874 distinct original instruction bytes. This result was rerun after the control-request source expansion.
- HAL control requests0–24: PASS1,684 original/source cases, 1,942 instruction bytes, with status/config/handle/MMIO write ordering compared. Requests25–40 still require source closure.
- Native MSPI command-queue implementation: isolated PASS73 cases /808 original instruction bytes. The source emits the exact480-byte scalar resource table at430880 (no executable pointers). Native reset integration is being run.
- Actual scatter→platform configuration: isolated PASS568 original instruction bytes. The initializer already publishes descriptor200001e8 via200004f0;41f846 consumes the four-row configuration table and does not allocate that descriptor. This removes a previous incorrect interpretation; integration still needs the real descriptor callbacks.

The [native provider report](nor-read-followup/REPORT.md) retains detailed transaction and peripheral evidence. Counts overlap and are not completeness percentages. `validation-checkpoint.json` is an older aggregate checkpoint; it does not validate all subsequent source changes.

## Concrete remaining gaps

| Interface/path | Current boundary | Source recovery vs external input |
| --- | --- | --- |
| Real application storage descriptor callbacks430a9c/430ac4/430aec | Success fixture substitutes a descriptor and byte callbacks | Source recoverable; being implemented. Read checks source bounds then copies. Program rounds byte count to words and invokes MRAM while discarding its status. The callback labeled erase only checks a four-byte range and does not erase. |
| Platform initialization41f846 and initializer consumers41f9f8/41fa50 | Source41f846 validated separately, not yet in strongest reset ELF | Initializer and local wrappers available in locked bytes; no hardware blocker. |
| MSPI command queue423f28/423f8e/423fac/423f54 and427xxx | Reviewed source/table ready; native reset comparison pending | Source available; physical queue progress remains an MMIO model. |
| HAL control requests25–40, NOR automatic timing/XIP420002/420890/420c5c | Explicit providers or unexecuted alternatives | Locked instructions and local SDK can recover implementation; physical calibration needs observed peripheral behavior. |
| Accepted-object power configuration422ba8 continuation | Explicit failing provider; real tested startup object is NULL | Recoverable instructions; authentic non-NULL configuration/indirect targets must be established rather than invented. |
| Runtime update41e348, ISR queue/event paths, termination and deferred callbacks | Some direct source tests exist; not fully linked/exercised by reset success test | Source recovery/integration work remains; asynchronous scheduling and exception timing modeled. |
| DFU missing/short/badCRC | Source error routine and guard/MRAM bridge implemented; matched failure profile in progress | Original synthetic missing-file fixture faults in byte-copy415726 before DFU error; exact divergence must be resolved or reported. Source-only success is insufficient. |
| Power interruption/cancellation | No cancellation API established in DFU task; no physical MRAM partial-write model | Software stop/reboot points can be tested. ROM programming atomicity/power-fail effects require ROM evidence or device traces. |
| Resident-ROM program0200ff20 and ROM delay Thumb41 | Bodies absent from locked OTA; source wrappers and public SDK contracts available | SDK can establish call ABI and wrapper semantics, not authenticate absent ROM machine code. ROM dump/trace or documented silicon behavior needed for its actual internals. |
| Complete standalone payload layout, vectors, all callbacks/data and compiler reproduction | Current ELF is relocated source with adapters and explicit numeric aliases | More source closure and image integration needed; exact IAR/layout evidence separately pending. |

## Reproduce and scope

`make -C g2/components/bootloader/thread_creation dfu-storage-power-compatible` builds/runs the focused native NOR/power image. `dfu-storage-queue-compatible` is the next stronger integration target. `completion-regressions` retains the earlier aggregate suite; it is not a hardware-ready payload build.

Source execution uses reconstructed C/assembly plus source-defined scalar tables. Authenticated fixture data currently includes initialSP4B, compressed initializer695B, and application vector8B. The test update is a generated288-byte file, not an official runnable update. NOR ports, peripheral progress, delays, selected mutex/kernel services and application storage remain modeled as documented. A numeric stock-address alias or `nm` with no undefined symbols is not an implemented source dependency.

Bootloader SHA256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`; main OTA SHA256: `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

No commits, staging, firmware flashing, hardware writes or IAR credential use. Physical boot, software/source completeness and byte identity remain separate unproven outcomes.
