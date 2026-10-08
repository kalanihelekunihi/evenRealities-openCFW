# Offline saturated-count integer correction and max-raw wrapper

Independent ARM32 interfaces are in max_raw.h. [Evidence and limits](../../../analysis/touch-max-raw-closure-2026-10-08/REPORT.md).

The saturated-scan callback is an explicit external boundary. This module cannot acquire samples, establish a physical maximum count or replace the complete MSCLP lifecycle. It preserves unsigned32 arithmetic and write-on-error behavior of the recovered wrapper.
