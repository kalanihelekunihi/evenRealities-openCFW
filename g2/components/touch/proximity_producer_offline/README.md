# Independent offline proximity CPU producer

See [analysis](../../../analysis/touch-proximity-producer-closure-2026-10-08/REPORT.md).

ARM32 recovered interfaces in proximity.h implement raw filters0x50a0, raw processing0x5938 and proximity debounce0x5a0a. Caller supplies coherent widget/context/sensor/history pointers and acquired raw counts. No production build or hardware validation is implied. Baseline/difference/IIR dependencies reuse sealed slider_producer_offline source.
