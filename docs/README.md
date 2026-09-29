# Documentation

Cross-device material lives here. Everything specific to one device lives with
that device.

| Document | Read it when |
| --- | --- |
| [`roadmap.md`](roadmap.md) | you want the phased plan from full decompilation to byte-identical C, and the list of shortcuts |
| [`tooling.md`](tooling.md) | you are setting up decompilation, byte-matching, emulation or debug tools |
| [`tooling-availability.md`](tooling-availability.md) | you need to know whether a compiler, SDK or tool is public, needs an account, or costs money |
| [`hardware/README.md`](hardware/README.md) | you need a part number, bus, pin, data rate, protocol, FCC record or datasheet |
| [`build.md`](build.md) | you are running a target or a gate failed |
| [`methodology.md`](methodology.md) | you want to know what "verified" means here |
| [`repository-layout.md`](repository-layout.md) | you need to decide where new work belongs |

## Hardware — [`hardware/`](hardware)

| Document | Contents |
| --- | --- |
| [`hardware/g2-glasses.md`](hardware/g2-glasses.md) | G2 system overview, IC table, buses and pads, inter-processor links, display, audio and power |
| [`hardware/g2-case.md`](hardware/g2-case.md) | charging case MCU, power parts, UART framing, dual-bank update |
| [`hardware/r1-ring.md`](hardware/r1-ring.md) | R1 pin and bus map, sensors, PMIC single-wire link, NFC charging |
| [`hardware/regulatory.md`](hardware/regulatory.md) | FCC IDs (grantee 2BFKR), exhibits, RF test data, ISED and Japan numbers |
| [`hardware/components/`](hardware/components) | one page per identified IC: datasheet links, key specs, SVD source |
| [`hardware/sources.md`](hardware/sources.md) | bibliography |

## G2

The active procedure is [`../g2/workflow/README.md`](../g2/workflow/README.md).
The fact references are indexed in [`../g2/docs/README.md`](../g2/docs/README.md):
formats, memory map, toolchains, libraries, protocols and the capability
checklist. Naming seeds are in [`../g2/symbols/`](../g2/symbols/README.md) and
recovered upstream configuration is in
[`../g2/config-recovered/`](../g2/config-recovered/README.md).

## R1

Start at [`../r1/README.md`](../r1/README.md) and the index in
[`../r1/docs/README.md`](../r1/docs/README.md): memory map, toolchain and
dependencies, protocol, storage formats, pinout, and security and bootloader.
Configuration seeds are in [`../r1/config-recovered/`](../r1/config-recovered/README.md).

## Dependencies

[`../third-party/README.md`](../third-party/README.md) is the registry of every
pinned upstream: submodules, fetched archives, licensed tools, and the pending
G2 emulator.
