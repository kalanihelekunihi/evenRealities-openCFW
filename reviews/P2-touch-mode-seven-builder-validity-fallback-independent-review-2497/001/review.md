# Independent review 2497

**Result:** PASS_SCOPED.

Candidate `analysis/touch-mode-seven-builder-validity-fallback-2496/001` receipt SHA-256 `07d2178e95a0e03d6345809796a31dae4fdb36931ef812e075101b56cb0d21ed`; all four artifact hashes and both owned spans validate. The isolated replay passes all 1,440 cases.

The complete tested mode-seven chain executes original firmware instructions. The matrix crosses row validity 0/1/2/3/255, both selector matrices, prior mode 0/7, loader version/selector, readiness, and initial words. The assertions support discrete validity selection: 1 selects configured mode C and its special constructor/group-mask path; 2 selects mode A; the other tested values fall back to mode B and omit the validity-1 group call. Full ordered builder stores and 224-byte buffers, child arguments/order, final mode/status/flags/delays, and R4–R11/SP are checked.

**Limits:** This is bounded to five validity values and supplied selector/config/list inputs. Arbitrary constructor fields, list mutation/aliasing, other validity bytes, and physical hardware remain open; non-builder peripheral writes are diagnostic only. Dependency execution does not establish ownership or completeness. Accepted:false; private scoped evidence only, no canonical admission.
