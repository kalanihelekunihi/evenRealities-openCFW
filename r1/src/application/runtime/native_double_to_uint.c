#include <stdint.h>
extern uint32_t r1_binary64_to_unsigned32_bits(uint64_t);

/* Compiler helpers use the base AAPCS even in the hard-float image.
 * Reuse the existing native bit implementation: stock ignores the sign and
 * retains ARM register-shift behavior beyond the ordinary unsigned range. */
__attribute__((pcs("aapcs"))) uint32_t __aeabi_d2uiz(double value)
{
    union { double value; uint64_t bits; } view = { .value=value };
    return r1_binary64_to_unsigned32_bits(view.bits);
}
