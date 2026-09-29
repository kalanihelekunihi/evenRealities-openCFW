# G2 documentation

The active procedure is in [`../workflow/README.md`](../workflow/README.md).
Look up facts here first. Hardware, regulatory and datasheet material that
applies to more than one device is in [`../../docs/hardware/`](../../docs/hardware/README.md).

| Document | Contents |
| --- | --- |
| [`reference/firmware-formats.md`](reference/firmware-formats.md) | EVENOTA container, component headers, CRC variants, main/case/touch/codec wrappers, EM9305 record package, payload identities |
| [`reference/memory-map.md`](reference/memory-map.md) | Apollo510B MRAM/TCM/SRAM/NOR, bootloader, EM9305, GX8002, touch and case memory maps |
| [`reference/toolchains.md`](reference/toolchains.md) | original compiler and runtime per payload; open questions blocking byte equality |
| [`reference/libraries.md`](reference/libraries.md) | identified upstream libraries, versions, commits, recovered configuration, submodule mapping |
| [`reference/protocols.md`](reference/protocols.md) | phone transport, protobuf services, EFS/OTA, case UART, codec, touch, HCI, TinyFrame, ring link |
| [`reference/decompilation-status.md`](reference/decompilation-status.md) | open-tool decompilation runs per payload, coverage and findings |
| [`reference/capabilities.md`](reference/capabilities.md) | capability checklist with stock address ranges, used to check pseudocode review coverage |
| [`reference/hardware-validation-notes.md`](reference/hardware-validation-notes.md) | on-device observations, flashing and recovery notes, safety cautions |
| [`../symbols/README.md`](../symbols/README.md) | address-keyed naming seeds per payload |
| [`../config-recovered/README.md`](../config-recovered/README.md) | recovered upstream configuration headers and patches |

Per-closure research records, progress logs and coverage ledgers from the
retired hybrid-overlay campaign were removed on 2026-09-29. The reference
documents cite them by path at commit `832137ec`, where
`git show 832137ec:<path>` still shows them.
