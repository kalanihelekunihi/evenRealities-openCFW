/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the retained G2 2.2.6.10
 * platform/input/service_gesture_processor.c object.  Fixed provider, SRAM,
 * and literal bindings are documented by the fail-closed recovery analyzer.
 */

#include <stdint.h>

typedef uintptr_t open_cfw_gesture_uintptr;

#define OPEN_CFW_GESTURE_POINTER(address) \
    ((const void *)(open_cfw_gesture_uintptr)(address))
#define OPEN_CFW_GESTURE_STRING(address) \
    ((const char *)(open_cfw_gesture_uintptr)(address))

#ifndef OPEN_CFW_GESTURE_PROXIMITY_CELL
#define OPEN_CFW_GESTURE_PROXIMITY_CELL \
    (*(volatile uint8_t *)(open_cfw_gesture_uintptr)0x20075018u)
#endif
#ifndef OPEN_CFW_GESTURE_DEBUG_CELL
#define OPEN_CFW_GESTURE_DEBUG_CELL \
    (*(volatile uint8_t *)(open_cfw_gesture_uintptr)0x20075017u)
#endif
#ifndef OPEN_CFW_GESTURE_NAME_TABLE
#define OPEN_CFW_GESTURE_NAME_TABLE \
    ((const char *const *)(open_cfw_gesture_uintptr)0x200036ecu)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_BUFFER
#define OPEN_CFW_GESTURE_MASK_BUFFER \
    ((char *)(open_cfw_gesture_uintptr)0x20072790u)
#endif

#ifndef OPEN_CFW_GESTURE_MASK_PRESS
#define OPEN_CFW_GESTURE_MASK_PRESS OPEN_CFW_GESTURE_STRING(0x00783244u)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_RELEASE
#define OPEN_CFW_GESTURE_MASK_RELEASE OPEN_CFW_GESTURE_STRING(0x0077b7f4u)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_SINGLE
#define OPEN_CFW_GESTURE_MASK_SINGLE OPEN_CFW_GESTURE_STRING(0x00783258u)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_DOUBLE
#define OPEN_CFW_GESTURE_MASK_DOUBLE OPEN_CFW_GESTURE_STRING(0x0078326cu)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_LONG
#define OPEN_CFW_GESTURE_MASK_LONG OPEN_CFW_GESTURE_STRING(0x00783280u)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_SLIDE_LEFT
#define OPEN_CFW_GESTURE_MASK_SLIDE_LEFT OPEN_CFW_GESTURE_STRING(0x0077b80cu)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_SLIDE_RIGHT
#define OPEN_CFW_GESTURE_MASK_SLIDE_RIGHT OPEN_CFW_GESTURE_STRING(0x0077b824u)
#endif
#ifndef OPEN_CFW_GESTURE_MASK_ERROR
#define OPEN_CFW_GESTURE_MASK_ERROR OPEN_CFW_GESTURE_STRING(0x00783294u)
#endif

#ifndef OPEN_CFW_GESTURE_LOG_LEVEL
uint32_t open_cfw_retained_gesture_log_level(void);
#define OPEN_CFW_GESTURE_LOG_LEVEL() open_cfw_retained_gesture_log_level()
#endif
#ifndef OPEN_CFW_GESTURE_LOG
void open_cfw_retained_gesture_log(
    uint32_t level, const void *module, const void *file,
    const void *function, uint32_t line, const void *format, ...
);
#define OPEN_CFW_GESTURE_LOG(...) open_cfw_retained_gesture_log(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_GESTURE_TRACE
void open_cfw_retained_gesture_trace(
    uint32_t metadata, const void *format, const void *repeat, ...
);
#define OPEN_CFW_GESTURE_TRACE(...) open_cfw_retained_gesture_trace(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_GESTURE_HEXDUMP
void open_cfw_retained_gesture_hexdump(const void *data, uint32_t size);
#define OPEN_CFW_GESTURE_HEXDUMP(data, size) \
    open_cfw_retained_gesture_hexdump((data), (size))
#endif
#ifndef OPEN_CFW_GESTURE_TOUCH_READ
void open_cfw_retained_gesture_touch_read(uint8_t *data);
#define OPEN_CFW_GESTURE_TOUCH_READ(data) \
    open_cfw_retained_gesture_touch_read((data))
