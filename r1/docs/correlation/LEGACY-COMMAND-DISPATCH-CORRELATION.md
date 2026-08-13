# Legacy command-frame dispatch correlation

Status: one R1 product function / 464 executable bytes byte-pinned; bounded pure router implemented.

## Outcome

The former frontier leader at `0x0004E258..<0x0004E428` clears a 36-byte global workspace,
copies the received legacy command frame into it, reads the opcode at byte offset 2, and routes
23 recognized opcodes to distinct handlers. It returns zero after a recognized route and
`0xFFFFFFFF` for an unknown opcode. The function body has SHA-256
`be3357d945c4470611d70da7e97691fe9fb6a87bbda16b8da2e6d3eea48e3ca1` and one direct caller,
at `0x0004514E`.

`../../scripts/firmware/summarize_r1_legacy_command_dispatch.py`
authenticates the recovered application, complete function body, caller set, workspace pointer
`0x2001A174`, and routing metadata.

## Recovered routing contract

| Opcode | Recovered handler | Opcode | Recovered handler |
| --- | --- | --- | --- |
| `0x11` | `0x00062584` | `0x12` | `0x00062546` |
| `0x21` | `0x0006244E` | `0x22` | `0x000624F4` |
| `0x23` | `0x0006249C` | `0x24` | `0x000624C8` |
| `0x34` | `0x00062412` | `0x37` | `0x000628F6` |
| `0x40` | `0x000629D4` | `0x52` | `0x00062834` |
| `0x53` | `0x00062388` | `0x54` | `0x000628AE` |
| `0x55` | `0x00062A5C` | `0x56` | `0x00062840` |
| `0x57` | `0x000628CC` | `0x85` | `0x00092B98` |
| `0x88` | special pair-auth response through `0x00033850` | `0x89` | `0x0006A714` |
| `0x8A` | `0x00062B4C` | `0x91` | `0x0006210C` |
| `0x94` | `0x0004E1F8` | `0x95` | `0x00062BEC` |
| `0xF2` | `0x00062C30` |  |  |

Opcode `0x88` is the only inline special case: the stock path emits pairing diagnostics, places
response byte `2` on its stack, and invokes `0x00033850` with type `2` and length `1`. This
closure records that routing distinction but exposes no pairing or authorization mutation.

## Clean-room boundary

[`../../src/r1_dispatch.c`](../../src/r1_dispatch.c) implements only the R1-owned
workspace and opcode-selection policy. It deliberately returns a typed route instead of invoking
the recovered handler addresses. Each handler retains its own ownership and source-admission
status; classifying this router does not admit or recreate any handler, provider, transport,
pairing, logging, or persistent-state implementation.

The stock function passes the caller's length directly to `memmove` after clearing 36 bytes and
therefore relies on an upstream length invariant. The clean-room function requires a 3-to-36-byte
frame and a full 36-byte caller-owned workspace, preserving valid behavior while rejecting the
overflow condition. Tests cover all 23 routes, zero filling, the full-size frame, undersized and
oversized frames/workspaces, an unknown opcode, and null arguments.

Reproduce the evidence check with:

```sh
python3 scripts/firmware/summarize_r1_legacy_command_dispatch.py
```
