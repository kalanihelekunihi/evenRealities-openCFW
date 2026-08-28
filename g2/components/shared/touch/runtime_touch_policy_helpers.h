/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_POLICY_HELPERS_H
#define OPEN_CFW_RUNTIME_TOUCH_POLICY_HELPERS_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC 0x45564E55UL
#define OPEN_CFW_TOUCH_POLICY_CONFIG_BYTES 8U
#define OPEN_CFW_TOUCH_POLICY_STORAGE_LIMIT 256U
#define OPEN_CFW_TOUCH_POLICY_DEFAULT_TIMEOUT_MS 1000U
#define OPEN_CFW_TOUCH_POLICY_ATTENTION_REARM_MS 200U

typedef enum open_cfw_touch_policy_status {
    OPEN_CFW_TOUCH_POLICY_OK = 0,
    OPEN_CFW_TOUCH_POLICY_UNAVAILABLE = -1,
    OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT = -2,
    OPEN_CFW_TOUCH_POLICY_OUT_OF_RANGE = -3,
    OPEN_CFW_TOUCH_POLICY_NOT_READY = -4,
    OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR = -5,
    OPEN_CFW_TOUCH_POLICY_INVALID_DATA = -6
} open_cfw_touch_policy_status;

typedef enum open_cfw_touch_policy_gesture {
    OPEN_CFW_TOUCH_POLICY_GESTURE_NONE = 0,
    OPEN_CFW_TOUCH_POLICY_GESTURE_LEFT = 1,
    OPEN_CFW_TOUCH_POLICY_GESTURE_RIGHT = 2,
    OPEN_CFW_TOUCH_POLICY_GESTURE_LONG_PRESS = 3,
    OPEN_CFW_TOUCH_POLICY_GESTURE_FIVE_FAST_CLICKS = 4
} open_cfw_touch_policy_gesture;

typedef struct open_cfw_touch_policy_config {
    uint32_t magic;
    uint16_t proximity_baseline;
    uint16_t long_press_ms;
} open_cfw_touch_policy_config;

typedef struct open_cfw_touch_policy_gesture_observation {
    int16_t position;
    uint16_t proximity;
    uint16_t elapsed_ms;
    uint8_t pressed;
    uint8_t fast_click;
} open_cfw_touch_policy_gesture_observation;

typedef struct open_cfw_touch_policy_provider {
    int (*storage_ready)(void *context);
    int (*storage_read)(void *context, uint32_t offset,
                        uint8_t *destination, size_t size);
    int (*attention_release_timeout_rearm)(void *context, uint32_t delay_ms);
    int (*gesture_policy_step)(
        void *context,
        const open_cfw_touch_policy_gesture_observation *observation,
        open_cfw_touch_policy_gesture *gesture);
    int (*baseline_update)(void *context, uint16_t saved_baseline,
                           uint16_t *current_baseline);
    void *context;
} open_cfw_touch_policy_provider;

typedef struct open_cfw_touch_policy_state {
    open_cfw_touch_policy_config config;
    uint16_t timeout_ms;
    uint16_t current_baseline;
    uint8_t config_valid;
} open_cfw_touch_policy_state;

void open_cfw_touch_policy_defaults(open_cfw_touch_policy_state *state);
int open_cfw_touch_policy_config_read(
    const open_cfw_touch_policy_provider *provider, uint32_t offset,
    uint8_t *destination, size_t size);
int open_cfw_touch_policy_config_load(
    open_cfw_touch_policy_state *state,
    const open_cfw_touch_policy_provider *provider);
int open_cfw_touch_policy_saved_baseline_read(
    const open_cfw_touch_policy_state *state, uint16_t *baseline);
uint16_t open_cfw_touch_policy_timeout_default(uint16_t timeout_ms);
int open_cfw_touch_policy_attention_rearm(
    const open_cfw_touch_policy_provider *provider);
int open_cfw_touch_policy_gesture_step(
    const open_cfw_touch_policy_provider *provider,
    const open_cfw_touch_policy_gesture_observation *observation,
    open_cfw_touch_policy_gesture *gesture);
int open_cfw_touch_policy_baseline_update(
    open_cfw_touch_policy_state *state,
    const open_cfw_touch_policy_provider *provider);

#endif
