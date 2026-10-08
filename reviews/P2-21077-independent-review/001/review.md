# P2-21077 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FDB4..0x47FE12 (94 bytes); instruction/reference outputs match candidate. The tail performs three separate global-word RMW reads/stores, then records the helper result in SP8 and executes PRIMASK save/restore around the mapped helpers. The byte query and callback return values are ignored; the final guard uses an independent fresh word read before a conditional OR6. FDB4 tail paths return explicit zero and use POP aliases that may reflect prior slot writes. The full-error path from 21470 bypasses this tail at FE10 and retains its full result; the nonzero guard path from 21472 branches into this tail but skips the earlier extraction. These path distinctions remain.
