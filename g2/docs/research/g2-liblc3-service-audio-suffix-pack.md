# G2 LC3 minimal strict-suffix packing audit

This receipt closes the Apollo-main flash-capacity arithmetic for the admitted
`-Oz` LC3/service-audio closure without authorizing a routed firmware image.
It supersedes the capacity conclusion of the earlier 30,676-byte full append
repack, not its evidence: that old repack remains counterfactual because it
would move 206 leaves without strict relocation contracts.

## Exact smaller move

The Apple best-order LC3 closure is 9,152 bytes larger than the current append
headroom.  The shortest contiguous append suffix that clears this deficit is
the final 84 relocated leaves:

* runtime interval `0x007EA620..0x007ECA44` (9,252 bytes),
* 9,174 bytes of strict source-owned closure payload plus 78 bytes of existing
  alignment padding,
* 288 authenticated relocations, all replayed at their proposed addresses,
* 127 exact-entry branch ingresses: 84 stock-entry redirects and 43 branches
  internal to the moved suffix, and
* zero exact-entry raw-pointer materializations.

Every moved leaf already has `strict_relocation_contract: true`.  A
deterministic first-fit-decreasing layout places the 84 closures, with exact
alignment, into seven authenticated tails of existing `B.W` plus generated
Thumb-NOP stock slots.  The entry branch in each host slot is retained; only
its already-generated NOP tail is used. Existing binary branch/pointer-value
targets are excluded from all 84 new entries. The packing consumes 9,174
payload bytes and 68 alignment bytes out of 61,320 authenticated tail bytes.
Host slots and payloads do not overlap.

The analyzer reconstructs a component in memory, rewrites all 84 entry
redirects, replays the 288 suffix relocations, writes the seven tail payloads,
and truncates only the now-dead suffix.  The resulting core receipt is:

* component size: 3,876,416 bytes,
* component SHA-256:
  `b3dc1d99cc8ce6b4c989e456379d613eb44aaa0fc20e0f0438c0831e3b67096b`,
* core end: `0x007EA620`, and
* suffix-pack placement digest:
  `fc797c985f1ed0b4e2cb88765dfe253e28111009adbcc2415828e184b83206ac`.

At that core end, the only fitting admitted Apple order is the already-audited
best order: 404-byte `.lc3_table_rodata`, 60,480-byte `.rodata`, then
19,360-byte `.text`.  It ends at `0x007FDFA0`, leaving 96 bytes before the
protected update record at `0x007FE000`.  Both recovered service-audio entry
sites can encode exact Thumb `B.W` redirects to the admitted setup/encode
roots.  The four exact 2,628-byte adapter RAM slots are unchanged.

## Additional size audit

The complete Apple closure was rebuilt with each of its 15 translation units
individually changed from the selected global `-Oz` policy to `-Os`, then to
`-O2`, while retaining section GC, the 11-import allowlist, and immutable-table
checks. No variant reduces the 80,244 bytes of emitted text/rodata/table data.
The table-only unit is byte-size neutral. Admitted `-Os` variants add 8 through
1,064 bytes; admitted `-O2` variants add 88 through 3,024 bytes. The energy,
MDCT, and SNS alternatives are rejected because their table-reference shape
no longer matches the six-reference policy. The previously tested
`-fmerge-all-constants` alternative also remains size-neutral. Because no
per-unit alternative is selected, the existing 84-configuration whole-encoder
`-O2` versus `-Oz` behavior equivalence remains the production behavior gate.

No retained stock LC3 or service-audio body is counted as free space. The only
reclaim used here is generated NOP padding behind already-routed entries plus
the exact strict append suffix after all of its entry redirects are replayed.

## Remaining production blocker

Capacity and the 84-leaf move are exact software proofs. The follow-on
production-order replay now source-authenticates all 11 runtime imports,
applies all 485 Apple LC3 relocations at the exact
table-rodata/rodata/text addresses, and verifies all 78 table initializers and
six table references. Production routing is still false until a canonical
package builder combines target-runtime tail payloads, suffix packing, LC3 XIP
bytes, four state slots, two service-audio veneers, and package integrity
updates in one atomic OTA receipt. See
`g2-liblc3-service-audio-production-replay.md` for the exact closure.

The analyzer emits no firmware and performs no hardware operations:

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_suffix_pack.py --pretty
python3 -m unittest \
  g2.tests.test_analyze_g2_liblc3_service_audio_suffix_pack
```