#endif
#ifndef OPEN_CFW_GESTURE_TOUCH_STOP
void open_cfw_retained_gesture_touch_stop(void);
#define OPEN_CFW_GESTURE_TOUCH_STOP() open_cfw_retained_gesture_touch_stop()
#endif
#ifndef OPEN_CFW_GESTURE_TOUCH_PREPARE_BASELINE
void open_cfw_retained_gesture_touch_prepare_baseline(uint32_t *value);
#define OPEN_CFW_GESTURE_TOUCH_PREPARE_BASELINE(value) \
    open_cfw_retained_gesture_touch_prepare_baseline((value))
#endif
#ifndef OPEN_CFW_GESTURE_PRODUCT_MODE
uint32_t open_cfw_retained_gesture_product_mode(void);
#define OPEN_CFW_GESTURE_PRODUCT_MODE() \
    open_cfw_retained_gesture_product_mode()
#endif
#ifndef OPEN_CFW_GESTURE_BUZZER_PLAY
void open_cfw_retained_gesture_buzzer_play(uint32_t type);
#define OPEN_CFW_GESTURE_BUZZER_PLAY(type) \
    open_cfw_retained_gesture_buzzer_play((type))
#endif
#ifndef OPEN_CFW_GESTURE_PROXIMITY_NOTIFY
void open_cfw_retained_gesture_proximity_notify(
    uint32_t selector, uint32_t value
);
#define OPEN_CFW_GESTURE_PROXIMITY_NOTIFY(selector, value) \
    open_cfw_retained_gesture_proximity_notify((selector), (value))
#endif
#ifndef OPEN_CFW_GESTURE_TIMESTAMP
uint32_t open_cfw_retained_gesture_timestamp(void);
#define OPEN_CFW_GESTURE_TIMESTAMP() open_cfw_retained_gesture_timestamp()
#endif
#ifndef OPEN_CFW_GESTURE_PUBLISH
void open_cfw_retained_gesture_publish(
    uint16_t timestamp, uint32_t event, uint32_t argument0,
    uint32_t argument1
);
#define OPEN_CFW_GESTURE_PUBLISH(timestamp, event, argument0, argument1) \
    open_cfw_retained_gesture_publish( \
        (timestamp), (event), (argument0), (argument1) \
    )
#endif

void open_cfw_gesture_production_click(uint8_t mask, uint8_t difference_x);
uint8_t open_cfw_gesture_get_proximity(void);
const char *open_cfw_gesture_event_name(uint8_t event);
char *open_cfw_gesture_format_mask(uint8_t mask);
void open_cfw_gesture_process(void);

static __attribute__((always_inline, unused)) inline int
open_cfw_gesture_trace_enabled(void)
{
    uint32_t level = OPEN_CFW_GESTURE_LOG_LEVEL();
    if ((level & 1u) != 0u) {
        return 1;
    }
    return (OPEN_CFW_GESTURE_LOG_LEVEL() & 4u) != 0u;
}

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_gesture_u16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline void
open_cfw_gesture_emit(uint32_t event, uint32_t argument0, uint32_t argument1)
{
    OPEN_CFW_GESTURE_PUBLISH(
        (uint16_t)OPEN_CFW_GESTURE_TIMESTAMP(), event, argument0, argument1
    );
}

#if !defined(OPEN_CFW_GESTURE_PRODUCTION_CLICK_ONLY) \
    && !defined(OPEN_CFW_GESTURE_GET_PROXIMITY_ONLY) \
    && !defined(OPEN_CFW_GESTURE_EVENT_NAME_ONLY) \
    && !defined(OPEN_CFW_GESTURE_FORMAT_MASK_ONLY) \
    && !defined(OPEN_CFW_GESTURE_PROCESS_ONLY)
#define OPEN_CFW_GESTURE_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_GESTURE_BUILD_ALL) \
    || defined(OPEN_CFW_GESTURE_PRODUCTION_CLICK_ONLY)
