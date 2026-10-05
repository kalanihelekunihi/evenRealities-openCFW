# Transport pad dispatcher and release boundary

`0x52df12` first dereferences a transport wrapper: instance u32@0, HAL handle u32@4, initialized byte@8, power byte@9. Instance>=9 returns1 immediately. Otherwise it calls `0x4c2e30(instance,0)`, HAL disable0x55c430(handle), conditional power0x55c7e8(handle,2,1) when byte9 is nonzero, clears byte9, calls uninitialize0x55c286(handle), clears byte8, and returns0. All subordinate statuses are ignored. Handle and caller's global handle pointer are not cleared. This is static call-chain evidence, not a tested release implementation.

The implemented/tested provider is only0x4c2e30:

```c
void transport_pads_raw(uint32_t instance,uint32_t command) {
    if (instance >= 8) return;
    uint32_t key = (uint8_t)command | (instance << 2);
    // key4*k: four pads; key4*k+1: first and third pads; otherwise no-op.
    // Each call reloads configuration word78ee48 and ignores HAL status.
}
```

| Instance | Command0 ordered pads | Command1 ordered pads |
|---|---|---|
|0|5,7,6,50|5,6|
|1|8,10,9,51|8,9|
|2|25,27,26,11|25,26|
|3|31,33,32,13|31,32|
|4|34,36,35,16|34,35|
|5|47,49,48,17|47,48|
|6|61,63,62,117|61,62|
|7|22,24,23,19|22,23|

Command is not boolean: instance0/command4 selects group1; instance1/command8 selects group3. Other combined keys generally no-op. Raw command truncates tobyte first; instance staysu32 and is checkedbefore shifting. Instance8, accepted by release's `<9` guard, performs no pad writes here. The dispatcher returns void; residualR0 differs by branch and is not a defined status.

Each config writes PADKEY73, pad value, PADKEY0 while preserving incoming PRIMASK. Masking is per pad call, not across the dispatcher. GPIO validation failure skips that pad's MMIO but does not stop subsequent calls. Stockconfiguration3 is authenticated data; perturbations test ignored errors/ordered rereads but do not establish physical electrical behavior.

No timer queue, allocation, buffer ownership, pending NVIC, command queue, callback or task state is changed by this provider. Full release needs HAL disable/power/uninitialize and command-queue release. Disable itself depends on command queue handle@0x828 and0x53909a; these are precisely outside this batch. No shutdown-safe claim.
