# R1 RTC epoch-initialization review

The existing C epoch initializer matches stock in 720 controlled execution
comparisons. No source body or composition eligibility changed. REA observes
the complete 102-byte native body at `0x5649C..0x56501`, inclusive.

The recovered order is significant: null request returns four before touching
the counter; otherwise the request's 16-bit offset at +48 is stored before
name/open validation. A name mismatch or unopened record returns 17 while
retaining that offset update. On success, epoch at +44 is read after the
comparison, stored into the counter and converted to a discarded calendar;
the function then returns zero. No full-table scan is introduced.

Tests cover four epochs including wrap and the 2100 boundary, five offset
words including both signed extremes, three opened-byte values, three
comparison results, null/non-null requests and request mutation during
comparison. The mutation cases confirm that the stored offset remains the
pre-comparison value while successful epoch adoption sees the changed request
word. Complete controlled record/counter/request bytes, return status and
counter state visible to the comparison provider agree. String comparison is
mocked; the C calendar kernel is actually linked and executed.

This closes the epoch initializer's tested contract, not the full lifecycle.
Open, driver setup and registration still require their own review, so the
lifecycle unit remained excluded at this stage. The later
[lifecycle review](rtc-lifecycle-review.md) checks open/registration and
includes the lifecycle and C driver bridges in composition. Private calendar scratch, gmtime state,
arbitrary invalid pointers, full fault snapshots, hardware operation and exact
instruction identity are not established. Composition remains at 238
application and 34 bootloader imports; no source-plan or gate changed.

[rtc-epoch-review.json](rtc-epoch-review.json) binds the unchanged source and
object, prior complete-build report, case results and REA observations. Probes
remain under ignored `build/goal-r1-rtc-epoch/`.
