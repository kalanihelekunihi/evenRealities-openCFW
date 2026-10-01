# Independent review 2175: median and averaging filters

**Result: PASS_SCOPED.** Candidate `analysis/touch-median-average-filters-2172/001` remains unaccepted.

Independent decoding and replay confirm the full-width unsigned median and wrapper’s ordered history updates. The average helper’s mask selects either two- or four-sample averaging; in the four-sample path history shifts from index 2 to 4, then index 0 to 2, before original sample/output stores.

All 1,154 isolated cases passed and matched frozen JSON; exact source, three body spans and listed artifacts hash-check. The fourth average input is fixed at 12345 and only two representative mode values are tested. Aliasing, concurrency, and physical meaning remain unproven. No canonical records changed.
