# G2 `pb_service_terminal.c` recovery

Status: complete linked-object census, clean-room production C, fail-closed
host/build/package qualification, with live qualification deferred by project
direction.
Run addresses use `run = file_offset + 0x00437FE0`.

## Result

Thirteen exact-named functions plus their shared alignment/literal tail occupy
`[0x005CE7C4,0x005CF2B4)`. The bodies contribute 2,554 bytes with SHA-256
`954b591a128ed3b02804f7f832bc9f59ba992c6450fa5f3badb03db4df4ae620`;
the 246-byte tail has SHA-256
`7d09b766d6efb89199b2c33d609f3a7a35adc963da8fd3d3914792242eb41d02`.
The complete 2,800-byte object has SHA-256
`8163d6203ef880d6eb46be6f0f9bab099b8b830cddb248c7f1bc512aa0cb1c4e`.
An unrelated Thumb prologue begins at `0x005CF2B4`, closing the terminal
boundary.

The function map includes the shared `terminal_encode_and_send` helper, one RX
decoder, one command-response encoder, and ten notification encoders. Thirty-
three `BL` sites enter exact starts and the bodies contain 130 calls. There are
no direct strict-interior branches or `B.W` entries. An all-byte scan finds 15
accidental values inside the interval, but none resolves to an exact function
start; no stored callable entry pointer is inferred from them.

## Message behavior

RX rejects a null input or destination with status 6 and decodes through
nanopb into caller-owned storage. Decode failure returns 5. Successful input
uses byte 1 as its magic value and suppresses a repeat of the byte at
`0x20074FFF` received within 3,000 ms of the tick at `0x20074874`, returning
13. A new message updates both globals and returns zero. Unlike some adjacent
protobuf services, this body does not contain an evidenced RX hexdump, so no
hexdump-limit contract is claimed.

The shared TX helper clears 0x850 bytes at `0x200F9694`, copies one of eleven
supported tag layouts, and nanopb-encodes through the 0x878-byte buffer at
`0x20374378`. An unsupported tag returns 8 and encode failure returns 5. If
the role gate permits transport, the helper uses route 1 / service `0x30` and
selects transmit for command responses or notify for the other envelopes.
Success returns zero even when the role gate suppresses transport.

The envelopes are:

- command response: caller magic, command `0xF0`, tag 13, one-byte error code,
  transmit;
- status reply: command `0xA1`, tag 9, two bytes;
- voice input: command `0xA2`, tag 10, one byte;
- query reply: command `0xA3`, tag 11, two 32-bit values;
- agent interrupt: command `0xA4`, tag 12, one byte;
- session switch: command `0xA5`, tag 18, two 32-bit values;
- new session: command `0xA6`, tag 19, one 32-bit value;
- display state: command `0xA7`, tag 20, three 32-bit slots;
- new-session cancellation: command `0xA8`, tag 22, one byte;
- list focus: command `0xA9`, tag 24, one 32-bit value;
- overlay focus: command `0xAA`, tag 25, two 32-bit values.

The ten notification wrappers use `last_magic + 1` without writing that value
back to the RX global. Pointer-taking wrappers return status 6 on null; the
no-argument/value wrappers build zeroed local payloads. Display-state values
other than state 4 clear the session and overlay fields before encoding.

The historical source tree and license remain unavailable, so historical
source-only functions are not inferred. The independently authored
`components/apollo_main/core_overlay/pb_service_terminal.c` supplies fifteen
compilable source functions: two private memory helpers plus clean-room
implementations for all thirteen stock service entries. Apple-Clang Thumb
qualification emits 1,368 text bytes and eight alignment bytes with 23 strict
relocations. Thirteen whole-body `B.W` redirects replace all 2,554 executable
stock bytes; only the authenticated 246-byte non-executable literal tail is
retained. Host tests cover RX status/replay behavior, every tag/payload layout,
null and role gates, display-state normalization, and transmit-versus-notify
routing. The canonical package is 4,503,622 bytes with SHA-256
`8e7028f3e7ffcecdbe44c1eede4ffa3bbbfa593d41ce10ed7f4630aff3d7247e`.

The software functional gap is closed. Live service-`0x30` master/peer BLE
and terminal-UI qualification is blocked by unavailable physical evidence. The earlier
nonresponsive-fault inference is superseded: the charging case was
accidentally bumped during lunch and caused that test disconnect, not a device
or flashing fault. Future acceptance still requires authorized master/peer
BLE and terminal-UI evidence. This is not a hardware-completeness claim and
does not block the closed software route.
