# MAX decoder initialization source

The initializer uses the authenticated NationalChip MAX decoder source and
parameter-list type. It reads the live keyword count once, prints the original
diagnostic when the count differs from the shipped model's two outputs, and
always initializes keyword strategy state afterward. The diagnostic is a
source string literal whose66 compiled bytes match stock exactly.

The macOS C-SKY compiler emits32 bytes inside the original interval.846 decoded
stock/source comparisons and six regression checks cover count values,
conditional logging, helper targets and the four-byte frame. The helper models
clobber volatile registers. Strategy init/reset and memset have separate source
qualification; these checks do not claim complete model/decoder behavior.

The next source candidate reconstructs LvpPrintMaxKwsList and its eight-byte
BSS list object. This routine assigns count2 and the source-owned parameter
table pointer before printing, so it performs initialization as well as
logging. It compiles to120 bytes with the original32-byte frame; its five
strings (97 bytes total) match stock. Before admission, its live list count
and pointer reads between printf calls need decoded qualification.

Full integration passed 333 tests. The rebuilt native macOS package passed
artifact verification with the MAX notice included. There are now 134
integrated C functions. The listing/state candidate remains unadmitted, and
the full source-only goal is active.
