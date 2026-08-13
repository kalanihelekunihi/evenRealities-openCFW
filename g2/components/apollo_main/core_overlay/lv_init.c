/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 LVGL initializer at 0x00473548.
 */

typedef void (*open_cfw_lv_init_noarg_fn)(void);
typedef void (*open_cfw_lv_init_u32_fn)(unsigned int value);
typedef void (*open_cfw_lv_init_u32_pair_fn)(
    unsigned int first,
    unsigned int second
);
typedef void (*open_cfw_lv_init_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);

extern void open_cfw_lv_global_initialize(void *global);

#ifndef OPEN_CFW_LV_INIT_GLOBAL
#define OPEN_CFW_LV_INIT_GLOBAL \
    ((volatile unsigned char *)(void *)0x2006F548U)
#endif

#ifndef OPEN_CFW_LV_INIT_GLOBAL_INITIALIZE
#define OPEN_CFW_LV_INIT_GLOBAL_INITIALIZE(global) \
    open_cfw_lv_global_initialize((void *)(global))
#endif

#ifndef OPEN_CFW_LV_INIT_CALL0
#define OPEN_CFW_LV_INIT_CALL0(address) \
    (((open_cfw_lv_init_noarg_fn)(address))())
#endif

#ifndef OPEN_CFW_LV_INIT_CALL1
#define OPEN_CFW_LV_INIT_CALL1(address, value) \
    (((open_cfw_lv_init_u32_fn)(address))(value))
#endif

#ifndef OPEN_CFW_LV_INIT_CALL2
#define OPEN_CFW_LV_INIT_CALL2(address, first, second) \
    (((open_cfw_lv_init_u32_pair_fn)(address))((first), (second)))
#endif

#ifndef OPEN_CFW_LV_INIT_LOG
#define OPEN_CFW_LV_INIT_LOG \
    ((open_cfw_lv_init_log_fn)0x0044D25DU)
#endif

#ifndef OPEN_CFW_LV_INIT_FATAL
#define OPEN_CFW_LV_INIT_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(void *)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_LV_INIT_UTF8_TEXT
static const volatile unsigned char open_cfw_lv_init_utf8_text[3] = {
    0xC3U,
    0x81U,
    0U,
};
#define OPEN_CFW_LV_INIT_UTF8_TEXT open_cfw_lv_init_utf8_text
#endif

#ifndef OPEN_CFW_LV_INIT_ENDIAN_FIRST_BYTE
#define OPEN_CFW_LV_INIT_ENDIAN_FIRST_BYTE() \
    open_cfw_lv_init_endian_first_byte()

static __attribute__((always_inline)) inline unsigned char
open_cfw_lv_init_endian_first_byte(void)
{
    volatile unsigned int value = 0x11223344U;

    return *(const volatile unsigned char *)(const void *)&value;
}
#endif

#define OPEN_CFW_LV_INIT_FILE ((const void *)0x006EE148U)
#define OPEN_CFW_LV_INIT_FUNCTION ((const void *)0x0078DC04U)
#define OPEN_CFW_LV_INIT_ALREADY ((const void *)0x00761B90U)
#define OPEN_CFW_LV_INIT_UTF8_WARNING ((const void *)0x006EE198U)
#define OPEN_CFW_LV_INIT_ASSERTED ((const void *)0x00761B70U)
#define OPEN_CFW_LV_INIT_BIG_ENDIAN_EXPRESSION ((const void *)0x0076DBB8U)
#define OPEN_CFW_LV_INIT_BIG_ENDIAN_MESSAGE ((const void *)0x006EE1E8U)

