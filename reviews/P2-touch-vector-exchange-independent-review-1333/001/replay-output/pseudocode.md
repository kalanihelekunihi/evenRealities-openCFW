# Touch vector exchange A274

Body A274..A29C is 40 instruction bytes, followed by three literals. Freshly read system base+8 and compare against RAM vector base. If unequal, load and return the word at flash vector base + 4*u32(index+16), ignoring callback input. If equal, zero callback reaches BKPT A298; otherwise load old RAM vector word at the same modular index, store callback and return old word. No stack frame or index guard exists. Breakpoint continuation branches into the write path but is not executed by these fixtures.

Thirty original-instruction fixtures cover five signed indices, three callback words and both vector-base cases. Exact destination writes, returned old words and guard stops are checked; physical vector activation, architectural index validity and concurrent access remain unresolved. No canonical admission or C implementation.
