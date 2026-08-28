# G2 bootloader EasyLogger transport source closure

The complete level-dropping EasyLogger driver at
`[0x0041B854,0x0041B862)` and its complete four-channel transfer routine at
`[0x0041F918,0x0041F9B6)` are replaced by maintained clean-room C. These are
G2-specific service implementations; no upstream identity is claimed.

## Authenticated stock and caller bounds

| Entry | Bytes | SHA-256 | Direct caller |
|---|---:|---|---:|
| channel-one output driver `[0x0041B854,0x0041B862)` | 14 | `d46fae4c767497230f0f9b6c050033b824887d7e59dd06e893eee604bbb9c59d` | `0x0041A694` |
| four-channel write `[0x0041F918,0x0041F9B6)` | 158 | `363f18ceab0127d6da1b90de353495e370f50bce9631ee5ffbc83c2d725a2a95` | `0x0041B85C` |

The caller oracle scans every aligned Thumb `BL` in the authenticated
148,599-byte bootloader. The following 34-byte
`[0x0041F9B6,0x0041F9D8)` vector/literal island remains retained official
data; the source route does not consume or relabel it.

## Recovered contract

`runtime_easylogger_transport_41b854.c` is 10,235 bytes, SHA-256
`23a5180d3de5e45625f8323a226291d9f5ced532d7d73a320e57640794161d1c`,
under MIT. It preserves the complete observable behavior:

- the driver discards the incoming log level, moves the buffer and length to
  the downstream ABI, selects channel `1`, and returns the downstream status;
- the transport zeroes a 56-byte descriptor before validation;
- channel values outside `0..3`, or records whose initialized byte at `+0x18`
  is not exactly one, return error `1`;
- channel records are 28 bytes at table `0x20000454`; the lower handle is at
  `+0x04` and the completion byte is at `+0x19`;
- the descriptor stores buffer/length at `+0x00/+0x04`, zeroes the words at
  `+0x0C/+0x10`, and selects lower operation zero at `+0x34`;
- the completion byte is cleared before lower start seam `0x004233E9`;
- completion is polled up to 1,000 times, with a ten-unit wait through
  retained seam `0x0041F9E7` after each unsuccessful poll;
- invalid/uninitialized channels and a nonzero lower-start result return one;
  a zero lower-start result returns zero even if completion times out, exactly
  matching stock.

The driver deliberately enters the guarded transport seam at `0x0041F919`.
The descriptor-zero seam is `0x00415FF5`. Host oracles cover invalid and
uninitialized channels, channel-one routing with arbitrary level, descriptor
layout, pre-start completion clearing, delayed and immediate completion,
lower-start failure, and the full 1,000-wait timeout. A freestanding
Cortex-M55 compile gate rejects warnings or language-runtime dependencies.

## Dual-profile production evidence

Apple Clang 21 and exact-root Linux Clang 22.1.8 emit byte-identical,
relocation-free leaves:

| Leaf | Overlay offsets Apple / Linux | Bytes | SHA-256 |
|---|---:|---:|---|
| driver | `9088 / 9072` | 16 | `d1cc42fea93ac782c64485bf4d8ae24108ab6b8a7e9b189918395a5f547521a1` |
| channel write | `9104 / 9088` | 120 | `75b841d487a68f0f09928f569ea01229e4ef4dd4022533200050b317edbfcd0b` |

Apple produces a 9,224-byte overlay ending at `0x00436880`, SHA-256
`790603494de6a154f9032c4e7257b4c203e477893619c0b25325b972b39c45da`,
and a 157,824-byte provider, SHA-256
`ed616af6c46214891f25e3102f04554129a989fc83422700eb29d6242d3e68f5`.
Linux produces 9,208 / 157,808 bytes with SHA-256
`ffd38e6fd268398b0c8c5cc5afd0d898e2fe3cb62d000f2c91b96e4682f8b9a8` and
`1d4c130d0e9ac6de37b8bfe9c682b096eff5d85048faaa22fd414b1da3bc622c`.
Canonical accounting is 9,211 source-owned, 10,542 generated patch, 14
alignment, and 138,057 retained official bytes across 151 functions, 132
relocated leaves, and 149 patch sites. Apple retains 6,016 bytes of overlay
headroom.

The unsigned Apple package is 4,739,402 bytes, SHA-256
`4eaff8522cca172ef79c3e57686f395437e7a5877ce4c0ea6ab4831cc72e76a2`.
Its 4,483,119-byte flash plan hashes to
`070831da2ab2673f02436641a00df96365078868010a5e4b3bc064e9306b1388`
and records 6,446 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,515,396 bytes, SHA-256
`d05b3c4af715097e470d33d6a7e78646d7136a80ec24d07a6ae79ba5fc0a548b`;
its 2,386,655-byte plan hashes to
`1e5cfc63f03815b6ee3574a1bf3e1631495823df2e390274da56e0fbbf64940a`
and records 3,421 placed regions with the same unresolved/container/protected
boundaries.

No signer, device, debugger, UART, transport, flasher, reset, or boot path was
accessed. Live channel initialization, lower-driver DMA/interrupt completion,
timeout timing, and emitted-log evidence remain blocked: there is no
authorized responsive right G2 temple, and the authorized left temple must
remain stock. Later retained executable bootloader bodies remain software
gaps, so firmware-wide functional completeness is not claimed.
