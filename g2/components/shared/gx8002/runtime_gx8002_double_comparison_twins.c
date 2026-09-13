/* SPDX-License-Identifier: MIT */
/* Stock wrappers at package 0x4ab20 and 0x4ab98 are decoded duplicates of
 * 0x4aae0 and 0x4ab60 respectively. Delegate to source-built libgcc routines;
 * no opaque address binding. NaNs return -1 for the first, +1 for the second. */
extern int __gtdf2(double a, double b);
extern int __ltdf2(double a, double b);
int open_cfw_gx8002_double_compare_4ab20(double a, double b)
{
    return __gtdf2(a, b);
}
int open_cfw_gx8002_double_compare_4ab98(double a, double b)
{
    return __ltdf2(a, b);
}
