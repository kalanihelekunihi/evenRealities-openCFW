/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 decimal-scaling helper.
 */

static double open_cfw_test_decimal_scale_multiply(
    double left,
    double right
);

#define OPEN_CFW_DECIMAL_SCALE_MULTIPLY(left, right) \
    open_cfw_test_decimal_scale_multiply((left), (right))

#include "../../components/apollo_main/core_overlay/runtime_decimal_scale.c"

union open_cfw_test_decimal_scale_bits {
    double value;
    unsigned long long bits;
};

unsigned int open_cfw_test_decimal_scale_multiply_calls;
unsigned long long open_cfw_test_decimal_scale_left_bits[128];
unsigned long long open_cfw_test_decimal_scale_right_bits[128];
unsigned long long open_cfw_test_decimal_scale_result_bits[128];

void open_cfw_test_decimal_scale_reset(void)
{
    open_cfw_test_decimal_scale_multiply_calls = 0U;
}

static double open_cfw_test_decimal_scale_multiply(
    double left,
    double right
)
{
    union open_cfw_test_decimal_scale_bits left_value;
    union open_cfw_test_decimal_scale_bits right_value;
    union open_cfw_test_decimal_scale_bits result_value;
    unsigned int index = open_cfw_test_decimal_scale_multiply_calls;

    left_value.value = left;
    right_value.value = right;
    result_value.value = left * right;
    if (index < 128U) {
        open_cfw_test_decimal_scale_left_bits[index] = left_value.bits;
        open_cfw_test_decimal_scale_right_bits[index] = right_value.bits;
        open_cfw_test_decimal_scale_result_bits[index] = result_value.bits;
    }
    open_cfw_test_decimal_scale_multiply_calls = index + 1U;
    return result_value.value;
}
