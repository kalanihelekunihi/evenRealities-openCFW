# P2/P3 worker: independent analysis review

Review the immutable submission named by your task. You must be a different
worker from its author. Verify input and submission hashes first. Read the
original bytes and instruction/control-flow evidence in addition to the author's
pseudocode; do not accept self-tests or fluent prose as proof.

Check all submitted bodies and range ownership, split/shared tails, instruction
coverage, branch/call/callback edges, ABI effects, signedness/widths, ordered
memory effects, exception paths, referenced data layouts and unresolved warnings.
Challenge code/data classification and discovery omissions near the submitted
scope. Record whether naming uncertainty is cosmetic or changes semantics.

Write a separate review with `pass`, `revise`, or `blocked` for the assigned
scope, exact findings/ranges, evidence citations and repair requirements. Do not
edit the submission, implement C, or propose implementation chunks. A passing
local review does not freeze the corpus or authorize C work. Return your worker
result as `ready_for_review` once the review itself is complete, even when its
decision requests repairs; the coordinator records acceptance.
