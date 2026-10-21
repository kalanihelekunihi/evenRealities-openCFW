#ifndef TOUCH_SCAN_FRAME_OFFLINE_H
#define TOUCH_SCAN_FRAME_OFFLINE_H
#include <stdint.h>
void touch_load_scan_frame(volatile uint32_t *hw,uint32_t mode,const uint32_t *frame);
void touch_start_scan_frame(const uint32_t *frame,const uint8_t *context);
#endif
