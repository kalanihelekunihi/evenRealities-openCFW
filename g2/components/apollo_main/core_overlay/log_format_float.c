/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the bounded G2 2.2.6.10 logging float converter at
 * 0x00472EF6.
 */

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_LOG_FLOAT_ABI __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_LOG_FLOAT_ABI
#endif

unsigned int open_cfw_log_decimal_write(
    unsigned int low,
    unsigned int high,
    char *destination
);

__attribute__((used, noinline))
OPEN_CFW_LOG_FLOAT_ABI
int open_cfw_log_float_write(
    char *destination,
    unsigned int precision,
    float value
)
{
    union {
        float floating;
        unsigned int bits;
    } representation;
    unsigned int capacity = *(const unsigned int *)(const void *)destination;
    unsigned int fraction = 0U;
    unsigned int whole = 0U;
    unsigned int mantissa;
    int exponent;
    char *cursor = destination;

    if (capacity < 4U) {
        return -3;
    }
    representation.floating = value;
    if ((representation.bits & 0x7FFFFFFFU) == 0U) {
        destination[0] = '0';
        destination[1] = '.';
        destination[2] = '0';
        destination[3] = '\0';
        return 3;
    }

    exponent = (int)((representation.bits >> 23U) & 0xFFU) - 127;
    mantissa = (representation.bits & 0x00FFFFFFU) | 0x00800000U;
    if (exponent >= 31) {
        return -2;
    }
    if (exponent < -23) {
        return -1;
    }
    if (exponent >= 23) {
        whole = mantissa << (unsigned int)(exponent - 23);
    } else if (exponent >= 0) {
        whole = mantissa >> (unsigned int)(23 - exponent);
        fraction = (mantissa << (unsigned int)(exponent + 1))
            & 0x00FFFFFFU;
    } else {
        fraction = mantissa >> (unsigned int)(-(exponent + 1));
    }

    if ((representation.bits & 0x80000000U) != 0U) {
        *cursor = '-';
        cursor += 1;
    }
    if (whole == 0U) {
        *cursor = '0';
        cursor += 1;
    } else {
        if ((int)whole < 0) {
            *cursor = '-';
            cursor += 1;
            whole = 0U - whole;
        }
        (void)open_cfw_log_decimal_write(
            whole,
            (int)whole < 0 ? 0xFFFFFFFFU : 0U,
            cursor
        );
        while (*cursor != '\0') {
            cursor += 1;
        }
    }
    *cursor = '.';
    cursor += 1;

    if (fraction == 0U) {
        *cursor = '0';
        cursor += 1;
    } else {
        int available = (int)capacity
            - (int)(cursor - destination)
            - 1;
        unsigned int index = 0U;

        if ((int)precision >= available) {
            precision = (unsigned int)available;
        }
        while ((int)index < (int)precision) {
            fraction *= 10U;
            *cursor = (char)('0' + ((int)fraction >> 24));
            cursor += 1;
            fraction &= 0x00FFFFFFU;
            index += 1U;
        }
        fraction *= 10U;
        if (((int)fraction >> 24) >= 5) {
            char *rounding = cursor;

            while (rounding != destination) {
                rounding -= 1;
                if (*rounding == '.') {
                    continue;
                }
                if (*rounding == '9') {
                    *rounding = '0';
                    continue;
                }
                *rounding = (char)(*rounding + 1);
                break;
            }
        }
    }
    *cursor = '\0';
    return (int)(cursor - destination);
}

#undef OPEN_CFW_LOG_FLOAT_ABI
