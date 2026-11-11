# R1 respiratory update in C

`native_gomore_respiratory.c` supplies stock stage `0x60680`. The
[receipt](gomore-respiratory-c-review.json) binds production source/objects, REA,
root/boundary/coordinator/host replay, defects, consolidation, qualification and
composition. The superseded unused generic root and declaration are removed.
No inline assembly or persistent RAM is added.

The root retains capped missing-history fills, byte-load order, interleaved square
sums, raw encoded checks/clamps, signaling comparisons, error/gap flags, confidence
penalties, ordered history shifts and selected-output aggregation. Native software
FP conversion/arithmetic interfaces are used explicitly; ordinary double casts
would change some raw-pattern behavior. Selected confidence is reloaded after the
mean so aliases into the selected slot retain native effects. Existing C history,
statistics and clear helpers supply those lower operations.

A 44-byte scratch object produces the exact 96-byte respiratory frame, with
estimator rate/confidence pointers at entry SP minus 80/minus 84. The coordinator
now reserves 56 additional private bytes in C, producing its stock 112-byte frame.
Host-entry-relative optical pointers/SP consequently match (-640,-644,-656),
without normalization. The reservation adds one private byte write; private frame
contents are excluded. The outer sensor-update caller's separate frame difference
remains open.

Production replay passes **2,792 root cases**, with raw FP boundaries/seeded values,
output aliases, unavailable flags, estimator mutations and caller-saved register
clobbering. All six estimator arguments, frame/pointers, record/output, flags,
FPSCR and preserved registers agree. Return flags have independent expectations.
**51 boundary cases**, including **47 faults**, match partial writes and invalid
accesses. Nine defects compiled from production source are rejected.

The adjusted production coordinator passes **4,512 ordered-call/state oracle
cases**. Actual host/coordinator/respiratory integration passes **334 cases**,
including nine faults and 3,259 modeled calls, with full contexts and exact optical
pointers/SP checked. History/statistics/clear C objects are linked; software FP,
square root and EABI byte clearing execute natively. Optical estimation is modeled;
host replay also models logging and fifteen other stage providers. This does not
establish a completely source-executed graph or physical device behavior.

The normal build compiles **689 units** (615 application, 74 bootloader), with
**179 application and 34 bootloader unresolved imports**. All **686 previous units
outside the generic owner and coordinator** retain identical source/object hashes.
The respiratory-stage import is replaced by optical estimator `0x69834`; the
import count stays unchanged. Source checks and relocatable composition pass
without new failures or duplicate strong symbols.

Qualification selects no new replacements and the canonical source plan remains
unchanged. Hybrid raw equality still includes executable stock pull-through.
Physical validation, concurrency/private frame behavior, full source-only final
linking and byte-identical reconstruction remain unproven. Reproduction artifacts
are under `build/goal-r1-gomore-respiratory-c/`; the normal report is
`build/sources-goal-r1-gomore-respiratory-c/report.json`.
