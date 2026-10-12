/* Oracle probe only: force an inexact FP operation using volatile operands.
 * This is not a selected implementation of the compiler-rt environment API. */
int __fe_raise_inexact(void)
{
    volatile float one=1.0f;
    volatile float tiny=0x1p-25f;
    volatile float rounded=one+tiny;
    (void)rounded;
    return 0;
}
