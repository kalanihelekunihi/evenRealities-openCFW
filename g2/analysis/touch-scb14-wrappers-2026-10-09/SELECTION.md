# Predeclared SCB wrapper linkage

Reuse the unchanged authenticated GNU14.2.1 cy_scb_common.c object from the
holdout task. Compare three previously identified wrappers outside the completed
controls: ReadArray0x9250/30bytes, WriteArray0x92A6/48bytes,
WriteDefaultArray0x92E6/48bytes. Their only R_ARM_THM_CALL relocations at object
offsets22/36/36 bind respectively to ReadArrayNoCheck, WriteArrayNoCheck and
WriteDefaultArrayNoCheck. Original BLs at0x9266/0x92CA/0x930A resolve those
targets to0x9218/0x926E/0x92D6; all three helpers are already exact controls.

Place wrappers and dependencies at these original instruction-supported
addresses; retain complete30/48/48-byte sections without arbitrary expansion.
No source recompilation, flag change, source edit, address search or manual
patch. Count only126new wrapper bytes; the128helper bytes are reused dependency
evidence and cannot be added again to cumulative unique comparison bytes.
