# G2 pathless `AT^NUS` command recovery

Status: clean-room implementation and dual-profile production routing complete;
hardware validation is blocked by unavailable authorized physical evidence.
Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The standalone handler body `[0x005A5520,0x005A552C)` is twelve bytes with
SHA-256
`6e4a3e381abcbd8e2cc20d13cf39e575c0165b96e20b8ec1b7a8da780ff1548a`.
Its four-byte literal pool `[0x005A552C,0x005A5530)` points to the retained
response and has SHA-256
`2567cbc76b274edabf68bf27abbc7935b2877b2e743e89d5ca54da297b43693d`.
The complete sixteen-byte object has SHA-256
`e7839a2d6e1af4863ff17f7010a3fc079e44f5565526b612458904f5c539ace8`.
The preceding retained `at_codec.c` object ends exactly at `0x005A5520`; the
retained `at_fs.c` object begins exactly at `0x005A5530`.

The record `[0x006C92A0,0x006C92B0)` registers `AT^NUS` with odd Thumb
pointer `0x005A5521`. That is the only stored ingress. There is no direct entry
or strict-interior branch/pointer, including `B.W`. The handler passes
`NUS+OK\r\n` to output provider `0x00541430` and returns one; it does not read
its arguments or perform additional validation.

No retained source path or exact historical symbol survives. The manifest's
`atNusHandler` name is descriptive, not a recovered source symbol. Historical
source inventory, source-only function count, license, and whole-source
identity therefore remain unknown. Those historical-source limits do not
prevent the independently authored replacement below from having an exact,
reviewed source inventory.

## Clean-room authorship and production routing

`components/apollo_main/core_overlay/at_nus.c` is an independently authored
clean-room replacement (743 bytes, SHA-256
`acc7eacdc2d064a62bfa9d4150ad5cf1b8e8130fee4616c0f2295bdba7469f06`) written
from this specification; no historical source survives. The handler emits the
retained `NUS+OK\r\n` response at `0x0078A370` through the retained output
provider at `0x00541430` and returns one, reading no arguments. Host tests pin
the response bytes, the single provider call, and the return value against an
oracle fixture; freestanding Thumb compilation exposes exactly one global text
symbol, `open_cfw_at_nus_handler`; a compile-time entry-name definition emits
the profile-disjoint `open_cfw_at_nus_handler_linux` symbol from the same C
implementation.

The candidate is routed under both reviewed compiler profiles through
profile-disjoint 18-byte leaves. Apple keeps the established leaf at overlay
offset 147,024. Linux appends `open_cfw_at_nus_handler_linux` at its core-stage
tail so no previously reviewed Linux leaf is displaced. Two mutually exclusive
`B.W` entry redirects replace the complete sixteen-byte stock object
`[0x005A5520,0x005A5530)`; the retained registration pointer `0x005A5521` at
`0x006C92A8` reaches the active source leaf through the redirect for each
profile. Apple remains byte-identical at overlay/component SHA-256
`21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622` /
`7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6`.
Linux produces overlay/component SHA-256
`13a12b7fc7ec3af866d4ebe9229105ce923d6842ec6e8c4b0e01564582ed8ab1` /
`dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6`.
Ownership is the full sixteen-byte stock object (twelve body bytes plus the
four-byte literal pool).

No authorized G2 hardware or captured production eAT session is available in
this workspace. Hardware validation therefore remains explicitly blocked; no
device-response, timing, or transport-level completeness claim is made.
