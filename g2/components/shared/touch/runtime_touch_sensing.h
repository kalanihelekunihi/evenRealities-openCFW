/* SPDX-License-Identifier: MIT OR GPL-3.0-only */
#ifndef OPEN_CFW_RUNTIME_TOUCH_SENSING_H
#define OPEN_CFW_RUNTIME_TOUCH_SENSING_H

#include <stddef.h>
#include <stdint.h>

typedef enum open_cfw_touch_power_state {
    OPEN_CFW_TOUCH_POWER_ACT = 0,
    OPEN_CFW_TOUCH_POWER_ALR = 1,
    OPEN_CFW_TOUCH_POWER_WOT = 2
} open_cfw_touch_power_state;

typedef enum open_cfw_touch_power_event {
    OPEN_CFW_TOUCH_POWER_EVENT_INACTIVE = 0,
    OPEN_CFW_TOUCH_POWER_EVENT_ALARM_EXPIRED = 1,
    OPEN_CFW_TOUCH_POWER_EVENT_TOUCH = 2,
    OPEN_CFW_TOUCH_POWER_EVENT_ALERT = 3
} open_cfw_touch_power_event;

typedef enum open_cfw_touch_gesture {
    OPEN_CFW_TOUCH_GESTURE_NONE = 0,
    OPEN_CFW_TOUCH_GESTURE_LEFT = 1,
    OPEN_CFW_TOUCH_GESTURE_RIGHT = 2,
    OPEN_CFW_TOUCH_GESTURE_LONG_PRESS = 3,
    OPEN_CFW_TOUCH_GESTURE_FIVE_FAST_CLICKS = 4
} open_cfw_touch_gesture;

typedef struct open_cfw_touch_scan_port {
    int (*program_channel)(void *context, const uint32_t words[6]);
    int (*run_conversion)(void *context, uint32_t selector);
    uint16_t (*read_result)(void *context, size_t channel);
    void *context;
} open_cfw_touch_scan_port;

typedef struct open_cfw_touch_gesture_state {
    int16_t press_position;
    int16_t last_position;
    uint16_t press_duration_ms;
    uint16_t long_press_ms;
    uint16_t swipe_threshold;
    uint8_t fast_clicks;
    uint8_t pressed;
} open_cfw_touch_gesture_state;

int open_cfw_touch_msc_scan(const uint32_t *descriptors,
                            size_t descriptor_stride_words,
                            size_t channel_count, uint16_t *maximum,
                            const open_cfw_touch_scan_port *port);
open_cfw_touch_power_state open_cfw_touch_power_transition(
    open_cfw_touch_power_state state, open_cfw_touch_power_event event);
void open_cfw_touch_gesture_init(open_cfw_touch_gesture_state *state,
                                 uint16_t long_press_ms,
                                 uint16_t swipe_threshold);
open_cfw_touch_gesture open_cfw_touch_gesture_press(
    open_cfw_touch_gesture_state *state, int16_t position);
open_cfw_touch_gesture open_cfw_touch_gesture_release(
    open_cfw_touch_gesture_state *state, int16_t position,
    uint16_t duration_ms, int fast_click);
uint16_t open_cfw_touch_calibration_threshold(uint16_t maximum,
                                              uint16_t baseline,
                                              uint16_t margin);

#endif
