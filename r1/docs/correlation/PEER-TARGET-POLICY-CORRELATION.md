# Target-glasses peer-address policy correlation

Status: three R1 product functions / 550 executable bytes byte-pinned; pure policy implemented.

## Outcome

The former 464-byte frontier leader at `0x0004CCCC` decides whether a connected glasses peer
matches either configured right- or left-side target address. Its 54-byte address validator and
32-byte three-slot peer accessor are part of the same closed callgraph. No third-party BLE
implementation is present in these bodies, so only their R1 matching behavior is implemented
locally.

`../../tools/summarize_r1_peer_target_policy.py`
authenticates the recovered application, function bodies, direct caller sets, erased-address
literal, and product state pointers.

| Entry | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x0003D724..<0x0003D75A` | 54 | `0d75f1f6bd3144d7bf3cac842edac77cf9535dd18730bad740007036e96567d6` | target-address validity |
| `0x0004CAE4..<0x0004CB04` | 32 | `c8a4243594f64c864334b88fbc8af6baeb31f9ca710bd5d1f1d50d8fc62a4d00` | three-slot peer-address lookup |
| `0x0004CCCC..<0x0004CE9C` | 464 | `46631ec1f7328b6ae5946d07214624383b3f700d29da918fbb5b9662c96a00e3` | right/left target matching |

The peer records start at recovered RAM address `0x20008298`, have three seven-byte slots, and
store the six-byte address at slot offset 1. The two target addresses start at `0x200064C9` and
are separated by one byte. These addresses pin the stock layout only; the clean-room API accepts
typed caller-owned buffers and embeds no device address.

## Functional contract

- A target address is configured only when it is neither six zero bytes nor six `0xFF` bytes.
- When neither target is configured, every connected glasses peer is accepted.
- When peer lookup is unavailable, the stock policy also accepts the connection.
- Otherwise, the peer is accepted only when it equals either valid configured target.
- A valid right target and a valid left target are independent; an invalid side is ignored.

The acceptance on missing peer data is a recovered compatibility behavior, not an authentication
guarantee. Callers must continue to use the separately recovered BLE security and product
authorization policy; this helper must not be promoted into a trust boundary.

The implementation in
`../src/r1_peer_target.c` is pure and bounded.
Nordic connection state, peer-address acquisition, logging, disconnection, advertising, and
transport remain external. Tests cover all-zero/all-`FF` sentinels, slot bounds, both target
matches, mismatch, single-side configuration, no configured targets, and unavailable lookup.
