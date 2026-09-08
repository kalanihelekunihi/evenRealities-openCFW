# GX8002 NPU accessor candidates

Seven accessors have unique stock matches established by fixed object bytes
plus independently decoded branch targets resolving to the known register
primitives. Four other SDK symbols did not match and are not assigned stock
addresses. This is bounded identity evidence, not source admission.

`runtime_gx8002_npu_accessors.c` reconstructs the matched routines. Getters
explicitly preserve both the output store and observed r0 return value;
original private C return types are not claimed. Integer address arithmetic
preserves the observed 32-bit indexed address calculation. The linked
candidate contains only newly compiled C, with no SDK object payload.

| Function | Package | Envelope | C bytes |
| --- | --- | ---: | ---: |
| get over-command address | 0xedec | 16 | 16 |
| get operation-overflow address | 0xedfc | 16 | 16 |
| reset | 0xee0c | 24 | 22 |
| set task head | 0xee24 | 12 | 10 |
| get task head | 0xee30 | 16 | 14 |
| get indexed base address | 0xee40 | 16 | 16 |
| get current-command address | 0xee50 | 16 | 14 |

Getters read offsets260,292,16,index*4,256 respectively, then store the value
to the output pointer and preserve it in r0. Reset sets bit3 at offsets4 and8
in order. Set-task-head writes offset16. Original frames are eight bytes for
getters/reset and four for set-task-head. Validate those observations against
stock/source before admission, including output aliasing where valid, helper
clobbers, order, pointer arithmetic, return values and padding boundaries.

```sh
python3 g2/tools/identify_gx8002_npu_accessors.py
python3 g2/tools/build_gx8002_npu_accessor_candidate.py
```

Evidence: `gx8002-npu-accessor-identification.json` and
`gx8002-npu-accessor-linked-candidate.json`. All seven candidates are now qualified
and registered in the integrated builder; all 427 integration tests pass.

The seven accessors have now passed 42,880 composed stock/source comparisons
and ten regression tests. Primitive execution is decoded, with its leaf ABI
checked independently; accessor calls conservatively clobber caller-saved
registers. Checks include getter output aliasing, observed return values,
unsigned indexed-address wrap, task-head full-width patterns, and reset order.
Original padding bytes after each callable symbol are zero and validated.
These are aligned synthetic-address models, not claims that all modeled
addresses are physically usable or proof of hardware timing.

```sh
python3 g2/tools/verify_gx8002_npu_accessors.py
python3 -m unittest discover -s g2/tests -p test_gx8002_npu_accessors.py
```
