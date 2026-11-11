# Sleep report request wrapper in C, 2026-11-10

`r1_health_notification_stage_0008b818` is now ordinary C in
`r1/src/application/runtime/native_health_notification_stages.c`. The pinned
2.2.6.0009 application has a 22-byte instruction body at `0x8b818`: it writes
the low byte of the first argument and low halfword of the second into a
four-byte stack request, then calls the sleep iterator at `0x5b39c` with
mode 1, callback `0x8f954`, and the request address. The C request has the
same byte and halfword offsets and passes the source-owned report callback.
The padding byte remains outside the contract. This removes one handwritten
assembly entry; the other notification stages in the same file remain assembly.

The R1-only source build receipt is
`build/sources-r1-sleep-wrapper-c-final-20261110/report.json`: 887/887 application
and 82/82 bootloader units compile with no known failures or duplicate strong
symbols. The strict bootloader link passes with a valid vector. The strict
application still has 32 unresolved functions and 26,712 bytes of flash load
overflow, exactly the preceding link totals. The sleep iterator itself remains
unimplemented. This check establishes the wrapper's source and call boundary;
it does not establish physical behavior or byte identity.
