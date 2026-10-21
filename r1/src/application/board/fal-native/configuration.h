/* Stock FAL configuration: error printf routing, no info/debug output.
 * Included after fal.h to avoid changing the authenticated upstream sources. */
#ifndef R1_FAL_NATIVE_CONFIGURATION_H
#define R1_FAL_NATIVE_CONFIGURATION_H
#include <fal.h>
#undef FAL_PRINTF
#define FAL_PRINTF(...) printf(__VA_ARGS__)
#undef log_i
#define log_i(...) ((void)0)
#undef log_d
#define log_d(...) ((void)0)
/* Native lookup/init assertion paths print once and do not return. */
#undef assert
#define assert(EXPR) do { if (!(EXPR)) { FAL_PRINTF("(%s) has assert failed at %s.\n", #EXPR, __func__); while (1) {} } } while (0)
#endif
