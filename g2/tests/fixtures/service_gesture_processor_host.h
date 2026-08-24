#ifndef OPEN_CFW_SERVICE_GESTURE_PROCESSOR_HOST_H
#define OPEN_CFW_SERVICE_GESTURE_PROCESSOR_HOST_H

#include <stdint.h>

extern uint8_t open_cfw_test_gesture_proximity;
extern uint8_t open_cfw_test_gesture_debug;
extern const char *open_cfw_test_gesture_names[256];
extern char open_cfw_test_gesture_mask_buffer[96];
extern uint8_t open_cfw_test_gesture_frame[16];
extern uint32_t open_cfw_test_gesture_product_mode;
extern uint32_t open_cfw_test_gesture_buzzer_count;
extern uint32_t open_cfw_test_gesture_buzzer_type;
extern uint32_t open_cfw_test_gesture_notify_count;
extern uint32_t open_cfw_test_gesture_notify_selector;
extern uint32_t open_cfw_test_gesture_notify_value;
extern uint32_t open_cfw_test_gesture_touch_stop_count;
extern uint32_t open_cfw_test_gesture_baseline_count;
extern uint32_t open_cfw_test_gesture_publish_count;
extern uint32_t open_cfw_test_gesture_publish_records[32][4];

void open_cfw_test_gesture_reset(void);
void open_cfw_test_gesture_touch_read(uint8_t *data);
uint32_t open_cfw_test_gesture_product_mode_get(void);
void open_cfw_test_gesture_buzzer_play(uint32_t type);
void open_cfw_test_gesture_notify(uint32_t selector, uint32_t value);
void open_cfw_test_gesture_touch_stop(void);
void open_cfw_test_gesture_prepare_baseline(uint32_t *value);
uint32_t open_cfw_test_gesture_timestamp(void);
void open_cfw_test_gesture_publish(
    uint16_t timestamp, uint32_t event, uint32_t argument0,
    uint32_t argument1
);

#define OPEN_CFW_GESTURE_PROXIMITY_CELL open_cfw_test_gesture_proximity
#define OPEN_CFW_GESTURE_DEBUG_CELL open_cfw_test_gesture_debug
#define OPEN_CFW_GESTURE_NAME_TABLE open_cfw_test_gesture_names
#define OPEN_CFW_GESTURE_MASK_BUFFER open_cfw_test_gesture_mask_buffer
#define OPEN_CFW_GESTURE_MASK_PRESS "PRESS"
#define OPEN_CFW_GESTURE_MASK_RELEASE "RELEASE"
#define OPEN_CFW_GESTURE_MASK_SINGLE "SINGLE"
#define OPEN_CFW_GESTURE_MASK_DOUBLE "DOUBLE"
#define OPEN_CFW_GESTURE_MASK_LONG "LONG"
#define OPEN_CFW_GESTURE_MASK_SLIDE_LEFT "SLIDE_L"
#define OPEN_CFW_GESTURE_MASK_SLIDE_RIGHT "SLIDE_R"
#define OPEN_CFW_GESTURE_MASK_ERROR "ERROR"
#define OPEN_CFW_GESTURE_LOG_LEVEL() 0u
#define OPEN_CFW_GESTURE_LOG(...) ((void)0)
#define OPEN_CFW_GESTURE_TRACE(...) ((void)0)
#define OPEN_CFW_GESTURE_HEXDUMP(data, size) ((void)(data), (void)(size))
#define OPEN_CFW_GESTURE_TOUCH_READ(data) open_cfw_test_gesture_touch_read(data)
#define OPEN_CFW_GESTURE_TOUCH_STOP() open_cfw_test_gesture_touch_stop()
#define OPEN_CFW_GESTURE_TOUCH_PREPARE_BASELINE(value) \
    open_cfw_test_gesture_prepare_baseline(value)
#define OPEN_CFW_GESTURE_PRODUCT_MODE() open_cfw_test_gesture_product_mode_get()
#define OPEN_CFW_GESTURE_BUZZER_PLAY(type) open_cfw_test_gesture_buzzer_play(type)
#define OPEN_CFW_GESTURE_PROXIMITY_NOTIFY(selector, value) \
    open_cfw_test_gesture_notify((selector), (value))
#define OPEN_CFW_GESTURE_TIMESTAMP() open_cfw_test_gesture_timestamp()
#define OPEN_CFW_GESTURE_PUBLISH(timestamp, event, argument0, argument1) \
    open_cfw_test_gesture_publish((timestamp), (event), (argument0), (argument1))

#endif
