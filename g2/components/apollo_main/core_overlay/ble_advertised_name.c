/*
 * SPDX-License-Identifier: MIT
 *
 * Preserve the stock G2 advertised-name structure while replacing its final
 * six per-temple BLE-address characters with the final six characters of the
 * validated pair serial used by the stock advertising builder.
 *
 * This hook replaces the final stock memcpy into the local-name suffix.  The
 * earlier PSN-to-manufacturer-data call is intentionally left untouched: on a
 * cold boot the stock builder writes the BLE address after that call, so an
 * earlier rewrite is immediately overwritten until a later pairing refresh.
 */

typedef __UINTPTR_TYPE__ open_cfw_adv_name_uintptr;

typedef void (*open_cfw_adv_name_memcpy_function)(
    void *destination,
    const void *source,
    unsigned int length
);

#ifndef OPEN_CFW_ADV_NAME_STOCK_MEMCPY_ADDRESS
#define OPEN_CFW_ADV_NAME_STOCK_MEMCPY_ADDRESS 0x00439BE5U
#endif

#ifndef OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER_ADDRESS
#define OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER_ADDRESS 0x2000383CU
#endif

#ifndef OPEN_CFW_ADV_NAME_STOCK_MEMCPY
#define OPEN_CFW_ADV_NAME_STOCK_MEMCPY(destination, source, length) \
    (((open_cfw_adv_name_memcpy_function) \
        (open_cfw_adv_name_uintptr)OPEN_CFW_ADV_NAME_STOCK_MEMCPY_ADDRESS)( \
            (destination), (source), (length) \
        ))
#endif

#ifndef OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER
#define OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER \
    ((const unsigned char *volatile *) \
        (open_cfw_adv_name_uintptr) \
            OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER_ADDRESS)
#endif

#define OPEN_CFW_ADV_NAME_SERIAL_LENGTH 14U
#define OPEN_CFW_ADV_NAME_SUFFIX_LENGTH 6U

static __attribute__((always_inline)) inline unsigned int
open_cfw_adv_name_is_serial_character(unsigned char value)
{
    return (value >= (unsigned char)'0' && value <= (unsigned char)'9')
        || (value >= (unsigned char)'A' && value <= (unsigned char)'Z')
        || (value >= (unsigned char)'a' && value <= (unsigned char)'z');
}

__attribute__((used, noinline))
void open_cfw_copy_advertised_name_pair_suffix(
    unsigned char *destination,
    const unsigned char *stock_suffix,
    unsigned int length
)
{
    const unsigned char *serial_record;
    const unsigned char *serial;
    unsigned int index;

    /* Preserve the exact stock BLE-address copy unless every PSN check passes. */
    OPEN_CFW_ADV_NAME_STOCK_MEMCPY(destination, stock_suffix, length);

    if (destination == (unsigned char *)0
        || length != OPEN_CFW_ADV_NAME_SUFFIX_LENGTH) {
        return;
    }
    serial_record = *OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER;
    if (serial_record == (const unsigned char *)0) {
        return;
    }
    serial = serial_record + 1U;
    for (index = 0U; index < OPEN_CFW_ADV_NAME_SERIAL_LENGTH; ++index) {
        if (!open_cfw_adv_name_is_serial_character(serial[index])) {
            return;
        }
    }
    if (serial[OPEN_CFW_ADV_NAME_SERIAL_LENGTH] != 0U) {
        return;
    }
    for (index = 0U; index < OPEN_CFW_ADV_NAME_SUFFIX_LENGTH; ++index) {
        destination[index] = serial[
            OPEN_CFW_ADV_NAME_SERIAL_LENGTH
            - OPEN_CFW_ADV_NAME_SUFFIX_LENGTH
            + index
        ];
    }
}

#undef OPEN_CFW_ADV_NAME_SUFFIX_LENGTH
#undef OPEN_CFW_ADV_NAME_SERIAL_LENGTH
#undef OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER
#undef OPEN_CFW_ADV_NAME_STOCK_MEMCPY
#undef OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER_ADDRESS
#undef OPEN_CFW_ADV_NAME_STOCK_MEMCPY_ADDRESS
