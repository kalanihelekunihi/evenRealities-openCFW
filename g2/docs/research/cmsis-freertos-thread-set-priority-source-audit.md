# CMSIS-FreeRTOS thread-priority source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`vTaskPrioritySet` and `osThreadSetPriority` are production source-owned as
one closed dependency unit. The task implementation is a bounded adaptation
of FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` under MIT. The public wrapper is a
bounded adaptation of CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `osThreadSetPriority` | `[0x004491B2,0x004491E4)` | 50 | `076a7d980114be9f392de41e1f1d058cb45a27bb5f6f831c3171c36039c4c388` |
| `vTaskPrioritySet` | `[0x00454C12,0x00454CEC)` | 218 | `fa38a23c007a168f79051504b23dd4087eb7845da2c3fb933c8083c8ade31152` |

The FreeRTOS adapter preserves null-as-current-task selection, the 0..55 G2
priority clamp, inherited/base-priority separation, event-list value
re-encoding, ready-list removal and tail insertion, top-ready-priority update,
and the upstream yield policy for current and non-current tasks. Its four
fixed calls bind to source-owned critical-section, list-remove, and yield
providers. The CMSIS wrapper preserves IRQ rejection, null/priority validation,
and status values.

Apple Clang 21 emits a 208-byte task leaf and a 50-byte wrapper at overlay
offsets `135396` and `135604`; Homebrew Clang 22.1.8 emits 210 and 50 bytes at
`137272` and `137484`. At this tranche boundary, the Apple component/package
were `3659050` /
`c191f78e5486d5627dc6d12bf731ed73090d3223e70ec3da2e753650cb43b213`
and `4437544` / `79575978fab81047f446953f19cc0dd0fbbc2a8501ae998405591b3f1c111108`;
the exact-root Linux component/package were
`3660930` / `fb916435ede275b277fe3da51cbbc3bb44131a2228a0c2170a41175b5f929706`
and `4439424` / `57a1299ea468bf3f06755fbe4be9ecacfb745e087f242405770ac31c1e8e80ea`.

This was the 32nd of 38 linked public CMSIS APIs. The later termination closure
supplies the current aggregate boundary. No image was signed or flashed.
