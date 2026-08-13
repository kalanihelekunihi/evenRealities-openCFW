# Ring-buffer lineage and source recovery audit

Scope: official G2 `2.2.6.10` Apollo-main image; upstream Git-history and
binary analysis only. No firmware output or hardware was changed.

## Result

The generic component is definitively the dynamic-buffer lineage of
`AndersKaloer/Ring-Buffer`. The binary proves the compatible official-source
interval from commit `cda00e1efb815bad5100757f0d10d117f633ced6`
(2022-11-21) through `190e30bebcec22d7311fd941179d70b4f439c441`
(2024-11-13). The latter is selected as openCFW's maintained snapshot because
it is the newest source-equivalent commit before the firmware build timestamp
`2025-04-28T13:29:15Z`. This is not proof of Even's exact checkout or absence
of a behavior-equivalent vendor fork.

The lower bound is discriminating: `cda00e1` introduced all of the following
facts observed together in stock code:

- `ring_buffer_init(buffer, buf, buf_size)` and its exact expanded assertion
  `((buf_size & (buf_size - 1)) == 0) == 1`;
- a 16-byte object with buffer, mask, tail, and head at offsets 0/4/8/12;
- dynamic `buffer_mask = buf_size - 1` rather than the older fixed 128-byte
  object;
- the seven observed empty/full/init/queue/queue-array/dequeue/dequeue-array
  entry points and overwrite-oldest full-buffer policy.

The later commits in the interval change documentation or source whitespace
without producing a retained binary discriminator. Reporting an exact vendor
commit would therefore overstate the evidence.

## Stock boundary

| Segment | Span | Bytes | Status |
|---|---:|---:|---|
| `ring_buffer_is_empty` | `[0x00598134,0x00598146)` | 18 | Fully identified and source-recreated; generated entry redirect |
| `ring_buffer_is_full` | `[0x00598146,0x00598160)` | 26 | Fully identified and source-recreated; generated entry redirect |
| `ring_buffer_init` | `[0x00598160,0x0059818C)` | 44 | Fully identified and source-recreated; generated entry redirect |
| init alignment/literals | `[0x0059818C,0x00598198)` | 12 | Fully classified retained stock data |
| `ring_buffer_queue` | `[0x00598198,0x005981C4)` | 44 | Fully identified and source-recreated; generated entry redirect |
| `ring_buffer_queue_arr` | `[0x005981C4,0x005981E0)` | 28 | Fully identified and source-recreated; generated entry redirect |
| `ring_buffer_dequeue` | `[0x005981E0,0x0059820A)` | 42 | Fully identified and source-recreated; generated entry redirect |
| `ring_buffer_dequeue_arr` | `[0x0059820A,0x0059823C)` | 50 | Fully identified and source-recreated; generated entry redirect |

The contiguous cluster is 264 bytes with SHA-256
`19b070eb57bf11089632a16a58f077f816d3b45502914ab2dc435dbd2b10d009`:
250 instruction bytes plus 14 bytes of alignment/literal data. The seven
redirected callable spans cover 252 bytes because two alignment bytes occur
inside those spans; the separate retained literal island is 12 bytes. The only
three external entries are init at `0x0058FB62`, queue-array at `0x0058FB24`,
and dequeue-array at `0x0058FB32`; internal calls close the remaining topology.

## Completion estimate

| Work item | Complete |
|---|---:|
| Family/API identification | 100% |
| Function boundaries and direct-call topology | 100% |
| ABI/behavior recovery | 100% |
| Authenticated maintained source snapshot | 100% |
| Target code-generation comparison | 75% |
| Production overlay integration | 100% |

Apple Clang 21 successfully compiles both the pristine snapshot probe and the
bounded production adapter. The latter emits seven independently relocated
leaves totaling 248 source bytes plus four generated alignment bytes at
`[0x007B3F34,0x007B4030)`. It reuses the authenticated stock assertion provider
and expression/path strings. Generated redirects replace all 252 callable
stock-span bytes (250 instructions plus two alignment bytes), while the
12-byte stock literal island remains retained and classified.

The promoted Apple aggregate is overlay 130,316 bytes (SHA-256
`c293b537...f3478`), Apollo component 3,653,712 bytes (SHA-256
`1fd35053...f1c1d`), and package 4,432,206 bytes (SHA-256
`a5625a4b...30c2`). Host differential tests cover initialization/assertion,
overwrite-oldest behavior, zero-length operations, and 10,000 deterministic
randomized operations. Lorelei still has no reviewed native Clang toolchain,
so Linux profile replay remains pending and no Linux aggregate is inferred.
