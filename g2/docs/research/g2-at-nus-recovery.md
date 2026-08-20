# G2 pathless `AT^NUS` command recovery

Status: complete linked-handler census and fail-closed behavioral analysis;
historical source unavailable, no source candidate, and not
production-routed. Run addresses use `run = file_offset + 0x00437FE0`.

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
identity therefore remain unknown. No clean-room candidate exists, the
handler is absent from `overlay.json`, and it claims zero package ownership
bytes.

## Clean-room authorship and production routing

`components/apollo_main/core_overlay/at_nus.c` is an independently authored
clean-room replacement (597 bytes, SHA-256
`b80576c1aea40353475d331686bb5ec2b5915bc1acf911b73e6fee4a12cc87ae`) written
from this specification; no historical source survives. The handler emits the
retained `NUS+OK\r\n` response at `0x0078A370` through the retained output
provider at `0x00541430` and returns one, reading no arguments. Host tests pin
the response bytes, the single provider call, and the return value against an
oracle fixture; freestanding Thumb compilation exposes exactly one global text
symbol, `open_cfw_at_nus_handler`.

The candidate is routed into the Apollo main overlay under the reviewed
apple-clang profile as one 18-byte relocated leaf (overlay offset 147,024,
run address `0x007B8174`), reached through a single `B.W` entry redirect with
NOP fill that replaces the complete sixteen-byte stock object
`[0x005A5520,0x005A5530)`; the stored registration pointer `0x005A5521` at
`0x006C92A8` now reaches the source leaf through the redirect. Apple Clang 21
overlay/component/package sizes are `147042/3670438/4448932` with SHA-256
`b1a5bcd75031fadd93e875fa643400f20125f4d89e74b5fb55e9aa111b9dc789`,
`76bc4a35a0fe0ed26e9489b4e4b5aec5f95ea90463685acd316851ea657d8a1e`, and
`a842e5e3327a7790c006a3f50b2192a9e48a2f415be51e8f4d7be91a15f09adb`. The leaf
and redirect are gated `apple-clang`; the linux-clang profile keeps its
recorded pins. Ownership is the full sixteen-byte stock object (twelve body
bytes plus the four-byte literal pool). The component build, source package,
`open_cfw` verification, and the fail-closed analyzer (now asserting the
production routing) all pass.
