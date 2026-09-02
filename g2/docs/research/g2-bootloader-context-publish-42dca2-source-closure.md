# G2 bootloader runtime-context publisher source closure

The complete 114-byte function at `0x0042DCA2..0x0042DD14` is now
source-owned MIT C. It validates the retained queue, publishes the two-word
runtime context without waiting, and raises event mask `0x00400000` on success.
Its only callers are `0x0042E33A` and `0x0042E364`.

Apple clang 21 and Homebrew clang 22 reproduce every byte exactly from
mnemonic-only Arm source under four strict provider relocations. Portable tests
cover absent queues, send failure, successful notification, and preservation
of existing event bits. Live retained RAM, RTOS queue/event, scheduler,
logging, timing, interrupt, reset, and cold-boot behavior is blocked by unavailable physical evidence.
