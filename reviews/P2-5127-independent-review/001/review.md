# Independent review P2-5127

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes, with exact bodies, branch/literal references and the documented four 32-byte frames. Valid and invalid callback paths, callback arguments, post-callback publication, and output/stack aliases follow the decoded code. Null callback reaches logger arguments then the repeated 0x41AC8A loop; no ordinary return is claimed for that path.

## Limits

Indirect callback target and loop-child behavior are unresolved; hardware, C, and admission claims are excluded. Private partial evidence; accepted:false.
