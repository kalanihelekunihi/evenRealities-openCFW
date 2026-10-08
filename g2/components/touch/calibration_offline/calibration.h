#ifndef TOUCH_CALIBRATION_OFFLINE_H
#define TOUCH_CALIBRATION_OFFLINE_H
#include <stdint.h>
uint32_t touch_saved_baseline(void);
uint32_t touch_sensor_active(uint32_t widget,uint32_t sensor,const uint8_t *context);
uint32_t touch_widget_active(uint32_t widget,const uint8_t *context);
uint32_t touch_proximity_change(void);
uint32_t touch_config_save(void);
void touch_calibration_report(void);
void touch_gesture_initialize(uint8_t *state,const uint16_t *parameter);
#endif
