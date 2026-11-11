/* Arm EABI comparisons use core argument registers even in this hard-float
 * image. LLVM's ge comparator returns negative for unordered inputs. */
extern int __gedf2(double, double);
__attribute__((pcs("aapcs"))) int __aeabi_dcmpge(double a, double b)
{
    return __gedf2(a, b) >= 0;
}
