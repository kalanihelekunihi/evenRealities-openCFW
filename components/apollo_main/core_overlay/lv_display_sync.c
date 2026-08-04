/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 LVGL display synchronization
 * callback at 0x004736F4.
 */

typedef struct {
    int x1;
    int y1;
    int x2;
    int y2;
} open_cfw_lv_display_sync_area;

typedef int (*open_cfw_lv_display_sync_get_fn)(void *display);
typedef unsigned char (*open_cfw_lv_display_sync_ready_fn)(void *display);
typedef void (*open_cfw_lv_display_sync_buffer_fn)(
    void *buffer,
    unsigned int value
);
typedef void (*open_cfw_lv_display_sync_void_fn)(void);
typedef void (*open_cfw_lv_display_sync_clear_fn)(
    unsigned int x1,
    unsigned int y1,
    unsigned int x2,
    unsigned int y2,
    unsigned int width,
    unsigned int height
);

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_GET_X
#define OPEN_CFW_LV_DISPLAY_SYNC_GET_X(display) \
    (((open_cfw_lv_display_sync_get_fn)0x0044FB4FU)(display))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_GET_Y
#define OPEN_CFW_LV_DISPLAY_SYNC_GET_Y(display) \
    (((open_cfw_lv_display_sync_get_fn)0x0044FB9BU)(display))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_TRANSLATE
#define OPEN_CFW_LV_DISPLAY_SYNC_TRANSLATE(area, dx, dy) \
    do { \
        (area)->x1 = (int)((unsigned int)(area)->x1 + (dx)); \
        (area)->x2 = (int)((unsigned int)(area)->x2 + (dx)); \
        (area)->y1 = (int)((unsigned int)(area)->y1 + (dy)); \
        (area)->y2 = (int)((unsigned int)(area)->y2 + (dy)); \
    } while (0)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER \
    (*(void * volatile *)(void *)0x200746B4U)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SELECT
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SELECT(buffer, value) \
    (((open_cfw_lv_display_sync_buffer_fn)0x0048ABB9U)( \
        (buffer), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_READY
#define OPEN_CFW_LV_DISPLAY_SYNC_READY(display) \
    (((open_cfw_lv_display_sync_ready_fn)0x0044FC43U)(display))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_BEGIN
#define OPEN_CFW_LV_DISPLAY_SYNC_BEGIN() \
    (((open_cfw_lv_display_sync_void_fn)0x0047381FU)())
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SYNC
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SYNC(area, destination, finish) \
    open_cfw_lv_buffer_sync((area), (destination), (finish))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_END
#define OPEN_CFW_LV_DISPLAY_SYNC_END() \
    (((open_cfw_lv_display_sync_void_fn)0x0047386BU)())
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SYNC_CLEAR
#define OPEN_CFW_LV_DISPLAY_SYNC_CLEAR(x1, y1, x2, y2, width, height) \
    (((open_cfw_lv_display_sync_clear_fn)0x00474067U)( \
        (x1), \
        (y1), \
        (x2), \
        (y2), \
        (width), \
        (height) \
    ))
#endif

__attribute__((used, noinline))
void open_cfw_lv_display_sync(
    void *display,
    const open_cfw_lv_display_sync_area *area,
    void *destination
)
{
    volatile open_cfw_lv_display_sync_area translated = *area;
    unsigned int dx = 0U - (unsigned int)OPEN_CFW_LV_DISPLAY_SYNC_GET_X(
        display
    );
    unsigned int dy = 0U - (unsigned int)OPEN_CFW_LV_DISPLAY_SYNC_GET_Y(
        display
    );
    unsigned char ready;

    OPEN_CFW_LV_DISPLAY_SYNC_TRANSLATE(&translated, dx, dy);
    OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SELECT(
        OPEN_CFW_LV_DISPLAY_SYNC_BUFFER,
        0U
    );
    ready = OPEN_CFW_LV_DISPLAY_SYNC_READY(display);
    if (ready == 0U) {
        *(volatile unsigned int *)(void *)(
            (unsigned char *)display + 0x30U
        ) = 0U;
        return;
    }

    OPEN_CFW_LV_DISPLAY_SYNC_BEGIN();
    OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SYNC(
        0,
        destination,
        1U
    );
    OPEN_CFW_LV_DISPLAY_SYNC_END();
    *(volatile unsigned int *)(void *)(
        (unsigned char *)display + 0x30U
    ) = 0U;
    OPEN_CFW_LV_DISPLAY_SYNC_BEGIN();
    OPEN_CFW_LV_DISPLAY_SYNC_CLEAR(0U, 0U, 0U, 0U, 0x240U, 0x120U);
}

#undef OPEN_CFW_LV_DISPLAY_SYNC_CLEAR
#undef OPEN_CFW_LV_DISPLAY_SYNC_END
#undef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SYNC
#undef OPEN_CFW_LV_DISPLAY_SYNC_BEGIN
#undef OPEN_CFW_LV_DISPLAY_SYNC_READY
#undef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SELECT
#undef OPEN_CFW_LV_DISPLAY_SYNC_BUFFER
#undef OPEN_CFW_LV_DISPLAY_SYNC_TRANSLATE
#undef OPEN_CFW_LV_DISPLAY_SYNC_GET_Y
#undef OPEN_CFW_LV_DISPLAY_SYNC_GET_X
