/* Not stock: minimal <inttypes.h> for the freestanding arm-none-eabi clang profile
 * (int32_t is int, int64_t is long long) used by LVGL logging formats. */
#ifndef G2_LVGL_INTTYPES_H
#define G2_LVGL_INTTYPES_H
#include <stdint.h>
#define PRId32 "d"
#define PRIu32 "u"
#define PRIx32 "x"
#define PRIX32 "X"
#define PRIi32 "i"
#define PRId64 "lld"
#define PRIu64 "llu"
#define PRIx64 "llx"
#define PRIuPTR "u"
#define PRIxPTR "x"
#define PRId16 "d"
#define PRIu16 "u"
#define PRId8 "d"
#define PRIu8 "u"
#endif
