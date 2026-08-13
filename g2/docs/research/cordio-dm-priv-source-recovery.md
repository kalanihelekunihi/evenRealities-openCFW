# Cordio DM privacy source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_priv.c` translation unit is bounded at
`[0x004D254C,0x004D293C)`. Twenty-one functions contribute 980 code bytes;
the trailing 28-byte literal pool brings the physical interval to 1,008
bytes with SHA-256
`749b2dab02c3e494d31a9c5b09da54bb026f13f698a0ad16d0971a4d41c22509`.
Nineteen direct calls, thirteen registered table/interface pointers, and zero
aligned strict-interior pointers close ingress.

Four public APIs have no body, caller, or pointer and are classified
dead-stripped: `DmPrivReadPeerResolvableAddr`,
`DmPrivReadLocalResolvableAddr`,
`DmPrivSetResolvablePrivateAddrTimeout`, and `DmPrivGenerateAddr`. All 25
source functions are therefore accounted for. This is source identification;
the stock object remains cut forward and no production byte is replaced.

## Source family and license

AmbiqSuite R2.4.2/R2.5.1 use the Packetcraft r19 architecture: one component
with nine actions. Packetcraft r20.05 through r20.05c and official later
AmbiqSuite R4.4.1 use the split architecture found in stock: seven ordinary
actions on component 6 and two AES-completion actions on component 15.

The exact r20/R4 source content is Git blob
`45966dc6bfcf77162b37695ba821eff78c1c551c`, 25,576 bytes, SHA-256
`13f285c4bf2d03744cd7f2665e465ed03f33491fd88cec001a303a04334b24ac`.
Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` is the public Apache-2.0 route.
The byte-identical AmbiqAI/neuralSPOT R4.4.1 import corroborates the later
source family but postdates G2 and is not claimed as its historical producing
commit.

## Stock ABI and behavior

`DmPrivInit` at `[0x004D27E0,0x004D27F6)` locks the WSF task, installs
`dmPrivFcnIf` in `dmFcnIfTbl[6]` and `dmPrivAesFcnIf` in slot 15, then
unlocks. The registered tables are:

- `dmPrivAct [0x0076AF6C,0x0076AF88)`: seven action pointers;
- `dmPrivAesAct [0x0078D454,0x0078D45C)`: two action pointers;
- `dmPrivFcnIf [0x0078A868,0x0078A874)`;
- `dmPrivAesFcnIf [0x0078A874,0x0078A880)`.

The main messages occupy events `0x30` through `0x36`; AES completions use
`0x78` and `0x79`. `dmPrivCb` is at `0x20073A58`, size `0x1A`, with 3-byte
hash/prand fields and a 16-byte AES buffer. Address resolution and generation
serialize through separate in-progress bits, zero-pad AES plaintext, and
report busy/authentication status through the registered DM callback.
Resolving-list operations map directly to the corresponding HCI commands.
Successful enable/disable completion updates `dmCb.llPrivEnabled` and emits
the device-privacy bridge event; the optional consumer remains default-routed
because `dm_dev_priv.c` is independently proved absent.

## Lorelei handoff

The repository preserves
`research/readiness/dm-priv/`, 6,447 bytes, SHA-256
`f4a8b9bdefac2edc3f400e471703c695ab2d434a84ad9680d3b73eb6c692761b`.
Its fifteen inner hashes cover all 25 source functions, the exact include and
provider closure, Os/O1 builds, and two live zero-unresolved links. The build
uses the byte-identical public r20.05c source; supplied R4 identities are
recorded without claiming a complete exact R4 header configuration. Firmware,
upstream source/header bytes, objects, ELFs, disassembly, and caches are
excluded.

Reproduce the guarded checks with:

```sh
python3 tools/analyze_g2_cordio_dm_priv.py --json
python3 tools/verify_research_corpus.py --json
```

The adjacent linked `dm_sec.c` object is the next coherent closure target;
the retained Ambiq HCI event port remains the subsequent producer-side target.
