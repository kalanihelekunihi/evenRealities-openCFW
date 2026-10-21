/* SPDX-License-Identifier: MIT */
#ifndef G2_EXTENDED_LOG_ROOT_CANDIDATE_H
#define G2_EXTENDED_LOG_ROOT_CANDIDATE_H
#include <stdint.h>
struct g2_extended_log_product {
    volatile uint8_t *state;
    char *buffer;
    const char *fatal_module, *fatal_file, *fatal_function, *fatal_format;
    const char *const *level_headers, *const *level_colors;
    const char *level_prefix, *module_suffix, *separator;
    const char *function_prefix, *function_suffix, *line_format;
    const char *line_suffix, *normal_suffix, *message_suffix;
};
extern const struct g2_extended_log_product g2_extended_log_product;
#endif
