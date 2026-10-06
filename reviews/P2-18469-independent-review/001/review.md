# Independent review P2-18469

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay produced the pinned 88-byte span `0x4601EA..0x460242`, and the instruction/reference manifests match the candidate. The wrapper's global address is loaded into R1 and used for the initial word load. On the nonzero path, a separate fresh global load is passed to `0x44981C` while R1 still contains the global address and incoming R2/R3 remain live; there is no second null check. Child result is discarded by the shared epilogue.

On the zero route, the three flag-derived calls use distinct fresh `0x43D0CE` results. The bit-1 path constructs the documented stack/literal arguments and calls `0x43D574`; the bit-0/bit-2 branches select `0x43CE9E` or skip it. The diagnostic path writes the 86 value at SP0 and the referenced literal at SP4. POP loads those current stack slots into R0/R1 and the saved incoming R7 into R2, then returns through saved LR; thus it does not return a child result or explicit boolean. The separate mask reads and conditional flow were checked.

Child contracts and broader global ownership remain unresolved. No source, gate, or admission changes.
