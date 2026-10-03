# Independent review 2643: profile derivation execution

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate, source, body, and artifact hashes match. The original seed word is zero and the mask literals resolve to `0x00F00FFF` and `0x000FF00F`. I reran the candidate emulator into a fresh isolated directory; all 1,600 fixtures pass with no function interception.

The tested matrix exercises the full nibble construction and both output-key maps. It confirms the external-bit increment, output writes, status, preserved R4/R5/SP, and sentinel return. In these fixtures, 1,280 cases match both keys and write both outputs with status 0; 320 unmatched-key cases return 5 without writes. The selected inputs do not produce partial first-output-only cases.

External values and the seed are bounded to the fixture setup; concurrent changes and aliasing remain untested. This is operation-specific private evidence and does not establish other parent operations or caller ownership.
