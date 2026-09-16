/* SPDX-License-Identifier: MIT */
/* Reconstructed from backup entry 0x4859c..0x4863c.
 * This is the stock centered-fmod helper, NOT IEEE remainder: exact half
 * periods retain the dividend's sign instead of choosing an even quotient.
 * Keep the two adjustments sequential, including for negative periods.
 */
extern double __ieee754_fmod(double, double);

double open_cfw_gx8002_centered_remainder(double x, double period)
{
    double r = __ieee754_fmod(x, period);
    if (r > 0.0 && r > period * 0.5)
        r -= period;
    if (r < 0.0 && -r > period * 0.5)
        r += period;
    return r;
}