void open_cfw_gesture_production_click(uint8_t mask, uint8_t difference_x)
{
    const void *module = OPEN_CFW_GESTURE_POINTER(0x0078bf24u);
    const void *file = OPEN_CFW_GESTURE_POINTER(0x006ef958u);
    const void *function = OPEN_CFW_GESTURE_POINTER(0x00764e90u);

    if ((mask & 4u) == 0u || difference_x != 1u) {
        return;
    }
    OPEN_CFW_GESTURE_BUZZER_PLAY(3u);
    if ((OPEN_CFW_GESTURE_LOG_LEVEL() & 2u) != 0u) {
        OPEN_CFW_GESTURE_LOG(
            4u, module, file, function, 37u,
            OPEN_CFW_GESTURE_POINTER(0x0077124cu)
        );
    }
    if (open_cfw_gesture_trace_enabled()) {
        const void *trace = OPEN_CFW_GESTURE_POINTER(0x0074de6cu);
        OPEN_CFW_GESTURE_TRACE(0x10000000u, trace, trace);
    }
}
#endif

#if defined(OPEN_CFW_GESTURE_BUILD_ALL) \
    || defined(OPEN_CFW_GESTURE_GET_PROXIMITY_ONLY)
uint8_t open_cfw_gesture_get_proximity(void)
{
    return OPEN_CFW_GESTURE_PROXIMITY_CELL;
}
#endif

#if defined(OPEN_CFW_GESTURE_BUILD_ALL) \
    || defined(OPEN_CFW_GESTURE_EVENT_NAME_ONLY)
const char *open_cfw_gesture_event_name(uint8_t event)
{
    return OPEN_CFW_GESTURE_NAME_TABLE[event];
}
#endif

#if defined(OPEN_CFW_GESTURE_BUILD_ALL) \
    || defined(OPEN_CFW_GESTURE_FORMAT_MASK_ONLY)
char *open_cfw_gesture_format_mask(uint8_t mask)
{
    char *output = OPEN_CFW_GESTURE_MASK_BUFFER;
    uint32_t used = 0u;
    uint32_t bit;

    output[0] = '\0';
    for (bit = 0u; bit < 8u; ++bit) {
        const char *name;
        if ((mask & (uint8_t)(1u << bit)) == 0u) {
            continue;
        }
        if (bit == 0u) {
            name = OPEN_CFW_GESTURE_MASK_PRESS;
        } else if (bit == 1u) {
            name = OPEN_CFW_GESTURE_MASK_RELEASE;
        } else if (bit == 2u) {
            name = OPEN_CFW_GESTURE_MASK_SINGLE;
        } else if (bit == 3u) {
            name = OPEN_CFW_GESTURE_MASK_DOUBLE;
        } else if (bit == 4u) {
            name = OPEN_CFW_GESTURE_MASK_LONG;
        } else if (bit == 5u) {
            name = OPEN_CFW_GESTURE_MASK_SLIDE_LEFT;
        } else if (bit == 6u) {
            name = OPEN_CFW_GESTURE_MASK_SLIDE_RIGHT;
        } else {
            name = OPEN_CFW_GESTURE_MASK_ERROR;
        }
        while (*name != '\0' && used < 95u) {
            output[used++] = *name++;
        }
        if (used < 95u) {
            output[used++] = '|';
        }
        output[used] = '\0';
    }
    if (used != 0u && output[used - 1u] == '|') {
        output[used - 1u] = '\0';
    }
    return output;
}
#endif

#if defined(OPEN_CFW_GESTURE_BUILD_ALL) \
    || defined(OPEN_CFW_GESTURE_PROCESS_ONLY)
