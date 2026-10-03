# Independent review 2961/001

**PASS_SCOPED**; `accepted` remains false.

The isolated 192-case replay passes and output hashes match. Source plus caller/classifier/decoder/save body pins match the locked image. The cases exercise float32 −274, 1000, +infinity, and quiet NaN across choices, flags, clock values, and masks. The original classifier returns category 4; the caller performs the category/threshold and zero-bound writes, returns 6, and stops before decoder or state publication. R4–R12, SP, and PRIMASK restoration pass.

Boundary values and other snapshot/transition paths, aliasing, and physical hardware effects remain outside scope.

Candidate receipt SHA-256: `4bb7be4dd93928eb96725010d8168f914a23fe2b17b60a1d8982e7069d2dddd4`.
