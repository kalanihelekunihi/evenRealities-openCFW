/* IAR AEABI signed 64-bit division __aeabi_ldivmod, stock 0x47cc1c..0x47cc5e
 * (0x47cc5e is padding; the unsigned core __aeabi_uldivmod follows at
 * 0x47cc60), firmware 2.2.6.10. Run-time ABI: numerator r1:r0, denominator
 * r3:r2; quotient r1:r0, remainder r3:r2 (remainder takes the numerator's
 * sign). Stock (hand assembly in IAR's runtime) makes both operands positive,
 * tail-calls the unsigned core when neither was negative, otherwise calls it
 * and fixes the signs from the saved word ip = (d sign) ^ (n asr 32).
 * Compilation is not byte identity. Profile g2-apollo-main-2.
 *
 * Replaces the quotient-only hand copy audio_uart_lv_div64_47cc1c (which did
 * not return the remainder in r3:r2); that name is kept as a defsym. */

/* Stock 0x0047CC1C (__aeabi_ldivmod) */
__attribute__((naked)) void __aeabi_ldivmod(void)
{
    __asm__ volatile(
        ".syntax unified\n"
        "ands.w ip, r3, #0x80000000\n"
        "bpl 1f\n"
        "rsbs r3, r3, #0\n"
        "rsbs r2, r2, #0\n"
        "sbc r3, r3, #0\n"
        "1:\n"
        "eors.w ip, ip, r1, asr #32\n"
        "beq.w __aeabi_uldivmod\n"
        "push {r4, lr}\n"
        "mov r4, ip\n"
        "bcc 2f\n"
        "rsbs r1, r1, #0\n"
        "rsbs r0, r0, #0\n"
        "sbc r1, r1, #0\n"
        "2:\n"
        "bl __aeabi_uldivmod\n"
        "lsls r4, r4, #1\n"
        "bcc 3f\n"
        "rsbs r1, r1, #0\n"
        "rsbs r0, r0, #0\n"
        "sbc r1, r1, #0\n"
        "tst r4, r4\n"
        "3:\n"
        "bpl 4f\n"
        "rsbs r3, r3, #0\n"
        "rsbs r2, r2, #0\n"
        "sbc r3, r3, #0\n"
        "4:\n"
        "pop {r4, pc}\n");
}
