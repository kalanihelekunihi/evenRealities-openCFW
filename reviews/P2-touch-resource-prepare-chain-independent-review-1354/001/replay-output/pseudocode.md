# Touch resource preparation chain

4C44..4C72 is46 instruction bytes. Follow descriptorword0, then word+8, then word+4 to flagpointer. Nonzero flagbyte returns128. Otherwise load resourceword0 from the intermediate record and call8FA0(resource,2). Nonzero returns8. Zero calls6AC0(1,originaldescriptor), returning its raw result. Restore two-word frame. 4C72..4C7A is six-byte forwarding adapter with its own two-word frame. No pointer guards occur locally.

Receipt-derived originalinstruction fixtures cover bothentries, three flags and three statuses for each explicit controlled deeperhelper. Exact calls/arguments, conversions/rawresult andSP are checked. Pointer validity, deeper effects and concurrency remain unresolved. No canonical admission or C implementation.
