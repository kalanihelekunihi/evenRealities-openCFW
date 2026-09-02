# G2 bootloader retained event-state source closure

Five retained event-state services are now source-owned MIT C: the state probe,
event-flags initializer, guarded context initializer, wait/log control, and
bit-publish control at `0x0042E224`, `0x0042E254`, `0x0042E39C`, `0x0042E3E0`,
and `0x0042E412`. The fixed literal loads and provider calls preserve the stock
ABI while portable models cover the decision and ordering behavior.

Apple clang 21 and Homebrew clang 22 reproduce all 228 authenticated bytes
exactly from mnemonic-only Arm source. Portable tests cover magic-state
classification, event creation, wait retry/termination, and bit publication.
Live retained state, event objects, scheduler wakeups, logging, and failure-reset
behavior is blocked by unavailable physical evidence.
