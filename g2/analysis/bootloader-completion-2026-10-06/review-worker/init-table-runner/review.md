# Initializer sort and runner review

The standalone source component at `g2/components/bootloader/init_table/`
implements the recovered consumer at `0x41f9f8`, its fixed no-argument table
entry for `0x433440..0x433460`, its wrapped priority subtraction comparator,
and the qsort implementation at `0x423d08/0x423a48`.
There is no qsort provider cut: stock execution runs the locked image's original
instructions, while source execution is restricted to the standalone ELF and
its explicit callback fixtures.

The current receipt is
[`comparison-qsort-extended.json`](comparison-qsort-extended.json), status
PASS. It compares all eight bytes of every record between original and source
for 98 direct qsort inputs: the original targeted edge cases plus 90
deterministic ascending, descending, random-permutation, duplicate-heavy, and
equal-key cases spanning counts 2 through 256. It also compares five runner
fixtures, including a no-argument source entry using the fixed four-row table,
equal keys and null callbacks, empty input, and the 257-row cap, plus five
comparator cases including wrapped subtraction. The receipt records 1,042
distinct original instruction bytes. The ELF hash is
`89f5cab4a4b38e6fb67d895f7e997b95bdefe92a906e62ab5971a52ca35de1b4`.

This is strong differential evidence for the exercised record size (8) and
input distributions; it is not an exhaustive proof over arbitrary qsort inputs,
record widths, or byte identity. No fixture is confirmed to force stock's
introsort heap-fallback branch. Callback addresses in isolated runner cases are
synthetic RAM functions. The fixed-table case uses external cuts at the four
stock callback addresses. Three callback wrapper bodies (`0x4301d6`,
`0x43194c`, `0x415590`) are compared separately in
[`initializer-callbacks/comparison.json`](../initializer-callbacks/comparison.json);
allocator init `0x41fd70` has a separately owned source component. Their
platform and HAL callees remain explicit dependency cuts, and no startup ELF
links the full fixed-table callbacks together. No peripheral behavior or full
bootloader completeness claim follows from these profiles.
