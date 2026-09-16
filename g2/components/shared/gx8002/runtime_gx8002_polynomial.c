/* SPDX-License-Identifier: MIT
 * Reconstructed from codec 2.2.6.10, package 0x49828..0x49890.
 * Coefficients are ascending powers; degree is nonnegative and the caller
 * supplies degree + 1 readable doubles. Preserve multiply-then-add order.
 */
#include <stdint.h>
_Static_assert(sizeof(double) == 8, "binary64 required");
double open_cfw_gx8002_polynomial(const double *coefficients,
                                 uint32_t degree, double x)
{
    double result = coefficients[degree];
    while (degree != 0) {
        --degree;
        result = x * result + coefficients[degree];
    }
    return result;
}
