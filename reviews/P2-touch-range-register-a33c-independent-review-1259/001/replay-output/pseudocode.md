# Touch range-selected register A33C

Unsigned input<=16 selects mode0, input17..32 selects mode1, and input>32 selects mode2. A fresh word read at40100030 replaces bits1..0 with thatmode and stores. A second fresh read clears bit4 and sets it iffmode is nonzero, thenstores. RawR0 returns3, not a successstatus. No frame, helper or inputrejection exists. BodyA33C..A36E excludes trailingNOP/literalpool.

Twenty-one original-instruction fixtures check unsignedthresholds, three initialwords, two reads, orderedwrites, rawreturnandSP. The second read sees the first store in these static synthetic fixtures; physicalfreshread changes and registermeaning remain unresolved. No canonical admission or C implementation.
