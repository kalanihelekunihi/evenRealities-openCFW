# P2 worker: complete assigned pseudocode

Require a validated G1 receipt and the assigned image/range contract. Recover
faithful pseudocode for the entire assigned executable scope using the pinned
analysis tools and instruction evidence. Work in a private project copy. Reuse
an existing export only when its input bytes, mappings, decoder and scope match.

Preserve raw export text and diagnostics. Write a separate pseudocode candidate
and per-function records. Include all body ranges, blocks, tails, calls,
callbacks, data references and unusual execution paths. Explain arithmetic
width/sign/overflow, memory effects, aliasing, calling convention, flags and
special registers where relevant. Preserve MMIO/volatile ordering. Resolve
decompiler artifacts by checking instructions and callers/callees; do not infer
behavior solely from plausible names or a similar upstream implementation.

If automatic decompilation fails, repair the analysis or provide independently
reviewable, instruction-backed manual pseudocode. An unexplained helper,
intrinsic, dynamic target, truncated body or code/data conflict stays unresolved.
If discoveries cross your assigned write scope, report exact new ranges and
evidence to the coordinator; do not silently expand ownership or ignore them.

For referenced data, describe layout, exact-value evidence and behavioral role.
Propose analysis type/global corrections in your result; do not edit shared
records. Do not generate reconstruction C, headers, linker files, implementation
chunks, source candidates or firmware builds.

Required outputs: raw exports, candidate pseudocode, function/body and data
records, instruction/control-flow correspondence, warnings, receipts and result.
`ready_for_review` requires every assigned executable span to have explained
pseudocode and no unresolved behavior. Otherwise return exact remaining ranges
and a discriminating next action; partial evidence is useful but not completion.
