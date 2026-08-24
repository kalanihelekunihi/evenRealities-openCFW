#include "service_gesture_processor_host.h"

uint8_t open_cfw_test_gesture_proximity;
uint8_t open_cfw_test_gesture_debug;
const char *open_cfw_test_gesture_names[256];
char open_cfw_test_gesture_mask_buffer[96];
uint8_t open_cfw_test_gesture_frame[16];
uint32_t open_cfw_test_gesture_product_mode;
uint32_t open_cfw_test_gesture_buzzer_count;
uint32_t open_cfw_test_gesture_buzzer_type;
uint32_t open_cfw_test_gesture_notify_count;
uint32_t open_cfw_test_gesture_notify_selector;
uint32_t open_cfw_test_gesture_notify_value;
uint32_t open_cfw_test_gesture_touch_stop_count;
uint32_t open_cfw_test_gesture_baseline_count;
uint32_t open_cfw_test_gesture_publish_count;
uint32_t open_cfw_test_gesture_publish_records[32][4];

void open_cfw_test_gesture_reset(void)
{
    uint32_t index;
    open_cfw_test_gesture_proximity = 0u;
    open_cfw_test_gesture_debug = 0u;
    open_cfw_test_gesture_product_mode = 0u;
    open_cfw_test_gesture_buzzer_count = 0u;
    open_cfw_test_gesture_buzzer_type = 0u;
    open_cfw_test_gesture_notify_count = 0u;
    open_cfw_test_gesture_notify_selector = 0u;
    open_cfw_test_gesture_notify_value = 0u;
    open_cfw_test_gesture_touch_stop_count = 0u;
    open_cfw_test_gesture_baseline_count = 0u;
    open_cfw_test_gesture_publish_count = 0u;
    for (index = 0u; index < 16u; ++index) {
        open_cfw_test_gesture_frame[index] = 0u;
    }
    for (index = 0u; index < 256u; ++index) {
        open_cfw_test_gesture_names[index] = "UNKNOWN";
    }
    open_cfw_test_gesture_names[0] = "OFF";
    open_cfw_test_gesture_names[1] = "ON";
}

void open_cfw_test_gesture_touch_read(uint8_t *data)
{
    uint32_t index;
    for (index = 0u; index < 16u; ++index) {
        data[index] = open_cfw_test_gesture_frame[index];
    }
}

uint32_t open_cfw_test_gesture_product_mode_get(void)
{
    return open_cfw_test_gesture_product_mode;
}

void open_cfw_test_gesture_buzzer_play(uint32_t type)
{
    ++open_cfw_test_gesture_buzzer_count;
    open_cfw_test_gesture_buzzer_type = type;
}

void open_cfw_test_gesture_notify(uint32_t selector, uint32_t value)
{
    ++open_cfw_test_gesture_notify_count;
    open_cfw_test_gesture_notify_selector = selector;
    open_cfw_test_gesture_notify_value = value;
}

void open_cfw_test_gesture_touch_stop(void)
{
    ++open_cfw_test_gesture_touch_stop_count;
}

void open_cfw_test_gesture_prepare_baseline(uint32_t *value)
{
    ++open_cfw_test_gesture_baseline_count;
    *value = 0x12345678u;
}

uint32_t open_cfw_test_gesture_timestamp(void)
{
    return 0x12345u + open_cfw_test_gesture_publish_count;
}

void open_cfw_test_gesture_publish(
    uint16_t timestamp, uint32_t event, uint32_t argument0,
    uint32_t argument1
)
{
    uint32_t index = open_cfw_test_gesture_publish_count;
    if (index < 32u) {
        open_cfw_test_gesture_publish_records[index][0] = timestamp;
        open_cfw_test_gesture_publish_records[index][1] = event;
        open_cfw_test_gesture_publish_records[index][2] = argument0;
        open_cfw_test_gesture_publish_records[index][3] = argument1;
    }
    ++open_cfw_test_gesture_publish_count;
}
