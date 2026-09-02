# G2 bootloader event-control wrapper source closure

Three small runtime services are now source-owned MIT C: the event-wait-one adapter at `0x0042E2EA`, guarded context teardown at `0x0042E3CA`, and event-bit publisher at `0x0042E444`. Their provider edges target the reviewed wait, guarded-action, and event-flag services.

Apple clang 21 and Homebrew clang 22 reproduce the authenticated 14-, 22-, and 20-byte bodies exactly from mnemonic-only Arm source. Portable host tests cover constant wait masks, null/non-null teardown behavior, context clearing, and bit-to-mask conversion. Live event-object behavior is blocked by unavailable physical evidence.
