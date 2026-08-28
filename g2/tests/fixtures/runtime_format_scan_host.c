/* SPDX-License-Identifier: MIT */
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

#include "../../components/shared/runtime/runtime_format_scan.c"

int open_cfw_test_scan_integers(
    const char *input,
    int *decimal,
    unsigned int *hexadecimal,
    unsigned int *octal,
    int *automatic
)
{
    return open_cfw_runtime_sscanf(
        input, "%d %x %o %i", decimal, hexadecimal, octal, automatic
    );
}

int open_cfw_test_scan_lengths(
    const char *input,
    signed char *byte,
    short *half,
    long long *wide,
    size_t *size
)
{
    return open_cfw_runtime_sscanf(input, "%hhd %hd %lld %zu", byte, half, wide, size);
}

int open_cfw_test_scan_text(
    const char *input,
    char *word,
    char *letters,
    char *raw,
    int *consumed
)
{
    return open_cfw_runtime_sscanf(input, "%5s %3[a-z]%2c%n", word, letters, raw, consumed);
}

int open_cfw_test_scan_inverted(const char *input, char *value)
{
    return open_cfw_runtime_sscanf(input, "%4[^0-9]", value);
}

int open_cfw_test_scan_floats(
    const char *input,
    float *first,
    double *second,
    double *third
)
{
    return open_cfw_runtime_sscanf(input, "%f %lf %la", first, second, third);
}

int open_cfw_test_scan_bounded_float(
    const char *input,
    float *first,
    float *second,
    double *third
)
{
    return open_cfw_runtime_sscanf(input, "%2f%3f %5la", first, second, third);
}

int open_cfw_test_scan_exponent_width(
    const char *input,
    float *value,
    int *consumed
)
{
    return open_cfw_runtime_sscanf(input, "%2f%n", value, consumed);
}

int open_cfw_test_scan_suppressed(const char *input, unsigned int *value)
{
    return open_cfw_runtime_sscanf(input, "%*s %u", value);
}
