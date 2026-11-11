# R1 optical reset and filter configuration in C

`native_gomore_optical_reset.c` supplies stock `0x71dd8` and `0x71d62` as C
candidates. The [receipt](gomore-optical-reset-c-review.json) binds production
source/object, REA, replay and qualification. No assembly or persistent RAM is
added. The generic guarded callback utilities retain their behavior under the
`_checked` suffix; they do not represent the native ABI.

Reset clears 1,736 bytes through EABI, publishes the stock state fields and two
negative-one smoother words, clears the 250-word history and constructs raw
parameters `0x3d23d70a` / `0x3ea3d70a` in the same 16-byte caller frame. It invokes
filter setup with mode two and order two, then returns zero. Setup uses the stock
signed mode comparison, preserving negative mode words. It calls the appropriate
coefficient generator, publishes count or doubled count after that provider,
and interleaves four stores at offsets 64 and 48 as in the native tail.

The production object passes **396 native/C cases**, including **22 faults**, with
actual stock coefficient generators, math and EABI clearing executing. Another
**2,060 cases**, including **406 faults**, model the coefficient providers to
exercise full count/mode words, aliases, mutations and caller-saved clobbers.
Checks include state/output bytes, ordered writes, partial failures, invalid
access locations/widths, FP status, preserved registers, raw returns and exact
provider arguments/stack depths. Reset's parameter bits and pointers are checked.
Independent checks assert history clearing, smoother values and configured count.
Eight compiled defect controls are rejected.

The actual optical estimator passes **1,344 gap/reset/warmup pairs** with C reset,
configuration, append and compaction substituted. This executes **384 resets**,
**5,088 compactions** and **5,088 appends**. The native coefficient generators and
filter execute. The heavy estimator path remains outside this replay and its
C implementation is still unfinished. Constant stores can compile to integer
instructions instead of native VFP stores; physical alignment behavior remains
unverified. Private frame bytes are excluded.

The normal source build compiles **692 units**, with no failures or duplicate
strong symbols. All **690 prior units** outside the renamed generic owner retain
source/object hashes. Application imports increase from 179 to **181**, exposing
the low/high and bandpass coefficient generators; bootloader imports remain **34**.
Qualification selects no replacement. The canonical plan and hybrid totals remain
4,369 source-built executable bytes, 641,791 stock executable bytes and 248 resource
bytes. Hybrid equality does not establish a complete C link or source byte
identity. No physical validation is claimed.
