# R1 optical window compaction in C

`native_gomore_optical_compact.c` supplies the stock `0x8eeba` ABI as a tested
C candidate. The [receipt](gomore-optical-compact-c-review.json) binds production
source/object, REA instructions, direct and caller replay, and qualification.
No assembly or persistent RAM is added.

The helper skips zero-count and elapsed-count-at-most-20 states. Otherwise it
scans endpoint halfwords, including the stock sentinel read beyond the counted
records when all entries are dropped. It captures a record's four words before
publishing them, adjusts three halfword indices modulo 65536, reloads the live
count for every retained record and finally subtracts the dropped count. The
checked generic utility keeps its existing behavior under the `_checked` name;
its guarded separate-buffer API is not the native state-block ABI.

The production object passes **1,674 native/C pairs**, including **60 faults**.
Checks cover ordered writes, invalid access location/width, surrounding bytes,
return/SP and preserved registers. An independent byte oracle checks completed
cases. Seven compiled defect controls are rejected, including omitted sentinel
access and reordered stores. The C profile splits stock doubleword loads/stores
into ordered word accesses; physical alignment behavior and bus atomicity remain
outside this evidence. Replay alone does not prove those hardware properties.

The actual native optical estimator passes **1,344 gap/reset/warmup pairs** with
both this helper and the production C history append substituted: **5,088 calls
to each**. The native filter and reset routines execute. State/output bytes,
external write order, FPSCR, native root return and helper arguments/stack depths
agree. The heavy estimation path is not covered and its C root remains unresolved.

The normal source build compiles **691 units** with no failures or duplicate
strong symbols. **179 application / 34 bootloader imports** remain. All 689 prior
units except the renamed generic owner retain source/object hashes. Qualification
selects no replacement; canonical source-plan and hybrid totals remain unchanged:
4,369 source-built executable bytes, 641,791 stock executable bytes, 248 resource
bytes. The hybrid output still equals stock because most executable bytes remain
stock pull-through. No complete C link, byte identity or physical validation is
claimed.
