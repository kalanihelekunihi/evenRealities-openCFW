/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the G2 2.2.6.10 AT^TP command
 * module retained as platform/service/eAT/at_tp.c.  Provider bindings,
 * retained literal addresses, and stock command behavior are pinned in
 * docs/research/g2-at-tp-recovery.md.  No stock object bytes are reproduced.
 */

#include <stdint.h>

#define OPEN_CFW_AT_TP_STRING(address) \
    ((const char *)(uintptr_t)(address))

#ifndef OPEN_CFW_AT_TP_GESTURE_FORMAT
#define OPEN_CFW_AT_TP_GESTURE_FORMAT OPEN_CFW_AT_TP_STRING(0x0073c560u)
#endif
#ifndef OPEN_CFW_AT_TP_DIFF_FORMAT
#define OPEN_CFW_AT_TP_DIFF_FORMAT OPEN_CFW_AT_TP_STRING(0x00769c64u)
#endif
#ifndef OPEN_CFW_AT_TP_BASELINE_FORMAT
#define OPEN_CFW_AT_TP_BASELINE_FORMAT OPEN_CFW_AT_TP_STRING(0x00769c80u)
#endif
#ifndef OPEN_CFW_AT_TP_BASELINE_SAVED
#define OPEN_CFW_AT_TP_BASELINE_SAVED OPEN_CFW_AT_TP_STRING(0x0071c348u)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_READ_FAILED
#define OPEN_CFW_AT_TP_GESTURE_READ_FAILED \
    OPEN_CFW_AT_TP_STRING(0x00769c9cu)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_USAGE
#define OPEN_CFW_AT_TP_GESTURE_USAGE OPEN_CFW_AT_TP_STRING(0x00731ba4u)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_INVALID
#define OPEN_CFW_AT_TP_GESTURE_INVALID OPEN_CFW_AT_TP_STRING(0x007008dcu)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_WRITE_FAILED
#define OPEN_CFW_AT_TP_GESTURE_WRITE_FAILED \
    OPEN_CFW_AT_TP_STRING(0x00769cb8u)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_READBACK_FAILED
#define OPEN_CFW_AT_TP_GESTURE_READBACK_FAILED \
    OPEN_CFW_AT_TP_STRING(0x00727234u)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_MISMATCH
#define OPEN_CFW_AT_TP_GESTURE_MISMATCH OPEN_CFW_AT_TP_STRING(0x006f1b90u)
#endif
#ifndef OPEN_CFW_AT_TP_GESTURE_UPDATED
#define OPEN_CFW_AT_TP_GESTURE_UPDATED OPEN_CFW_AT_TP_STRING(0x00727268u)
#endif
#ifndef OPEN_CFW_AT_TP_OK
#define OPEN_CFW_AT_TP_OK OPEN_CFW_AT_TP_STRING(0x0078a454u)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_DIFF
#define OPEN_CFW_AT_TP_COMMAND_DIFF OPEN_CFW_AT_TP_STRING(0x005a5d08u)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_STOP
#define OPEN_CFW_AT_TP_COMMAND_STOP OPEN_CFW_AT_TP_STRING(0x005a5d0cu)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_DEBUG_ON
#define OPEN_CFW_AT_TP_COMMAND_DEBUG_ON OPEN_CFW_AT_TP_STRING(0x0078cc34u)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_DEBUG_OFF
#define OPEN_CFW_AT_TP_COMMAND_DEBUG_OFF OPEN_CFW_AT_TP_STRING(0x0078cc3cu)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_BASELINE_READ
#define OPEN_CFW_AT_TP_COMMAND_BASELINE_READ OPEN_CFW_AT_TP_STRING(0x0078a43cu)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_BASELINE_SET
#define OPEN_CFW_AT_TP_COMMAND_BASELINE_SET OPEN_CFW_AT_TP_STRING(0x0078a448u)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_GESTURE_READ
#define OPEN_CFW_AT_TP_COMMAND_GESTURE_READ OPEN_CFW_AT_TP_STRING(0x0077e208u)
#endif
#ifndef OPEN_CFW_AT_TP_COMMAND_GESTURE_SET
#define OPEN_CFW_AT_TP_COMMAND_GESTURE_SET OPEN_CFW_AT_TP_STRING(0x007851c0u)
#endif

