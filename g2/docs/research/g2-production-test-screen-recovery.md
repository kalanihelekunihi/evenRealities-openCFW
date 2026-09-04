# G2 generic production-test screen recovery

Status: complete linked-object census, clean-room production C implementation,
dual-profile source routing, and fail-closed behavioral verification. Physical
panel validation is blocked by unavailable authorized G2 hardware evidence.

The retained `app\gui\ProductionTest\production_test.c` object occupies
`[0x005CF7A8,0x005CF8E4)`: three bodies / 286 bytes, two alignment bytes, and
a 28-byte pool, for 316 physical bytes. The body and physical SHA-256 values
are `0b94d5465cc85f336d3f2a57079e2dd3f2fe9f8cc1db9292be575b2db2ca9c9e`
and `93ffdf985efdeae31d82e22ab419652833f94ab3692d162f34534ab84afbb1bb`.

The exact retained common-data handler, an always-true predicate, and screen
event handler are all pointer-routed. Descriptor `0x006A45E0` binds screen ID
`0x10B`, handlers, and state `0x200030A0`; cell `0x00793748` binds the
predicate. No BL or `B.W` targets any entry or strict interior. A bytewise scan
does find 92 entry/interior-shaped values: three are the authenticated roots;
the other 89 are pinned instruction-byte lookalikes, not accepted pointers.

For event 2, the UI handler creates a black 640 by 480 root and nine 10 by 10
white objects in a 3×3 grid. X positions are 66, 266, and 466; Y positions are
21, 121, and 221. It publishes the root at `0x20074894` and `0x200030A4`.
Event 3 is a recognized no-op. The next unrelated delimiter parser begins at
`0x005CF8E4`, closing the physical boundary.

OpenCFW now owns a clean-room MIT implementation in
`components/apollo_main/core_overlay/production_test_screen.c` with its ABI in
`production_test_screen.h`. The three stock entries are source-routed in both
reviewed Apple Clang 21.0.0 and Homebrew Clang 22.1.8 profiles. Their compiled
text is 294 bytes in each profile and the event leaf has a strict 25-call
relocation contract to the retained LVGL ABI. All 286 stock body bytes are
displaced; the two alignment bytes and 28-byte diagnostic pool remain retained.

`tools/analyze_g2_production_test_screen.py` pins the source/header identities,
three production leaves, final post-link entry branches and NOP fill, compiled
text hashes, package/manifest consistency, complete non-code extent, descriptor
and pointer topology, grid contract, callees, false-positive census, and next
function boundary. The host runtime test verifies the registered ABI and exact
3×3 object layout. No hardware write or flash operation was performed. Closing
physical validation requires an authorized G2 panel trace confirming the black
640×480 root and nine 10×10 white dots at the recovered coordinates.
