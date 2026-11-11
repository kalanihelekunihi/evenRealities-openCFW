# Logger containing-object byte access

The logger now passes a byte view of its containing frame to clear, formatter,
concatenation and callback providers. Stock lengths 246/247 can put suffix bytes
past the 256-byte message member into the adjacent sentinel; using the whole
object representation keeps that access within the containing object's extent.
Static assertions pin the sentinel and varargs offsets at 256 and 260 bytes.

The [receipt](gomore-log-object-c-review.json) verifies that **all 684 compiled
objects and both relocatable composed outputs are byte-for-byte unchanged**.
Only the logger source changed; the other 683 sources are unchanged. All **4,390
direct logger cases and 72 stock-formatter cases** pass again, including exact
published pointers and suffix spill cases. The normal build remains **684 units**
with **164 application and 34 bootloader imports**, without failures or duplicate
strong symbols. The canonical source plan is unchanged.

The previous [logger review](gomore-log-c-review.md) retains its original evidence
scope. This source-representation correction does not prove private frame aliases,
physical device behavior, a complete source-only final link or native byte identity.
Qualification and hybrid packaging were not repeated because every object and
composed output is identical to the prior checkpoint. The current report is
`build/sources-goal-r1-gomore-log-object-c/report.json`.
