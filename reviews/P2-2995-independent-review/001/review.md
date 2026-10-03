# Independent review 2995 — transmit drain

**Result:** PASS_SCOPED; `accepted: false`.

I checked the candidate bound to `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-event-apply-original-transmit-drain-2994/001`. Its source, decoded ITCM leaf, two body digests, and three listed artifact hashes match the receipt. I reran its original-instruction fixture script with output redirected to a fresh isolated directory; it passed all 320 cases.

Across counts 1, 4, 5, 8, and 9, the asserted literal drain writes follow `ceil(count / 4)`; the cases then check the ordered restoration writes, delay argument and loop count, incoming R3 return, SP, and PRIMASK. The script executes the original event/delay code without firmware-function interception.

The fixture keeps transmit occupancy at four and uses an explicit ready/status setup. It does not establish real FIFO/payload behavior, receive-FIFO behavior, other volatile reads/registers, NZCV effects, physical hardware semantics, or caller ownership. This is private scoped evidence and does not admit a canonical record.
