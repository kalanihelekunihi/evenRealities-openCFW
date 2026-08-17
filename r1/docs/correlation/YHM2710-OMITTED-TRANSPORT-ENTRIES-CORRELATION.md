# YHM2710 omitted transport-entry correlation

## Result

Three explicit Ghidra-analysis seeds and the real policy target behind one of
them are now exact manual provenance supplements. Together they add
**four functions / 138 executable bytes** to the independently reconstructed YHM2710
closure. No stock binary, binary library, generated object, or opaque callback
is used by the build.

| Exact extent | Bytes | SHA-256 | Reconstructed role |
| --- | ---: | --- | --- |
| `0x000350E0..<0x0003510A` | 42 | `14f761cd6c8124fd2847335f8d6a9073ae753cdbf2ffbe5eae3b064eedb4bde9` | read register 3, set mask `0x08`, write register 3 |
| `0x00050614..<0x00050618` | 4 | `b47cb87d023eba0bd8c62727498eff741711fa1bd136b9930084637425cc3f9d` | branch-only public veneer for the register-3 policy |
| `0x000507CC..<0x000507FA` | 46 | `9391d38a9bd7c3659670f94676017935dd0401f36a4c20f282ef2276df2e0832` | complete register-read dispatch body behind `0x0003540C` |
| `0x00050804..<0x00050832` | 46 | `a8bfd276bfa23466703d61cbf43a24db694d6ddedc550c096108ee92ea94b553` | complete register-write dispatch body behind `0x00035760` |

## Entry and call evidence

- `0x000463CA` calls the veneer at `0x00050614`, which tail-branches to
  `0x000350E0`.
- `0x000350E0` calls the public register-read veneer at `0x0003540C` and the
  public register-write veneer at `0x00035760`.
- `0x0003540E` tail-branches to the complete read dispatch body at `0x000507CC`.
- `0x00035762` tail-branches to the complete write dispatch body at `0x00050804`.
- Both dispatch bodies retain their recovered lock, readiness, device-slot,
  completion, and common-release calls; the evidence tool pins every direct
  local branch target.

The explicit `0x00050614` seed therefore cannot be closed honestly without
also inventorying `0x000350E0`: the former is only a four-byte thunk and the
latter contains the observable register policy.

## Transparent implementation

The complete read/write dispatch behavior was already represented by the
typed transport operations in `reconstructed/yhm2710/`. The newly exposed
policy is implemented as `yhm2710_set_charging_event`: it performs a bounded
one-byte read of register 3, preserves every existing bit, ORs `0x08`, and
writes the byte back. Provider failure is propagated and the write is skipped
when the read fails. The host test pins the successful `0x42 -> 0x4A` update.

## Boundary

All four rows are classified `yhmicros_yhm2710_candidate` with disposition
`clean_room_reimplementation_owner_authorized`. The evidence tool performs
read-only analysis of the recovered image. It does not expose a live
single-wire transport, mutate GPIO, or admit a YHMICROS firmware element. Any
physical timing/electrical validation remains an owned-ring bring-up task.

## Verification

Run:

```sh
python3 tools/evidence/summarize_r1_yhm_transport_entries.py
```

The repository verifier also checks the four exact ledger rows, body hashes,
call topology, source symbols, tests, and the absence of opaque build inputs.
