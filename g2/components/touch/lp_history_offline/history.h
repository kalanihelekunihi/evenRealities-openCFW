#ifndef TOUCH_LP_HISTORY_OFFLINE_H
#define TOUCH_LP_HISTORY_OFFLINE_H
#include <stdint.h>
/* Reconstructed stock7e04 tuner/history gate reset; does not clear samples. */
void touch_lp_history_reset(uint8_t *context);
/* New offline/app decoder, not a claimed stock software consumer. Capacity is
 * supplied by caller; actual generated history allocation remains unknown.
 * enabled_at_capture is a slot-position mask snapshot, not current enable state. */
typedef struct {uint16_t value;uint8_t slot,frame,counter,baseline_reset,baseline_valid,written;} touch_lp_sample;
enum {TOUCH_LP_SAMPLE=0,TOUCH_LP_DISABLED=1,TOUCH_LP_EMPTY=2,TOUCH_LP_BAD_META=3,TOUCH_LP_TOO_SHORT=4,TOUCH_LP_UNWRITTEN=5};
uint32_t touch_lp_history_span(const uint8_t *common,uint32_t capacity,uint32_t *needed);
uint32_t touch_lp_history_read(const uint8_t *common,const uint8_t *history,uint32_t capacity,uint32_t enabled_at_capture,uint32_t frame,uint32_t slot,touch_lp_sample *sample);
#endif
