# Ambiq Cordio HCI command recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Current closure

The shared Ambiq `hci_cmd.c` object is bounded at
`[0x0052AE38,0x0052B8A4)`, 2,668 bytes, SHA-256
`dc34dc1f11085b6c7e8748c7edebf2e1b4dbc1568774dd8352b7fc064ca15119`.
It contains 50 linked bodies totaling 2,654 bytes and one 14-byte
alignment/literal island. The concatenated body SHA-256 is
`cab0777a869c367127b83c0f51c76bb8c7fec32582d7b3f634f8e4f157ccecc1`.

Stock accounts for all 72 definitions in the later official Ambiq R4.4.1
source family: 50 linked and 22 source-only. Ghidra missed `hciCmdInit` at
`[0x0052AEC6,0x0052AEE6)`; raw Thumb control flow and its exact queue/timer
initialization restore the entry. The next function at `0x0052B8A4` belongs
to a different TU.

The exact direct-call scan finds 156 ingress sites across all 50 linked
entries and all 127 direct calls issued by the bodies. No aligned stored pointer
targets a function entry. One aligned word at `0x006317C0` numerically equals
`HciLeStartEncryptionCmd+0x4D`, but is unrelated packed data rather than a
function pointer; no accepted stored or branched strict-interior ingress
survives.

## Command queue ABI

`hciCmdCb=0x20073A90` contains a 16-byte timer, queue at `+0x10`, opcode at
`+0x18`, and command-credit byte at `+0x1A`. The literal island contains
`&hciCmdCb.cmdQueue=0x20073AA0`, `hciCmdCb`, and external
`hciCb=0x20073870`.

`hciCmdAlloc` allocates a three-byte command header plus parameters.
`hciCmdSend` queues commands, starts the ten-second timeout, and removes and
frees a command only after the closed transport reports success. Completion
stops the timer, restores one command credit, and services the next queue
entry. Timeout shuts down and reboots the radio before requesting a DM reset.
`hciClearCmdQueue` drains pending WSF buffers before reset.

## Source family

The selected later official oracle is AmbiqSuite R4.4.1 imported by
AmbiqAI/neuralSPOT commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`:

```text
blob    106e76123c0f03f05f7ce3e4238d02b1ac98fd8f
bytes   51,777
sha256  3a2d4609d803524f4765dbdfc65ec043035f2aa75526b0aa39f04873e62d5468
```

Its 72-definition inventory, queue-clear helper, command order, peer-SCA
wrapper, and radio-test API surface match stock. The later import is a
reconstruction oracle, not G2's proven historical generating commit. This
file remains proprietary under the Arm Cordio SLA; openCFW records metadata
and clean-room behavior only.

The complete source-order and stock-body ledger is
[`ambiq-cordio-hci-cmd-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-cmd-function-map.tsv).
[`analyze_g2_cordio_hci_cmd.py`](../../tools/analyze_g2_cordio_hci_cmd.py)
pins that manifest, provenance, aggregate closure, every linked body, the
physical interval, literal island, direct-call digests, and pointer
classification. Its focused regression test keeps the 50/22 inventory,
queue ABI, and proprietary-source boundary fail-closed.
