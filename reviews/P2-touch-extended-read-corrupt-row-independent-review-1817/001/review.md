# Independent review 1817: scoped corrupt-row trace pass

The exact body is 82E0..854C (620 bytes, 291 decoded instructions). All 15 isolated traces execute original instructions and reached helpers without interception. The setup recomputes CRCs after writing row payloads and sequence values, then corrupts primary row zero with mirroring disabled. When a request intersects that row, the trace shows a zero-filled failed chunk and status `0x093E0001`; later valid chunks still copy. Requests beginning at row one return zero status. The asserted output, untouched A5 suffix, copy-callback presence, return, and SP restoration are reproduced.

The candidate source and artifact hashes match its receipt. An isolated replay completed all 15 traces and produced a `replays.json` byte-identical to the candidate file.

This is bounded trace evidence for the stated synthetic layout and requests, not full pseudocode recovery. Multiple corrupt rows, blank-versus-corrupt status interaction, provider failure, multi-copy behavior, and physical storage remain unresolved. No canonical admission or coverage change is made.