__attribute__((used, noinline))
void open_cfw_lv_initialize(void)
{
    if (OPEN_CFW_LV_INIT_GLOBAL[0] != 0U) {
        OPEN_CFW_LV_INIT_LOG(
            2U,
            OPEN_CFW_LV_INIT_FILE,
            0xB9U,
            OPEN_CFW_LV_INIT_FUNCTION,
            OPEN_CFW_LV_INIT_ALREADY
        );
        return;
    }

    OPEN_CFW_LV_INIT_GLOBAL_INITIALIZE(OPEN_CFW_LV_INIT_GLOBAL);
    OPEN_CFW_LV_INIT_CALL0(0x0048AA61U);
    OPEN_CFW_LV_INIT_CALL0(0x004C6D05U);
    OPEN_CFW_LV_INIT_CALL0(0x0049ACB1U);
    OPEN_CFW_LV_INIT_CALL0(0x00464331U);
    OPEN_CFW_LV_INIT_CALL0(0x004C6D8DU);
    OPEN_CFW_LV_INIT_CALL0(0x004546DDU);
    OPEN_CFW_LV_INIT_CALL0(0x004503A5U);
    OPEN_CFW_LV_INIT_CALL0(0x0044D32DU);
    OPEN_CFW_LV_INIT_CALL1(0x004B1B99U, 0x40U);
    OPEN_CFW_LV_INIT_CALL0(0x0048438DU);
    OPEN_CFW_LV_INIT_CALL0(0x004C73D7U);
    OPEN_CFW_LV_INIT_CALL0(0x0044B90DU);
    OPEN_CFW_LV_INIT_CALL2(0x00488F4DU, 0U, 0U);
    OPEN_CFW_LV_INIT_CALL0(0x004C794DU);

    if (
        OPEN_CFW_LV_INIT_UTF8_TEXT[0] != 0xC3U
            || OPEN_CFW_LV_INIT_UTF8_TEXT[1] != 0x81U
            || OPEN_CFW_LV_INIT_UTF8_TEXT[2] != 0U
    ) {
        OPEN_CFW_LV_INIT_LOG(
            2U,
            OPEN_CFW_LV_INIT_FILE,
            0x12CU,
            OPEN_CFW_LV_INIT_FUNCTION,
            OPEN_CFW_LV_INIT_UTF8_WARNING
        );
    }

    if (OPEN_CFW_LV_INIT_ENDIAN_FIRST_BYTE() == 0x11U) {
        OPEN_CFW_LV_INIT_LOG(
            3U,
            OPEN_CFW_LV_INIT_FILE,
            0x135U,
            OPEN_CFW_LV_INIT_FUNCTION,
            OPEN_CFW_LV_INIT_ASSERTED,
            OPEN_CFW_LV_INIT_BIG_ENDIAN_EXPRESSION,
            OPEN_CFW_LV_INIT_BIG_ENDIAN_MESSAGE
        );
        OPEN_CFW_LV_INIT_FATAL();
        return;
    }

    OPEN_CFW_LV_INIT_CALL0(0x004C8F0BU);
    OPEN_CFW_LV_INIT_CALL1(0x004C8EFDU, 0x20071AC8U);
    OPEN_CFW_LV_INIT_CALL0(0x004C91A9U);
    OPEN_CFW_LV_INIT_GLOBAL[0] = 1U;
}

#undef OPEN_CFW_LV_INIT_BIG_ENDIAN_MESSAGE
#undef OPEN_CFW_LV_INIT_BIG_ENDIAN_EXPRESSION
#undef OPEN_CFW_LV_INIT_ASSERTED
#undef OPEN_CFW_LV_INIT_UTF8_WARNING
#undef OPEN_CFW_LV_INIT_ALREADY
#undef OPEN_CFW_LV_INIT_FUNCTION
#undef OPEN_CFW_LV_INIT_FILE
#undef OPEN_CFW_LV_INIT_ENDIAN_FIRST_BYTE
#undef OPEN_CFW_LV_INIT_UTF8_TEXT
#undef OPEN_CFW_LV_INIT_FATAL
#undef OPEN_CFW_LV_INIT_LOG
#undef OPEN_CFW_LV_INIT_CALL2
#undef OPEN_CFW_LV_INIT_CALL1
#undef OPEN_CFW_LV_INIT_CALL0
#undef OPEN_CFW_LV_INIT_GLOBAL_INITIALIZE
#undef OPEN_CFW_LV_INIT_GLOBAL
