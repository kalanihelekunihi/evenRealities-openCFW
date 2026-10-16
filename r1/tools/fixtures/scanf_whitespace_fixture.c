/* Verification-only ASCII whitespace callback; not a native ctype provider. */
#include <stdint.h>
int32_t r1_scanf_whitespace_fixture(int32_t ch){return ch==32 || (uint32_t)ch-9u<5u;}
