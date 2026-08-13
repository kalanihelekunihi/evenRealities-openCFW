# Cordio DM PHY source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_phy.c` unit is bounded at `[0x004C5734,0x004C5874)`: six
linked functions contribute 308 code bytes and a 12-byte literal tail brings
the physical object to 320 bytes, SHA-256
`3c0856787ff56af58207792e0d15365aae8de8efb84efb82e9398dd5c7cf81e8`.
Five direct calls, one registered HCI-handler pointer, and zero strict-interior
pointers close ingress. `DmReadPhy` and `DmSetDefaultPhy` have no surviving
body, caller, or stored pointer and are classified dead-stripped.

`DmPhyInit [0x004C584A,0x004C5868)` decisively selects the Packetcraft
r20.05/Ambiq R4 source family. It locks the task, installs component 9, and
calls the widened `HciSetLeSupFeat` ABI with the 64-bit mask
`0x0000000000000900` and `TRUE`, enabling the 2M and coded PHY feature bits,
then unlocks. The r19/AmbiqSuite 2.x body only installs the interface and uses
the older 32-bit declaration, so it cannot explain the stock call shape.

The selected public Apache-2.0 source is Packetcraft r20.05c blob
`50124b4c6381c744eefc241ede3888989b56897e`, 7,780 bytes, SHA-256
`0bbe1687c0ababa185443a61aedab08037445d4802aaa8b6978f8a8d4f4a272c`.
Official AmbiqSuite R4.4.1 as imported by AmbiqAI/neuralSPOT is byte-identical
later corroboration, not a claim that its import commit historically produced
the G2 binary.

`dmPhyFcnIf [0x0078A85C,0x0078A868)` retains the default reset/message
handlers and `dmPhyHciHandler`, SHA-256
`3794cf8786f7ac1d372238f121ca140d76466e0a6ec54a77f4bd250bcd7de2f3`.
HCI events `0x29`--`0x2B` dispatch read, default-set, and update completions;
the three action leaves call the application callback at `dmConnCb + 0x9C`.
`DmSetPhy` resolves the connection under the task lock and forwards the full
five-argument PHY preference request to HCI.

The repository preserves
`research/readiness/dm-phy/`, 5,470 bytes, SHA-256
`304fa7a13ab27a15bb79c06df5567d30aa75a94417377d28f43b2c2d60e9008e`.
Its fourteen inner hashes cover all eight source functions, fourteen build
inputs, twelve provider seams, and two live Os/O1 zero-unresolved links. It
excludes firmware, licensed source/header bytes, objects, ELFs, disassembly,
maps, and caches.

```sh
python3 tools/analyze_g2_cordio_dm_phy.py --json
python3 tools/verify_research_corpus.py --json
```

Production still cuts these bytes forward: source replacement and generated
ownership are both zero. The next bounded task is a fail-closed inclusion
census for the three-function `dm_sec_slave.c`, followed by `dm_sec_master.c`.
