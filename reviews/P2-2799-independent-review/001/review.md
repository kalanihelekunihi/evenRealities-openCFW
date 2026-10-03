# Independent review 2799 — current profile restore original fixtures

**Result: REVISE_PROSE.** The isolated replay passed all 18 actual fixtures, and the source, body, and candidate artifact hashes match. The execution confirms three separate index reads and their corresponding profile loads, ordered field/control writes, the final clear-byte write, return registers, and preserved frame/mask state.

There is a fixture-count mismatch in the candidate prose: the receipt and `replays.json` both report 18, which is also the replay’s Cartesian product (3 index sequences × 3 target patterns × 2 mask values), while `pseudocode.md` says 27. Correct the prose to 18, or add nine fixtures and update the receipt if 27 was intended. This is a prose/count correction; no behavioral failure was observed.

The evidence is limited to those 18 injected-state cases and does not establish arbitrary caller/concurrent mutation or physical behavior. `accepted` remains false.
