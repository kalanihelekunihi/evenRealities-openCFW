# Goodix GH3X2X register-profile decoder provider boundary

## Decision

The formerly unclassified function at `0x0002B6E0` / 514 executable bytes is routed to
`goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable`. It
decodes a private eight-channel GH3X2X register profile and is not eligible for local
reconstruction.

## Exact evidence

| Entry | Bytes | SHA-256 | Direct entry |
| --- | ---: | --- | --- |
| `0x0002B6E0` | 514 | `25a1ec257775b73fe1310c36758df77a32bed3314de24d61b8574c0fe9e61a4f` | `0x0002A810` (`B.W`) |

The sole caller is the already Goodix-gated four-byte branch thunk at `0x0002A810`; there is no
outside direct caller. That thunk is invoked by the provider register/configuration parser when
it reaches the profile terminator. The caller-set digest is
`f00d34b85455f97445d8df49ec029d56a569c909aa1fcc2c5941c90202669f0e`.

The function expands per-channel fields, presence masks, sampling divisors, and auxiliary channel
records into provider-owned state. It also contains provider fatal-loop bounds for invalid channel
counts. These semantics place it inside the GH3X2X provider; they do not authorize copying the
private profile layout, parser, or failure behavior.

Use a lawfully obtained Goodix package with recorded version, hashes, ABI, license, and
redistribution terms. The summarizer is static, performs no live register I/O or device access,
and emits no private profile blob.

## Reproduce

```sh
python3 tools/summarize_r1_goodix_register_profile.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
