# Independent review 2351

**Result:** PASS_SCOPED.

Receipt 31378fee3225a66548320289e661bd457a9882e31c2016f5adb2e409fb636d1a pins the source and body [0x4C7C,0x4DA8), with the disassembly/replay/pseudocode hashes matching. Isolated replay passes all 192 fixtures.

The original 4C7C, 6AC0(0), 4C72, 4C44, 8FA0 and successful 6AC0(1) path execute without function interception. Allowed old modes reach the final chain: zero peripheral base produces normalized status 8, while nonzero base writes version byte 2 and permits mode1/status0. Unsupported modes 3/255 return1 and skip the final chain; mode1 is supported and reaches the final chain when setup succeeds. Mode arguments, calls, return/status, version/config changes and R4-R7/SP assertions pass.

Every fixture has exactly one zero store to cfg.word20 and reads it as zero at return. The corrected literal is separately pinned at 0x4DA8 with value 0x28F. No later local code in these fixtures rewrites word20.

**Limits:** The zero and nonzero base cases are synthetic RAM fixtures, not physical peripheral behavior. This does not establish persistence across other callers, intervening writers, aliasing or real integration, and does not resolve dynamic callback-target closure. Private evidence only; no canonical admission.
