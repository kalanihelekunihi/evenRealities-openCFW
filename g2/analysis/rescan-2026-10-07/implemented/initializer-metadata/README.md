# Initializer record extraction

`extract.py` authenticates the locked bootloader and decodes its four 8-byte startup records at433440..433460. It writes callback addresses, priorities, known role labels, image bounds and table/helper hashes. Alternate bounded tables can be selected explicitly. It retains the runner's256-record cap; it does not guess callback implementations or replace the signed wrapping comparator with unsigned Python sorting.

Run `python3 extract.py --output records.json` here and `python3 -m unittest discover -s . -p 'test_*.py'`. Five tests check the actual callback set, image tampering, misaligned extents, image bounds and the256-record cap. The cap test reads a synthetic expanded table extent, not a claim that257 real startup entries exist.

This is an extraction helper for already recovered metadata, not new executable coverage. Source runner and qsort remain at `g2/components/bootloader/init_table/`; prior original-instruction comparisons and seven integrated cases establish their separate bounded behavioral evidence. IAR archive `.rtmodel` and stack metadata do not automatically identify application initialization tables or full C types.
