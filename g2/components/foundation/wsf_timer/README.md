# Stock timer cancellation subset

See [analysis](../../../analysis/radio-timer-stop-2026-10-05/REPORT.md) and [independent review](../../../analysis/radio-timer-stop-2026-10-05/review/report.md). SOURCE_PROVENANCE.json identifies pinned Cordio Apache-licensed bodies; body notices are retained. Sparse stock cancellation layout uses next@0/started@13; middle fields are intentionally opaque.

Build with `make -C g2 ambiq-gpio-config-simulator`. The linked provider includes actual WSF critical instructions and real GPIO providers, without executable stubs. Verifier compares original instructions/source/independent model. It does not prove callback drain, asynchronous lifetime, hardware shutdown or byte equality.
