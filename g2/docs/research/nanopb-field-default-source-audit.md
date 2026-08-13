# Nanopb `pb_field_set_to_default` source audit

## Decision

The G2 function at `[0x0048FCE2,0x0048FDF2)` is authenticated, source-recreated,
and production-integrated as nanopb `pb_field_set_to_default`. The selected source
oracle remains nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`.

## Boundary and topology

The 272-byte stock body has SHA-256
`0d0dd0be0ae68f84bb20e39f7c95f500656316563d95b6d5cc3e290d4b131728`.
Its only direct caller is `BL 0x0048FCE2` at `0x0048FE7E`, encoding
`fff730ff`. The surrounding 24 bytes `[0x0048FE72,0x0048FE8A)` hash to
`8f30c2456222973fb3f6728f3e4951968e8b94754fc69ec90434a1ca29e95590`.
There is no alternate `B.W`, conditional, narrow, interior, or stored-pointer
ingress.

The predecessor `decode_extension` body `[0x0048FC88,0x0048FCE2)` is 90
bytes with SHA-256
`0f630c1173971762af8df1ec82ed50cff6f292a9b77eafae06e56b9f3b659472`.
The successor is the separately authenticated 166-byte
`pb_message_set_to_defaults` body.

## Upstream release matrix

The exact selected definition is `pb_decode.c[28476:31080]`, 2,604 bytes
with SHA-256
`dced6e406d8c2c657a90cd599a60457a83bbc123b6ddfbfb9bff71778a773265`.
A disposable checkout compared the definition across the limited plausible
release set. The bytes are identical in all four releases:

| Release | Peeled commit | Definition SHA-256 |
|---|---|---|
| `nanopb-0.4.7` | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `dced6e...3265` |
| `nanopb-0.4.8` | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `dced6e...3265` |
| `nanopb-0.4.9` | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `dced6e...3265` |
| `nanopb-0.4.9.1` | `cad3c18ef15a663e30e3e43e3a752b66378adec1` | `dced6e...3265` |

This proves an exact pristine compatibility interval for this definition; it
does not uniquely identify the vendor checkout. The repository-wide selected
baseline remains 0.4.9 because it is the authenticated whole snapshot.

## Dependency closure

| Site | Target | Provider | Candidate treatment |
|---|---|---|---|
| `0x0048FD04` | `0x004D93A4` | `pb_field_iter_begin_extension` | fixed stock seam |
| `0x0048FD12` | `0x0048FDF2` | `pb_message_set_to_defaults` | internalize with paired candidate |
| `0x0048FD98` | `0x004D9384` | `pb_field_iter_begin` | fixed stock seam |
| `0x0048FDA2` | `0x0048FDF2` | `pb_message_set_to_defaults` | internalize with paired candidate |
| `0x0048FDB6` | `0x0043C0E4` | released memory fill | replace with local byte loop |

When this body and `pb_message_set_to_defaults` are recreated together, three
cross-calls become source-local and the nonstandard `(destination, count,
value)` memory-fill dependency disappears. The paired 438-byte candidate then
retains four fixed helper families: `pb_field_iter_begin_extension`,
`pb_field_iter_begin`, `pb_field_iter_next`, and `decode_field`. It has no
fixed data, heap, device, or callback seam of its own.

## Independent decompiler confirmation

Rizin recovered the upstream branch structure and five calls. Ghidra 12.1.2
headless then imported the raw image without full-image autoanalysis and
independently recovered:

- recursive extension-default initialization and `found = false`;
- optional/repeated/oneof size or presence reset using the recovered 16-bit
  `pb_size_t` ABI;
- recursive submessage initialization only when descriptor metadata requires
  it;
- zero-fill for ordinary static fields; and
- pointer/count reset for pointer fields.

The noanalysis decompile completed in about five seconds. This makes targeted
headless queries the default for already bounded functions; full-image
analysis is reserved for discovery and cross-reference work.

## Production integration and reproduction

Boundary, upstream definition, release-range identity, caller topology,
outgoing call mapping, semantic recovery, source recreation, Apple target
compilation, placement, and production integration are each 100% complete.
Selector 0 emits 256 bytes at `0x007B38CC` with relocated SHA-256
`5cfe4525760f82d39ca487e4a4dfb5120b30401ddaca71b49d73ad81fc6a409a`.
Its four strict relocations resolve to source-owned iterator/default routines.
The complete 272-byte stock entry is now a guarded `B.W` plus Thumb NOP fill.
The paired message routine now binds `decode_field` to the reviewed source leaf
at `0x007B39CC`; this defaults closure has no executable stock seam. Linux
replay and hardware execution remain deferred.

```sh
python3 tools/analyze_g2_nanopb_field_default.py --json
python3 -m unittest tests.test_analyze_g2_nanopb_field_default
python3 -m unittest tests.test_runtime_nanopb_defaults_pair
```

The analyzer fails closed on the official image and upstream identities, body,
caller context, ingress topology, all five calls, neighbors, and definition
span. The paired production suite additionally pins host semantics, both local
files, selector section sizes, and exact relocation-symbol order.
