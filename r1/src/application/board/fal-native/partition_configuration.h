/* Pinned fal_partition.c diagnostic coordinates under Clang.
 * Stock reports the opening line (144) of its two-line cache bounds log;
 * Clang's variadic macro location reports the closing line (145). */
#ifndef R1_FAL_NATIVE_PARTITION_CONFIGURATION_H
#define R1_FAL_NATIVE_PARTITION_CONFIGURATION_H
#include "configuration.h"
#undef log_e
#define log_e(...) FAL_PRINTF("\033[31;22m[E/FAL] (%s:%d) ", __func__, (__LINE__ == 145 ? 144 : __LINE__)); FAL_PRINTF(__VA_ARGS__); FAL_PRINTF("\033[0m\n")
#endif
