# Independent review P2-18479

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 106-byte prefix `0x460374..0x4603DE`, with matching instruction/reference manifests. The function saves R5-R7/LR and uses a 16-byte frame. The initial `0x43D0CE` result drives the bit-1 route; its diagnostics write 250, the literal at `0x460D60`, and 279 to SP8/SP4/SP0 respectively before the later `0x43D574` call. These local slots alias the saved R5-R7 words. The alternate route makes distinct fresh `0x43D0CE` calls for bit 0 and (only when bit 0 is clear) bit 2. The bit-2-set route calls `0x43CE9E` with the recorded arguments.

At `0x4603C0`, the code unconditionally stores 250 through the literal at `0x460E08` plus 12. It then checks the global addressed by `0x460E0C`. If nonzero, it separately reloads it without retesting null and calls `0x45F840` with key 3 and live R2/R3; zero child result branches to the external epilogue, while nonzero execution exits this mapped interval at `0x4603DE`.

The continuation and epilogue remain outside the candidate span; no broader return, state, or child semantics are inferred. Partial/unaccepted only.
