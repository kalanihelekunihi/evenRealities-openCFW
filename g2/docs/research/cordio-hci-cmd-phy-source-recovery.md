# Cordio HCI PHY-command recovery

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock links only `HciLeSetPhyCmd` from the three-definition Apache-2.0
`hci_cmd_phy.c` source. Its body is `[0x00539E48,0x00539E92)`, 74 bytes,
followed by two alignment bytes owned by the TU. The physical interval
`[0x00539E48,0x00539E94)` hashes to
`c0474ed7346e079929469434be9d0915768ce3ab16535b28e28470883e6ca780`.
`HciLeReadPhyCmd` and `HciLeSetDefaultPhyCmd` are source-only.

The sole caller is `DmSetPhy` at `0x004C5844`. The wrapper allocates opcode
`0x2032` with seven parameter bytes through `hciCmdAlloc`, serializes handle,
all-PHYs, TX-PHY, RX-PHY, and PHY-options in little-endian HCI order, and
submits the buffer through `hciCmdSend`. Allocation failure returns without a
send. There is no stored entry pointer or strict-interior ingress.

## Source identity

The three AmbiqSuite R2.5.1 definition bodies are identical to the selected
Packetcraft r20.05c public source. The files differ in header formatting:

| Source | Git blob | Bytes | SHA-256 |
|---|---|---:|---|
| AmbiqSuite R2.5.1 `hci/ambiq/hci_cmd_phy.c` | `e9ef9a54cb1a8df7e71abfa579800c6226d5ba9b` | 2,869 | `e3df61a67bb7d4c88a2e9a36ed3cac3a5de250c850052368f6c9f014a9c9237d` |
| Packetcraft r20.05c `hci/dual_chip/hci_cmd_phy.c` | `e7bb445bb080a09bf3041f98dde3d355864eaf48` | 2,924 | `e9ddb84511f1163614fd3e912f903160d7fa913158690e2aff13729c522c75c6` |

The selected public commit is
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. This TU is not independently
release-discriminating; the closed DM PHY initializer and surrounding HCI ABI
provide the r20/R4 generation pin.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_cmd_phy.py --json
python3 -m unittest tests.test_analyze_g2_cordio_hci_cmd_phy
```

## Production admission

All three Apache-2.0 wrappers are maintained in
`components/shared/cordio/runtime_cordio_hci_cmd_phy.c`. The implementation
uses explicit little-endian stores for the exact public r20.05c payloads and
returns without sending when command allocation fails. Host tests cover all
three commands and allocation failure; the full translation unit and each API
compile for Cortex-M55.

The sole linked entry, `HciLeSetPhyCmd`, is production-routed by one guarded
redirect. Its 74 stock body bytes are replaced by 60 compiled bytes under two
strict relocations to the authenticated HCI command allocator and sender. The
read-PHY and set-default-PHY APIs remain source-owned and target-compiled
without inventing stock routes.

The canonical build now has a 365,508-byte overlay and 3,888,904-byte Apollo
component. The 4,667,398-byte package has SHA-256
`30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf`;
the 3,808,528-byte flash plan has 5,477 placed, two unresolved, five
container-only, and six protected regions. `make cordio-hci-cmd-phy-closure`
reproduces the software gate. Live PHY negotiation remains blocked by
unavailable authorized responsive G2/EM9305 physical evidence. No image was
signed, installed, or flashed; the wider HCI family remains a software gap.
