# P2-15865 independent review

Fresh replay passed all 2,048 original calls without hooks. Inactive cases preserve the global pointer and flag. Active cases use a zero counter and verify the post-wait flag clear and pointer zeroing. The fixture checks global RAM, local RAM outside the documented 32-byte nested-stack area, branch-dependent R0, the R1 entry-R3 alias, callee-saved registers, SP/PC/PRIMASK, and unchanged flash.

The active path’s nonzero-counter delay/timeout behavior, faults, aliases, and concurrency are outside scope. The RAM model does not qualify physical clock behavior. Status remains partial and unaccepted.
