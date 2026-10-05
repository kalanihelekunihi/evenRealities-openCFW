# Lossless display resource shortcut

Run `python3 g2/analysis/shortcut-batch-2026-10-05/resources/extract.py` from this checkout. It authenticates the official Apollo payload and checks six descriptors against the prior original-instruction storage-admission proof. Each asset becomes a grayscale PNG and exact raw L8 file, with address/range/hash/consumer provenance in `extraction.json`. PNG is an inspection format; firmware reuse requires original pixel bytes and appropriate descriptor relocation, not PNG insertion.

Six round trips, one held-out descriptor and one wrong-color rejection pass. The independent decoder verifies PNG CRCs, dimensions and pixel equality. This is storage decoding, not a live LVGL renderer or display fidelity test. No new Unicorn runs are claimed; the eight prior original-instruction cases remain the consumer-boundary evidence with their explicit allocator/cache/alignment stubs.

These are immutable image resources in the stored Apollo payload, not runtime scanout buffers. The 28,872 unique bytes were already classified; newly classified bytes are zero. Other 422 candidates, fonts, compressed formats and external NOR resources remain outside this recipe. One visual inspection shows a certification-style graphic; that does not prove artwork authorship or global UI usage.

Official firmware and extracted assets retain their vendor rights; root MIT does not cover them (root NOTICE). Redistribution permission is not established. Generated PNG/raw files stay local and are ignored specifically here. Tool, provenance and validation remain visible. Do not publish the pixel files as openly licensed assets.
