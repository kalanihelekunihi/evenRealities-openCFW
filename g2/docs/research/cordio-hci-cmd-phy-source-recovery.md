# Cordio HCI PHY-command recovery

Status date: 2026-08-09  
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

No production bytes are replaced yet.
