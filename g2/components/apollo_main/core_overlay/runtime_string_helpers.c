/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of two libc-shaped string helpers retained in
 * G2 firmware 2.2.6.10 at 0x0048D540..0x0048D558 (strcpy, 24 bytes) and
 * 0x0048D724..0x0048D866 (strtoul, 318 bytes; Apollo main application,
 * component `apollo_main`, work item AM-040).
 *
 * Both are clean-room C written from the stock instruction stream
 * (decoded with capstone on macOS; Ghidra RMI decompilation alone
 * mis-simplifies the strtoul table arithmetic, see below). No upstream
 * family is claimed: the shapes match IAR DLib libc, but that family
 * confirmation belongs to the iar-dlib census work, so these are
 * first-party reviewed ports with retained libc-locale callees.
 *
 * Retained callees (all outside this item's range, still stock):
 *  - 0x004D58AE locale-aware whitespace test (nonzero = skip)
 *  - 0x004D58C2 locale-aware digit-class mapping (value searched below)
 *  - 0x004D40E0 word-at-a-time memchr over the digit table
 *    (returns the match address, NULL on miss)
 *  - 0x00439CB2 overflow errno setter (stores 0x22/ERANGE at 0x00439CD4)
 *
 * strtoul table derivation (verified instruction by instruction):
 *  - The literal word at 0x0048D7DC (0x00263A2C) is a PC-relative delta:
 *    T = word + (ldr-site PC 0x0048D7C8) + 0x14 = 0x006F1208, the C
 *    library digit table in shared SRAM (0x006xxxxx region; cf. the
 *    0x006A4744/0x00600FAA runtime words in docs/memory-map.md).
 *  - T+base holds the per-base significant-digit threshold byte;
 *    T+0x28 is the digit-class table searched with memchr over the
 *    first `base` entries.
 *  - The digit is NOT found-minus-base: the stock keeps only the low
 *    byte of T+0x28 and computes digit = (found - (T+0x28 low byte)) &
 *    0xFF. This works because the firmware table satisfies
 *    (T+0x28)&0xFF == 0x30, so (T+0x28+index-0x30)&0xFF == index. The
 *    port reproduces this exact computation (not the simplified index
 *    form) so it stays behavior-identical for any table placement.
 *  - Overflow: if more significant digits than the threshold were
 *    consumed, or (on a tie) acc-digit borrows or
 *    (acc-digit)/base != previous acc, the result is 0xFFFFFFFF with
 *    the errno hook called and, when non-NULL, *errno_flag = 1.
 *  - No digits at all (after sign/base/zero handling) stores the
 *    original pointer to *endptr when non-NULL and returns 0; an
 *    invalid base (<0, ==1, >36) does the same. A leading '-' negates
 *    the accumulated value (including the 0xFFFFFFFF overflow value:
 *    stock negates unconditionally via rsb, with no overflow guard).
 *
 * Hardware qualification stays blocked by unavailable physical
 * evidence; no flashing, DFU, MMIO probing, signing, or publishing
 * was performed.
 */

typedef unsigned int open_cfw_strtoul_addr;
typedef unsigned char open_cfw_strtoul_byte;

#ifndef OPEN_CFW_STR_ISSPACE
typedef int (*open_cfw_str_isspace_fn)(int c);
#define OPEN_CFW_STR_ISSPACE(c) \
    (((open_cfw_str_isspace_fn)0x004D58AFU)(c))
#endif

#ifndef OPEN_CFW_STR_DIGIT_CLASS
typedef int (*open_cfw_str_digit_class_fn)(int c);
#define OPEN_CFW_STR_DIGIT_CLASS(c) \
    (((open_cfw_str_digit_class_fn)0x004D58C3U)(c))
#endif

#ifndef OPEN_CFW_STR_TABLE_MEMCHR
typedef void *(*open_cfw_str_table_memchr_fn)(
    const void *table, int value, unsigned int count);
#define OPEN_CFW_STR_TABLE_MEMCHR(table, value, count) \
    (((open_cfw_str_table_memchr_fn)0x004D40E1U)((table), (value), (count)))
#endif

#ifndef OPEN_CFW_STR_OVERFLOW_ERRNO
typedef void (*open_cfw_str_overflow_errno_fn)(void);
#define OPEN_CFW_STR_OVERFLOW_ERRNO() \
    (((open_cfw_str_overflow_errno_fn)0x00439CB3U)())
#endif

/*
 * Digit-table base recovered from the stock PC-relative delta
 * (see header note): literal 0x00263A2C at 0x0048D7DC plus the
 * ldr-site PC 0x0048D7C8 plus 0x14. Kept as a pointer-typed hook so
 * host tests can substitute a host table without address truncation.
 */
#ifndef OPEN_CFW_STRTOUL_TABLE
#define OPEN_CFW_STRTOUL_TABLE \
    ((const open_cfw_strtoul_byte *)0x006F1208U)
#endif
#ifndef OPEN_CFW_STRTOUL_TABLE_SEARCH_OFFSET
#define OPEN_CFW_STRTOUL_TABLE_SEARCH_OFFSET 0x28U
#endif

__attribute__((used, noinline))
char *open_cfw_libc_strcpy(char *dst, const char *src)
{
    char *keep = dst;
    char c;

    do {
        c = *src++;
        *dst++ = c;
    } while (c != '\0');
    return keep;
}

__attribute__((used, noinline))
unsigned int open_cfw_libc_strtoul(
    const char *str, char **endptr, int base, unsigned int *errno_flag)
{
    const char *p = str;
    const char *nodigits;
    const char *significant;
    const open_cfw_strtoul_byte *table = OPEN_CFW_STRTOUL_TABLE;
    const char *search = (const char *)(
        (__UINTPTR_TYPE__)table + OPEN_CFW_STRTOUL_TABLE_SEARCH_OFFSET);
    open_cfw_strtoul_byte search_low =
        (open_cfw_strtoul_byte)(__UINTPTR_TYPE__)search;
    unsigned int acc = 0U;
    unsigned int prev = 0U;
    unsigned int digit = 0U;
    int sign_is_minus = 0;
    int c;

    if (errno_flag != 0) {
        *errno_flag = 0U;
    }
    while (OPEN_CFW_STR_ISSPACE((unsigned char)*p) != 0) {
        p++;
    }
    c = (unsigned char)*p;
    if (c == '-' || c == '+') {
        sign_is_minus = (c == '-');
        p++;
    }
    if (base < 0 || base == 1 || base > 36) {
        if (endptr != 0) {
            *endptr = (char *)str;
        }
        return 0U;
    }
    if (base == 0) {
        if (*p != '0') {
            base = 10;
        } else if ((((unsigned char)p[1]) | 0x20U) != 0x78U) {
            base = 8;
        } else {
            base = 16;
            p += 2;
        }
    } else if (base == 16) {
        if (p[0] == '0' && (((unsigned char)p[1]) | 0x20U) == 0x78U) {
            p += 2;
        }
    }
    nodigits = p;
    while (*p == '0') {
        p++;
    }
    significant = p;
    for (;;) {
        const char *found;
        c = OPEN_CFW_STR_DIGIT_CLASS((unsigned char)*p);
        found = (const char *)OPEN_CFW_STR_TABLE_MEMCHR(
            search, c, (unsigned int)base);
        if (found == 0) {
            break;
        }
        prev = acc;
        digit = ((unsigned int)(
            (__UINTPTR_TYPE__)found - search_low)) & 0xFFU;
        acc = (unsigned int)base * acc + digit;
        p++;
    }
    if (nodigits == p) {
        if (endptr != 0) {
            *endptr = (char *)str;
        }
        return 0U;
    }
    {
        int extra =
            (int)((unsigned int)(p - significant) - table[base]);
        if (extra < 0) {
            /* Fewer significant digits than the per-base limit. */
        } else if (extra > 0 || acc - digit > acc
            || (acc - digit) / (unsigned int)base != prev) {
            OPEN_CFW_STR_OVERFLOW_ERRNO();
            if (errno_flag != 0) {
                *errno_flag = 1U;
            }
            acc = 0xFFFFFFFFU;
        }
    }
    if (sign_is_minus) {
        acc = (unsigned int)(-(int)acc);
    }
    if (endptr != 0) {
        *endptr = (char *)p;
    }
    return acc;
}

#ifdef OPEN_CFW_STR_DEFINE_TEST_HOOKS
#undef OPEN_CFW_STR_ISSPACE
#undef OPEN_CFW_STR_DIGIT_CLASS
#undef OPEN_CFW_STR_TABLE_MEMCHR
#undef OPEN_CFW_STR_OVERFLOW_ERRNO
#endif
