# Third-party gap audit and new Ambiq Zephyr reference

2026-10-09. Exclusive worker output; no firmware sources, canonical coverage, shared index, submodule pins, staging, or existing evidence changed. Workflow README, PROCEDURE, CONTRACTS and REPOSITORY read fully. This is P2 source inference support, not C reconstruction or a completeness gate.

## New retained reference

Official repository `https://github.com/AmbiqMicro/ambiqzephyr`, branch `ambiq-stable`, exact inspected revision `2e3474150a431d255394521b4da3fb149f3b4052`. Read-only GitHub commit/tree APIs verified revision and paths. Official release notes describe the August 31, 2026 release and Apollo510/Apollo510B EM9305 transport, sleep, clock and recovery changes. The following raw files were downloaded by exact revision, retaining Apache-2.0 notices:

| Retained file | Original path | SHA-256 |
|---|---|---|
| acquisitions/apollox_blue.c | drivers/bluetooth/hci/apollox_blue.c | 9d561bc515c9f889b2f879569ff679edb8343a582e39b0a4788e86b885fdfbed |
| acquisitions/em9305_ll_features.h | drivers/bluetooth/hci/em9305_ll_features.h | 58fb3463652968b6b2206f572ab1f7f25013dbae028a270aa891aa5ae77ddda2 |
| acquisitions/LICENSE | LICENSE | c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08 |

The inspected registration/manifests and consolidated reference did not mention this repository. Recommend coordinator-owned pinned reference submodule if retaining the full Zephyr tree is justified. No worker modifies the already dirty `.gitmodules`.

## Concrete inference and discriminator

Driver lines 75–86 define opcode `0xFFF2` as local supported feature setup with length eight; lines 120–134 construct the exact eight-byte feature mask. Lines 1147–1181 send feature setup, TX power, then configure EM9305 sleep; low-power success deasserts CLKREQ, while low-power sleep failure returns an error. Non-low-power failure logs and continues. Lines 179–234 separate radio recovery from heartbeat.

Consolidated `g2/docs/reference/protocols.md:275–276` calls stock `0xFFF2` NVDS update. Same opcode alone does not establish same command schema across chip/controller versions. The finite new check is to inspect the already authenticated stock command emitter payload length and bytes against this eight-byte feature mask and the SDK NVDS struct. If they are equal, record a supported feature interpretation with exact bytes and controller version assumptions; if different, retain the stock NVDS interpretation. A source name cannot override target instructions. Consolidated links to historical `cordio-hci-*-recovery.md` did not resolve at their referenced current paths in this checkout, so those old reports were not silently treated as present evidence.

This supplies a concrete protocol and clock-order comparator for existing stock reset/transport roots. It does not establish the producing source, linked configuration, hardware operation, or permission to import Zephyr behavior into stock. Newer recovery/sleep policy may intentionally differ from the locked firmware.

## Coverage already present and searches closed in this pass

Inspected `.gitmodules`, consolidated libraries/protocols, prior source discovery finite checklist and EM9305 official-version boundary, fresh dependency-gap report, SDK 5.2 public-source map, Cordio SDK parser lead, and IAR/Nema gap report. Existing dirty/untracked work includes subsequent SDK5.2 acquisition, Cordio ATT/SMP/signaling, FlashDB/TLSF, DSP simulator and LZ4 reports. Those branches are already owned and were not restarted. The older Nema report's package-unavailable observation is superseded by the newer authenticated SDK5.2 source map; it must not be propagated as current status.

Public searches: `site:github.com EM9305 qf_port SDK`, `site:github.com Apollo510 AmbiqSuiteSDK 5.2.0`, `site:github.com GX8002 lvp SDK`. Results produced the new official Ambiq Zephyr reference. NationalChip/lvp_sed HEAD `28439b899f395b546f578bfe459dc4226428f0f0` was checked, but consolidated libraries already explicitly attribute lvp_kws/lvp_sed boot code. No duplicate acquisition was justified from that result. No new official EM9305 v4.2 port implementation surfaced. Search results are a bounded visibility observation, never universal absence proof.

SDK public source map already inventories TinyUSB/OpenAMP/libmetal/CMSIS/crypto candidates and explains absent locked target attribution. Generic inclusion in the newer SDK does not justify new source providers. Existing CMSIS_5 reference supplies DSP family source; exact supplied header identity and stock inclusion remain separate. Private IAR DLIB, Nema implementation, EM/controller source and producing compiler/configuration gaps remain. These require authentic matching inputs or new target-bound evidence.

## Remaining useful work

The Ambiq Zephyr eight-byte feature-vs-NVDS comparison is newly actionable. Previously enumerated codec mode tables, application callback descriptors and finite model-size tuples remain finite source checks unless their owners have since closed them. This audit did not establish their vacancy or perform instruction work. Whole-firmware knowledge exhaustion cannot be certified by a repository/source listing; it needs systematic target coverage and independent review. No downloaded source was compiled or executed and no hardware was accessed.
