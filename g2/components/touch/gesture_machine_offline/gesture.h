#ifndef TOUCH_GESTURE_MACHINE_OFFLINE_H
#define TOUCH_GESTURE_MACHINE_OFFLINE_H
#include <stdint.h>
typedef struct {uint8_t active,position,padding[2];uint32_t counter;} touch_gesture_sample;
typedef struct {uint8_t position,padding[3];uint32_t counter;} touch_speed_sample;
typedef struct {
 uint16_t hold_threshold;uint8_t reserved[2];
 touch_gesture_sample previous,current,press_start;
 uint32_t hold_elapsed;uint8_t tap_count,pending_tap,padding[2];
 uint32_t release_counter,motion_counter;uint8_t motion_position,motion_padding[3];
 touch_speed_sample speed_samples[3];
 uint8_t speed_index,speed_count,filtered_speed;int8_t direction;
 uint8_t mode,event_flags,event_distance,event_speed;
} touch_gesture_state_layout;
_Static_assert(sizeof(touch_gesture_state_layout)==80,"gesture state ABI");
_Static_assert(__builtin_offsetof(touch_gesture_state_layout,press_start)==20,"press offset");
_Static_assert(__builtin_offsetof(touch_gesture_state_layout,event_flags)==77,"event offset");
enum { TOUCH_GESTURE_PRESS=1,TOUCH_GESTURE_RELEASE=2,TOUCH_GESTURE_SINGLE_TAP=4,
 TOUCH_GESTURE_DOUBLE_TAP=8,TOUCH_GESTURE_HOLD=0x10,
 TOUCH_GESTURE_NEGATIVE_MOTION=0x20,TOUCH_GESTURE_POSITIVE_MOTION=0x40 };
uint8_t *touch_gesture_step(uint8_t *state,uint32_t active,uint8_t position,uint32_t counter);
void touch_gesture_attention_rearm(void);
#endif
