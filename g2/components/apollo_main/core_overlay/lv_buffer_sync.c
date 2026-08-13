/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 full-screen LVGL buffer synchronizer
 * at 0x0047366C.
 */

typedef struct {
    int x1;
    int y1;
    int x2;
    int y2;
} open_cfw_lv_buffer_sync_area;

typedef unsigned char (*open_cfw_lv_buffer_sync_ready_fn)(
    void *display,
    const open_cfw_lv_buffer_sync_area *area,
    unsigned int layer
);
typedef void (*open_cfw_lv_buffer_sync_transfer_fn)(
    void *destination,
    const void *source,
    unsigned int width,
    unsigned int height
);
typedef void (*open_cfw_lv_buffer_sync_u32_fn)(unsigned int value);
typedef void (*open_cfw_lv_buffer_sync_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);

#ifndef OPEN_CFW_LV_BUFFER_SYNC_DISPLAY
#define OPEN_CFW_LV_BUFFER_SYNC_DISPLAY \
    (*(void * volatile *)(void *)0x200746B8U)
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_READY
#define OPEN_CFW_LV_BUFFER_SYNC_READY(display, area, layer) \
    (((open_cfw_lv_buffer_sync_ready_fn)0x004B092BU)( \
        (display), \
        (area), \
        (layer) \
    ))
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_TRANSFER
#define OPEN_CFW_LV_BUFFER_SYNC_TRANSFER(destination, source, width, height) \
    (((open_cfw_lv_buffer_sync_transfer_fn)0x005FA13DU)( \
        (destination), \
        (source), \
        (width), \
        (height) \
    ))
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_SELECT
#define OPEN_CFW_LV_BUFFER_SYNC_SELECT(value) \
    (((open_cfw_lv_buffer_sync_u32_fn)0x004B075FU)(value))
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_FINISH
#define OPEN_CFW_LV_BUFFER_SYNC_FINISH(value) \
    (((open_cfw_lv_buffer_sync_u32_fn)0x004B0C8BU)(value))
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_LOG
#define OPEN_CFW_LV_BUFFER_SYNC_LOG \
    ((open_cfw_lv_buffer_sync_log_fn)0x0044D25DU)
#endif

#ifndef OPEN_CFW_LV_BUFFER_SYNC_FATAL
#define OPEN_CFW_LV_BUFFER_SYNC_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(void *)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

#define OPEN_CFW_LV_BUFFER_SYNC_FILE ((const void *)0x006DD7D4U)
#define OPEN_CFW_LV_BUFFER_SYNC_FUNCTION ((const void *)0x0078ABF8U)
#define OPEN_CFW_LV_BUFFER_SYNC_ASSERTED ((const void *)0x00760630U)
#define OPEN_CFW_LV_BUFFER_SYNC_EXPRESSION ((const void *)0x00786250U)
#define OPEN_CFW_LV_BUFFER_SYNC_MESSAGE ((const void *)0x0071FAD8U)

__attribute__((used, noinline))
void open_cfw_lv_buffer_sync(
    const open_cfw_lv_buffer_sync_area *area,
    void *destination,
    unsigned char finish
)
{
    open_cfw_lv_buffer_sync_area full = {
        0,
        0,
        0x23F,
        0x11F,
    };
    void *display;
    const void *source;

    if (area != (const open_cfw_lv_buffer_sync_area *)0) {
        OPEN_CFW_LV_BUFFER_SYNC_LOG(
            3U,
            OPEN_CFW_LV_BUFFER_SYNC_FILE,
            0xA1U,
            OPEN_CFW_LV_BUFFER_SYNC_FUNCTION,
            OPEN_CFW_LV_BUFFER_SYNC_ASSERTED,
            OPEN_CFW_LV_BUFFER_SYNC_EXPRESSION,
            OPEN_CFW_LV_BUFFER_SYNC_MESSAGE
        );
        OPEN_CFW_LV_BUFFER_SYNC_FATAL();
        return;
    }

    display = OPEN_CFW_LV_BUFFER_SYNC_DISPLAY;
    if (OPEN_CFW_LV_BUFFER_SYNC_READY(display, &full, 0U) != 1U) {
        return;
    }

    source = *(const void * const *)(const void *)(
        (const unsigned char *)display + 0x10U
    );
    OPEN_CFW_LV_BUFFER_SYNC_TRANSFER(
        destination,
        source,
        0x240U,
        0x120U
    );
    OPEN_CFW_LV_BUFFER_SYNC_SELECT(0U);
    OPEN_CFW_LV_BUFFER_SYNC_FINISH((unsigned int)finish);
}

#undef OPEN_CFW_LV_BUFFER_SYNC_MESSAGE
#undef OPEN_CFW_LV_BUFFER_SYNC_EXPRESSION
#undef OPEN_CFW_LV_BUFFER_SYNC_ASSERTED
#undef OPEN_CFW_LV_BUFFER_SYNC_FUNCTION
#undef OPEN_CFW_LV_BUFFER_SYNC_FILE
#undef OPEN_CFW_LV_BUFFER_SYNC_FATAL
#undef OPEN_CFW_LV_BUFFER_SYNC_LOG
#undef OPEN_CFW_LV_BUFFER_SYNC_FINISH
#undef OPEN_CFW_LV_BUFFER_SYNC_SELECT
#undef OPEN_CFW_LV_BUFFER_SYNC_TRANSFER
#undef OPEN_CFW_LV_BUFFER_SYNC_READY
#undef OPEN_CFW_LV_BUFFER_SYNC_DISPLAY