#ifndef OPEN_CFW_AT_TP_DEBUG_FLAG_ADDRESS
#define OPEN_CFW_AT_TP_DEBUG_FLAG_ADDRESS 0x20075017u
#endif
#ifndef OPEN_CFW_AT_TP_DEBUG_FLAG
#define OPEN_CFW_AT_TP_DEBUG_FLAG \
    (*(volatile uint8_t *)(uintptr_t)OPEN_CFW_AT_TP_DEBUG_FLAG_ADDRESS)
#endif

#ifndef OPEN_CFW_AT_TP_OUTPUT
void open_cfw_retained_at_tp_output(const char *format, ...);
#define OPEN_CFW_AT_TP_OUTPUT(...) open_cfw_retained_at_tp_output(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_AT_TP_STOP
void open_cfw_retained_at_tp_stop(void);
#define OPEN_CFW_AT_TP_STOP() open_cfw_retained_at_tp_stop()
#endif
#ifndef OPEN_CFW_AT_TP_READ_DIFF
void open_cfw_retained_at_tp_read_diff(uint16_t values[5]);
#define OPEN_CFW_AT_TP_READ_DIFF(values) \
    open_cfw_retained_at_tp_read_diff((values))
#endif
#ifndef OPEN_CFW_AT_TP_READ_BASELINE
uint16_t open_cfw_retained_at_tp_read_baseline(void);
#define OPEN_CFW_AT_TP_READ_BASELINE() open_cfw_retained_at_tp_read_baseline()
#endif
#ifndef OPEN_CFW_AT_TP_PREPARE_BASELINE_SAVE
void open_cfw_retained_at_tp_prepare_baseline_save(uint32_t *state);
#define OPEN_CFW_AT_TP_PREPARE_BASELINE_SAVE(state) \
    open_cfw_retained_at_tp_prepare_baseline_save((state))
#endif
#ifndef OPEN_CFW_AT_TP_SAVE_BASELINE
void open_cfw_retained_at_tp_save_baseline(void);
#define OPEN_CFW_AT_TP_SAVE_BASELINE() open_cfw_retained_at_tp_save_baseline()
#endif
#ifndef OPEN_CFW_AT_TP_WRITE_GESTURE
int open_cfw_retained_at_tp_write_gesture(const uint16_t *configuration);
#define OPEN_CFW_AT_TP_WRITE_GESTURE(configuration) \
    open_cfw_retained_at_tp_write_gesture((configuration))
#endif
#ifndef OPEN_CFW_AT_TP_READ_GESTURE
int open_cfw_retained_at_tp_read_gesture(uint16_t *configuration);
#define OPEN_CFW_AT_TP_READ_GESTURE(configuration) \
    open_cfw_retained_at_tp_read_gesture((configuration))
#endif
#ifndef OPEN_CFW_AT_TP_DELAY
int open_cfw_cmsis_delay(uint32_t ticks);
#define OPEN_CFW_AT_TP_DELAY(ticks) open_cfw_cmsis_delay((ticks))
#endif

