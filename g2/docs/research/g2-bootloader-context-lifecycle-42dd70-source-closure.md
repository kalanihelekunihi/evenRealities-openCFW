# G2 bootloader runtime-context lifecycle source closure

Four retained runtime lifecycle helpers are now source-owned MIT C: queue
context initialization at `0x0042DD70`, action-context initialization and
teardown at `0x0042DDAE` and `0x0042DDDA`, and the runtime enable sequence at
`0x0042DDF2`. The source preserves fixed queue dimensions, null-result failure
paths, guarded teardown and clearing, and the ordered critical/enable/mode/
commit provider sequence.

Apple clang 21 and Homebrew clang 22 reproduce all 136 authenticated bytes
exactly from mnemonic-only Arm source. Portable tests cover success and failure
status, context clearing, guarded teardown, and call ordering. Live scheduler,
retained-object, interrupt-mask, and failure-reset behavior is blocked by
unavailable physical evidence.
