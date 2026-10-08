#ifndef TOUCH_SLIDER_PRODUCER_OFFLINE_H
#define TOUCH_SLIDER_PRODUCER_OFFLINE_H
#include <stdint.h>
typedef struct {uint16_t raw,baseline,difference;uint8_t status,negative_reset,baseline_fraction,compensation;} touch_sensor_layout;
_Static_assert(sizeof(touch_sensor_layout)==10,"sensor ABI");
uint32_t touch_position_iir(uint32_t sample,uint32_t prior,uint32_t coefficient);
void touch_linear_centroid(uint8_t *touch,const uint8_t *widget);
void touch_position_filters(uint8_t *touch,const uint8_t *widget);
void touch_slider_process(uint8_t *widget);
/* Widget144-byte configuration, context60 bytes; bounded numSns>=3 allocation.
 * Native local non-X position fields are definedzero; stock uninitialized stack
 * bytes outside X/count are excluded from equivalence claims. */
/* Selected actual slider raw path: software rawfilterbits4/7/10 are disabled
 * in locked widget1 flags0x6000; HW-IIR/commonmode acquisition remain external. */
uint32_t touch_sensor_baseline(uint8_t *widget_context,uint8_t *sensor,const uint8_t *context);
void touch_sensor_difference(const uint8_t *widget_context,uint8_t *sensor);
void touch_slider_clamp(uint32_t widget_id,const uint8_t *context);
uint32_t touch_slider_raw(uint32_t widget_id,const uint8_t *context);
uint32_t touch_slider_widget(uint32_t widget_id,uint8_t *context);

#endif