#if !defined(OPEN_CFW_AT_TP_PRINT_ONLY)
static __attribute__((always_inline)) inline int open_cfw_at_tp_equal(
    const char *left, const char *right
)
{
    if (left == (const char *)0 || right == (const char *)0) {
        return 0;
    }
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

static __attribute__((always_inline)) inline int open_cfw_at_tp_parse_threshold(
    const char *text, uint16_t *threshold
)
{
    uint32_t value = 0u;

    if (text == (const char *)0 || *text == '\0') {
        return 0;
    }
    while (*text != '\0') {
        uint32_t digit;
        if (*text < '0' || *text > '9') {
            return 0;
        }
        digit = (uint32_t)(*text - '0');
        if (value > 6553u || (value == 6553u && digit > 5u)) {
            return 0;
        }
        value = value * 10u + digit;
        ++text;
    }
    if (value == 0u) {
        return 0;
    }
    *threshold = (uint16_t)value;
    return 1;
}
#endif

static __attribute__((always_inline)) inline void
open_cfw_at_tp_emit_gesture(const uint16_t *configuration)
{
    if (configuration != (const uint16_t *)0) {
        OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_FORMAT, *configuration);
    }
}

#if !defined(OPEN_CFW_AT_TP_TEST_ONLY)
void open_cfw_at_tp_print_gesture_cfg(const uint16_t *configuration)
{
    open_cfw_at_tp_emit_gesture(configuration);
}
#endif

#if !defined(OPEN_CFW_AT_TP_PRINT_ONLY)
int open_cfw_at_tp_test(const char *parameter1, const char *parameter2)
{
    uint16_t values[5] = {0u, 0u, 0u, 0u, 0u};
    uint16_t configured;
    uint16_t readback = 0u;
    uint32_t baseline_save_state = 0u;

    if (parameter1 == (const char *)0) {
        return 0;
    }

    if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_DIFF)) {
        OPEN_CFW_AT_TP_READ_DIFF(values);
        OPEN_CFW_AT_TP_OUTPUT(
            OPEN_CFW_AT_TP_DIFF_FORMAT,
            values[0], values[1], values[2], values[3], values[4]
        );
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_STOP)) {
        OPEN_CFW_AT_TP_STOP();
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_DEBUG_ON)) {
        OPEN_CFW_AT_TP_DEBUG_FLAG = 1u;
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_DEBUG_OFF)) {
        OPEN_CFW_AT_TP_DEBUG_FLAG = 0u;
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_BASELINE_READ)) {
        configured = OPEN_CFW_AT_TP_READ_BASELINE();
        OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_BASELINE_FORMAT, configured);
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_BASELINE_SET)) {
        OPEN_CFW_AT_TP_STOP();
        OPEN_CFW_AT_TP_PREPARE_BASELINE_SAVE(&baseline_save_state);
        OPEN_CFW_AT_TP_SAVE_BASELINE();
        OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_BASELINE_SAVED);
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_GESTURE_READ)) {
        if (OPEN_CFW_AT_TP_READ_GESTURE(&readback) != 0) {
            OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_READ_FAILED);
            return 0;
        }
        open_cfw_at_tp_emit_gesture(&readback);
    } else if (open_cfw_at_tp_equal(parameter1, OPEN_CFW_AT_TP_COMMAND_GESTURE_SET)) {
        if (parameter2 == (const char *)0) {
            OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_USAGE);
            return 0;
        }
        if (!open_cfw_at_tp_parse_threshold(parameter2, &configured)) {
            OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_INVALID);
            return 0;
        }
        if (OPEN_CFW_AT_TP_WRITE_GESTURE(&configured) != 0) {
            OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_WRITE_FAILED);
            return 0;
        }
        (void)OPEN_CFW_AT_TP_DELAY(100u);
        if (OPEN_CFW_AT_TP_READ_GESTURE(&readback) != 0) {
            OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_READBACK_FAILED);
            return 0;
        }
        if (configured != readback) {
            OPEN_CFW_AT_TP_OUTPUT(
                OPEN_CFW_AT_TP_GESTURE_MISMATCH, configured, readback
            );
            return 0;
        }
        OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_GESTURE_UPDATED);
        open_cfw_at_tp_emit_gesture(&readback);
    }

    OPEN_CFW_AT_TP_OUTPUT(OPEN_CFW_AT_TP_OK);
    return 1;
}
#endif
