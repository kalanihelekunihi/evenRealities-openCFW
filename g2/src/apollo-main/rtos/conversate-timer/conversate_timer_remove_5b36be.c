/* Native timer callback dispatch 0x5b36be..0x5b3717 and table 0x75ea90. */
#include <stdint.h>

extern void audio_conversate_timer_1_start_5b3766(void);
extern void audio_conversate_timer_1_stop_5b37c8(void);
extern void audio_conversate_timer_2_start_5b37d8(void);
extern void audio_conversate_timer_2_stop_5b383c(void);
extern void audio_conversate_timer_3_start_5b384c(void);
extern void audio_conversate_timer_3_stop_5b38b6(void);

struct timer_callbacks {
    void (*start)(void);
    void (*stop)(void);
};

__attribute__((used, section(".g2_conversate_timer_callbacks_75ea90")))
const struct timer_callbacks audio_conversate_timer_callbacks_75ea90[4] = {
    {0, 0},
    {audio_conversate_timer_1_start_5b3766, audio_conversate_timer_1_stop_5b37c8},
    {audio_conversate_timer_2_start_5b37d8, audio_conversate_timer_2_stop_5b383c},
    {audio_conversate_timer_3_start_5b384c, audio_conversate_timer_3_stop_5b38b6},
};

void audio_conversate_timer_remove_5b36be(uint32_t index, uint32_t slot) {
    uint8_t row = (uint8_t)index;
    uint8_t column = (uint8_t)slot;
    if (row == 0u || row >= 4u)
        return;
    if (column == 1u) {
        void (*callback)(void) = audio_conversate_timer_callbacks_75ea90[row].start;
        if (callback)
            callback();
    } else if (column == 2u) {
        void (*callback)(void) = audio_conversate_timer_callbacks_75ea90[row].stop;
        if (callback)
            callback();
    }
}
