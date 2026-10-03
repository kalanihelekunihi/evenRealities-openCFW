# Independent review 2651: stepwise profile handler

**Result: PASS_SCOPED.** `accepted` remains false.

The source, code spans, lookup table, and candidate artifact hashes match. I reran a replay copy into a fresh isolated directory; all 1,600 fixtures pass. The original stepwise handler, selector, and lookup copy execute; only indirect handler destinations are synthetic.

The code walks one unsigned integer step at a time from old to new, calls the selector with each adjacent pair, and skips handler dispatch on a nonzero selector result while continuing the walk. Handler arguments use the original final `(new, old, newsecond, oldsecond)` values, and handler return values are ignored. The stack byte starts at 26 and retains the final selector-written index; equal endpoints perform no iterations and retain 26. Return registers, preserved registers, SP, and sentinel return match the fixture assertions.

Indirect handler behavior and actual table contents remain unresolved. The tested endpoint range is 0 through 19; larger walks, out-of-range table indices, concurrency, and ownership are outside scope. This is private evidence, not canonical admission.
