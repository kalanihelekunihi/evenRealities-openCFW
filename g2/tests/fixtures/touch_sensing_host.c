/* SPDX-License-Identifier: MIT */
/* Host fixture for clean-room touch sensing and gesture policy. */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_sensing.c"

typedef struct scan_fixture {
    uint32_t programs;
    uint32_t conversions;
    uint32_t selector;
    uint32_t last_words[6];
    int fail_channel;
} scan_fixture;

static int program(void *context, const uint32_t words[6])
{
    scan_fixture *fixture = context;
    unsigned index;
    ++fixture->programs;
    for (index = 0U; index < 6U; ++index) fixture->last_words[index] = words[index];
    return fixture->fail_channel != (int)fixture->programs;
}

static int convert(void *context, uint32_t selector)
{
    scan_fixture *fixture = context;
    ++fixture->conversions;
    fixture->selector = selector;
    return 1;
}

static uint16_t read_result(void *context, size_t channel)
{
    (void)context;
    static const uint16_t values[3] = {100U, 700U, 350U};
    return values[channel];
}

uint32_t open_cfw_test_touch_msc_scan(void)
{
    uint32_t descriptors[3][8] = {{1U,2U,3U,4U,5U,0xFFFFFFFFU,7U,8U},
                                  {9U,10U,11U,12U,13U,0U,15U,16U},
                                  {17U,18U,19U,20U,21U,0x12345678U,23U,24U}};
    scan_fixture fixture = {0};
    open_cfw_touch_scan_port port = {program, convert, read_result, &fixture};
    uint16_t maximum = 0U;
    uint32_t result = 0U;
    result |= open_cfw_touch_msc_scan(&descriptors[0][0], 8U, 3U,
                                      &maximum, &port) == 0 ? 1U : 0U;
    result |= maximum == 700U && fixture.programs == 3U &&
              fixture.conversions == 3U ? 2U : 0U;
    result |= fixture.selector == 0x6D9U ? 4U : 0U;
    result |= fixture.last_words[3] == 0x00FF0063U &&
              fixture.last_words[4] == 0x00400064U &&
              fixture.last_words[5] ==
              ((0x12345678U & 0xC000FFCAU) | 0x00FF0004U) ? 8U : 0U;
    fixture.programs = 0U; fixture.conversions = 0U; fixture.fail_channel = 2;
    result |= open_cfw_touch_msc_scan(&descriptors[0][0], 8U, 3U,
                                      &maximum, &port) == 4 ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_power_transitions(void)
{
    uint32_t result = 0U;
    result |= open_cfw_touch_power_transition(OPEN_CFW_TOUCH_POWER_ACT,
        OPEN_CFW_TOUCH_POWER_EVENT_INACTIVE) == OPEN_CFW_TOUCH_POWER_ALR ? 1U : 0U;
    result |= open_cfw_touch_power_transition(OPEN_CFW_TOUCH_POWER_ALR,
        OPEN_CFW_TOUCH_POWER_EVENT_ALARM_EXPIRED) == OPEN_CFW_TOUCH_POWER_WOT ? 2U : 0U;
    result |= open_cfw_touch_power_transition(OPEN_CFW_TOUCH_POWER_WOT,
        OPEN_CFW_TOUCH_POWER_EVENT_TOUCH) == OPEN_CFW_TOUCH_POWER_ACT ? 4U : 0U;
    result |= open_cfw_touch_power_transition(OPEN_CFW_TOUCH_POWER_WOT,
        OPEN_CFW_TOUCH_POWER_EVENT_ALERT) == OPEN_CFW_TOUCH_POWER_ALR ? 8U : 0U;
    result |= open_cfw_touch_power_transition(OPEN_CFW_TOUCH_POWER_ACT,
        OPEN_CFW_TOUCH_POWER_EVENT_TOUCH) == OPEN_CFW_TOUCH_POWER_ACT ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_gestures(void)
{
    open_cfw_touch_gesture_state state;
    uint32_t result = 0U;
    unsigned click;
    open_cfw_touch_gesture_init(&state, 800U, 20U);
    open_cfw_touch_gesture_press(&state, 50);
    result |= open_cfw_touch_gesture_release(&state, 80, 100U, 0) ==
              OPEN_CFW_TOUCH_GESTURE_RIGHT ? 1U : 0U;
    open_cfw_touch_gesture_press(&state, 50);
    result |= open_cfw_touch_gesture_release(&state, 20, 100U, 0) ==
              OPEN_CFW_TOUCH_GESTURE_LEFT ? 2U : 0U;
    open_cfw_touch_gesture_press(&state, 50);
    result |= open_cfw_touch_gesture_release(&state, 51, 800U, 0) ==
              OPEN_CFW_TOUCH_GESTURE_LONG_PRESS ? 4U : 0U;
    for (click = 0U; click < 4U; ++click) {
        open_cfw_touch_gesture_press(&state, 50);
        if (open_cfw_touch_gesture_release(&state, 50, 20U, 1) !=
            OPEN_CFW_TOUCH_GESTURE_NONE) return result;
    }
    open_cfw_touch_gesture_press(&state, 50);
    result |= open_cfw_touch_gesture_release(&state, 50, 20U, 1) ==
              OPEN_CFW_TOUCH_GESTURE_FIVE_FAST_CLICKS ? 8U : 0U;
    result |= open_cfw_touch_calibration_threshold(100U, 200U, 50U) == 250U &&
              open_cfw_touch_calibration_threshold(65530U, 1U, 20U) == 65535U
              ? 16U : 0U;
    return result;
}