void open_cfw_gesture_process(void)
{
    uint8_t data[16] = {0};
    uint8_t proximity;
    uint8_t mask;
    uint8_t difference_x;
    uint8_t speed;
    uint16_t baseline;
    uint16_t raw;
    uint16_t difference;
    uint16_t saved_baseline;
    const void *module = OPEN_CFW_GESTURE_POINTER(0x0078bf24u);
    const void *file = OPEN_CFW_GESTURE_POINTER(0x006ef958u);
    const void *function = OPEN_CFW_GESTURE_POINTER(0x0077b83cu);

    OPEN_CFW_GESTURE_TOUCH_READ(data);
    if (OPEN_CFW_GESTURE_DEBUG_CELL != 0u) {
        OPEN_CFW_GESTURE_HEXDUMP(data, 16u);
    }
    proximity = data[0];
    mask = data[1];
    difference_x = data[2];
    speed = data[3];
    baseline = open_cfw_gesture_u16(&data[4]);
    raw = open_cfw_gesture_u16(&data[6]);
    difference = open_cfw_gesture_u16(&data[8]);
    saved_baseline = open_cfw_gesture_u16(&data[10]);

    if ((OPEN_CFW_GESTURE_LOG_LEVEL() & 2u) != 0u) {
        OPEN_CFW_GESTURE_LOG(
            3u, module, file, function, 112u,
            OPEN_CFW_GESTURE_POINTER(0x006e17c8u),
            proximity, baseline, saved_baseline, raw, difference,
            difference_x, speed, mask, open_cfw_gesture_format_mask(mask)
        );
    }
    if (open_cfw_gesture_trace_enabled()) {
        const void *trace = OPEN_CFW_GESTURE_POINTER(0x006d9974u);
        OPEN_CFW_GESTURE_TRACE(
            0x0e400000u, trace, trace,
            proximity, baseline, saved_baseline, raw, difference,
            difference_x, speed, mask, open_cfw_gesture_format_mask(mask)
        );
    }

    if (proximity != 0u) {
        if ((OPEN_CFW_GESTURE_LOG_LEVEL() & 2u) != 0u) {
            OPEN_CFW_GESTURE_LOG(
                3u, module, file, function, 116u,
                OPEN_CFW_GESTURE_POINTER(0x0078bf30u),
                open_cfw_gesture_event_name(proximity), proximity
            );
        }
        if (open_cfw_gesture_trace_enabled()) {
            const void *trace = OPEN_CFW_GESTURE_POINTER(0x0077b854u);
            OPEN_CFW_GESTURE_TRACE(
                0x0c800000u, trace, trace,
                open_cfw_gesture_event_name(proximity), proximity
            );
        }
        OPEN_CFW_GESTURE_PROXIMITY_CELL = proximity;
        OPEN_CFW_GESTURE_PROXIMITY_NOTIFY(3u, proximity);
    }

    if (mask == 0u) {
        return;
    }
    if (OPEN_CFW_GESTURE_PRODUCT_MODE() == 1u) {
        open_cfw_gesture_production_click(mask, difference_x);
        return;
    }

    if ((OPEN_CFW_GESTURE_LOG_LEVEL() & 2u) != 0u) {
        OPEN_CFW_GESTURE_LOG(
            4u, module, file, function, 130u,
            OPEN_CFW_GESTURE_POINTER(0x0072d484u),
            mask, open_cfw_gesture_format_mask(mask), difference_x, speed
        );
    }
    if (open_cfw_gesture_trace_enabled()) {
        const void *trace = OPEN_CFW_GESTURE_POINTER(0x007185a4u);
        OPEN_CFW_GESTURE_TRACE(
            0x11000000u, trace, trace,
            mask, open_cfw_gesture_format_mask(mask), difference_x, speed
        );
    }

    if ((mask & 0x80u) != 0u) {
        uint32_t baseline_command = 0u;
        if ((OPEN_CFW_GESTURE_LOG_LEVEL() & 2u) != 0u) {
            OPEN_CFW_GESTURE_LOG(
                1u, module, file, function, 133u,
                OPEN_CFW_GESTURE_POINTER(0x00764eb0u)
            );
        }
        if (open_cfw_gesture_trace_enabled()) {
            const void *trace = OPEN_CFW_GESTURE_POINTER(0x00743258u);
            OPEN_CFW_GESTURE_TRACE(0x04000000u, trace, trace);
        }
        OPEN_CFW_GESTURE_TOUCH_STOP();
        OPEN_CFW_GESTURE_TOUCH_PREPARE_BASELINE(&baseline_command);
        return;
    }
    if ((mask & 0x01u) != 0u) {
        open_cfw_gesture_emit(0x0du, 0u, 0u);
    }
    if ((mask & 0x04u) != 0u) {
        if (difference_x < 2u) {
            open_cfw_gesture_emit(0u, 0u, 0u);
        } else if (difference_x >= 10u) {
            open_cfw_gesture_emit(0x1010u, 0u, 0u);
        }
    }
    if ((mask & 0x08u) != 0u) {
        open_cfw_gesture_emit(1u, 0u, 0u);
    }
    if ((mask & 0x10u) != 0u) {
        open_cfw_gesture_emit(3u, 0u, 0u);
    }
    if ((mask & 0x20u) != 0u) {
        open_cfw_gesture_emit(5u, difference_x, speed);
    }
    if ((mask & 0x40u) != 0u) {
        open_cfw_gesture_emit(4u, difference_x, speed);
    }
    if ((mask & 0x02u) != 0u) {
        open_cfw_gesture_emit(0x0eu, 0u, 0u);
    }
}
#endif
