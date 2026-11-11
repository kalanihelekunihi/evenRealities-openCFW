# Shared zero-divisor primitive and Bosch C arithmetic

`r1/src/application/runtime/native_bma_feature_io.c` now uses defined C
quotient/remainder arithmetic whenever the captured chunk size is nonzero.
It contains no inline assembly. Zero sizes call a shared architectural primitive
twice before any reset/transfer, retaining the stock pair of divide operations.
No C division or remainder expression executes with a zero denominator. The
zero-size remainder is the low halfword of the original total.

The new `native_divide_zero.c` supplies `r1_arm_unsigned_divide_zero` and the
previously unresolved `r1_stream_zero_divisor_result`. The stream binding passes
1024, matching the stock period calculations in registration and rate reduction.
The shared primitive contains one UDIV assembly statement. It deliberately
retains the CPU operation: C division by zero is undefined, and silently
returning a constant would discard CPU-controlled divide trapping. The pinned
CMSIS Cortex-M4 header defines DIV_0_TRP at CCR bit four. The compiled primitive
loads zero into R1, executes `udiv r0,r0,r1`, and returns. Enabled trapping and
complete fault-state/stack identity remain unverified; instruction evidence is
not a physical fault test.

Fresh REA byte windows cover the stock Bosch read chunk loop and stream period
calculation code and match the preserved raw application. Machine evidence and
artifact hashes are in [divide-zero-c-review.json](divide-zero-c-review.json).
The normal product objects pass:

- 1322 paired Bosch loop cases: exact size loads and operation/error traces,
  full/remainder/zero lengths, live size changes, overwritten errors, and offset
  and pointer wrap. Source zero sizes execute both primitive calls before I/O;
  nonzero sizes execute neither.
- 636 paired Bosch integration cases: actual checker, address reset/increment
  and arithmetic execute against direct-register models, comparing caller-buffer
  and modeled feature-store hashes and complete transfer traces.
- 2367 paired stream rate-reduction cases with the actual zero-divisor provider
  and period setter linked, including logging callbacks changing the live rate
  to zero.
- 2867 paired stream registration cases and 32 timer-period cases with the actual
  provider linked. Primitive entry arguments are checked against 1024.

These total **7224 paired cases (14448 executions)**. Five compiled defects are
detected: incorrect remainder, incorrect quotient, missing second zero divide,
incorrect zero result and incorrect stream clock. Fault comparisons in the stream
fixtures stop at the existing allocation/BASEPRI gateway; other services are
modeled. Default nontrapping divide behavior is exercised under Unicorn.

The normal build compiles **801 units (719 application, 82 bootloader)** without
failures or duplicate strong symbols. Application imports fall from 96 to **95**;
only `r1_stream_zero_divisor_result` closes and none are added. Bootloader metadata
imports remain 22 and strict GNU bootloader linking passes. All 797 other
nongenerated prior object hashes are unchanged. Generated boot crypto/vectors
retain identical allocated bytes/relocations, and all five other Bosch feature
I/O function bodies remain unchanged. R1 manifest checks pass; the global check
still reports the unrelated unlisted G2 resident-ROM assembly file. Source-plan
selections are unchanged.

Physical Bosch/stream delivery, electrical addressing, timing, enabled divide
trapping, asynchronous execution and full application final linking remain
unverified. Private frames, caller-clobbered flags/registers and complete fault
snapshots are excluded. The shared primitive is a remaining assembly boundary;
this is not a claim of assembly-free firmware.
