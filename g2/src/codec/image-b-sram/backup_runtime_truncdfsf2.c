/* Compiler-rt llvmorg-20.1.8 binary64-to-binary32 helper, pinned upstream.
 * The old C-SKY GCC diagnoses one upstream signed/unsigned comparison under
 * -Werror; preserve upstream bytes and narrow the diagnostic to this include.
 */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#include "../../../../third-party/upstream/llvm-compiler-rt-format-20.1.8/truncdfsf2.c"
#pragma GCC diagnostic pop
