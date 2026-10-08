# Independent review — P2-21405

Status: partial; accepted: false.

Fresh replay passed for the 100-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The prior acquisition tail updates the current counter with wrapping addition, reloads current/high-water independently, selects the high-water value using the unsigned comparison, stores it, and follows the recorded release path. The POP places the saved entry R3 into R1. In the next routine, the old size is loaded and retained before the operation call; the updated size is loaded afterward and the difference is computed with wrapping subtraction.

Later exits remain unresolved, and helper contracts are outside this evidence. Review remains partial/unaccepted.
