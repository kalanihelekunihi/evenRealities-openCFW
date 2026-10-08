# The two previously unvisited updater bytes

0x42aa1e..0x42aa20 is Thumb instruction e01b, B.N 0x42aa58. It is not padding. R10/SL is loaded from literal42acfc=200271bd at42a924. Stock stores classifier result to stack snapshot+16, writes that byte to the global at42a9ee, rereads global at42a9f2 for the auxiliary flag, then rereads global again at42aa0a for bounds dispatch.

Classifier output is0..4 under the validated scalar instruction behavior. With no intervening mutation, the above-four default branch is therefore not reached. Values5..255 at the second post-store global reread take the real branch, leaving args+4/+8 unchanged. Stock does not map those values to class3 bounds or return6 at this point. The stack snapshot remains the original classifier result.

The preserved218 source used the cached snapshot for these decisions and mapped its catch-all to class3. The successor uses two volatile global reads and limits class3 bounds to exactly3. Three original/source synthetic mutation comparisons (5,127,255) reach the two bytes and preserve sentinel bounds. They stop at the first actual state/deepsleep helper entry after dispatch and compare the full snapshot: class remains2 despite global values5/127/255. Earlier attempts continued into downstream invalid-state behavior and faulted; that behavior is excluded, not called a successful full updater execution.

The prefix receipts have PRIMASK=1 at the reached boundary; native critical-save masks ordinary interrupts for this region. The synthetic mutation is not a modeled ordinary IRQ interleaving.

This proves dispatch semantics under a synthetic changed byte. It does not demonstrate an IRQ race or memory corruption on hardware. Unmutated151+17 native updater fixtures still cover756/758 bytes. The synthetic prefix tests do not turn that into full native updater completion or prove all asynchronous behaviors.
