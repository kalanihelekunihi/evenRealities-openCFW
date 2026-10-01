# Independent review 1813: scoped trace pass

The exact body is 82E0..854C (620 bytes/291 instructions). All 24 isolated traces execute original instructions with no interceptions. With current row zero, row-one overlay [24,36) is traversed first, then row-zero overlay [20,32) overwrites their intersection [24,32); requested slices, A5 suffix, zero return and SP match the generated traces. This establishes precedence only for this fixed two-overlay arrangement and current-row position, not complete pseudocode recovery.

Only two fixed overlays, one-copy/no-mirror and a fixed row ordering are covered; arbitrary ordering, multi-copy, mirror/error paths and physical storage remain unproved. This does not establish complete pseudocode or physical storage behavior. No canonical acceptance or coverage change is made.
