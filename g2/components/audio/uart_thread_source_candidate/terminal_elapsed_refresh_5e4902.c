/* Stock Terminal elapsed-label refresh 0x5e4902. */
#include <stdint.h>

extern uint32_t audio_td_counter_b_get(void); /* C-owned stock 0x5973dc */
extern uint32_t audio_td_record_elapsed_get_59769c(uint32_t record,
                                                    uint32_t *seconds);
extern void audio_terminal_elapsed_text_5e48b8(uint32_t seconds);
extern void audio_terminal_elapsed_clear_5e4894(void);

void audio_terminal_elapsed_refresh_5e4902(void) {
    uint32_t seconds;
    uint32_t record = audio_td_counter_b_get();
    if (audio_td_record_elapsed_get_59769c(record, &seconds) != 0u)
        audio_terminal_elapsed_text_5e48b8(seconds);
    else
        audio_terminal_elapsed_clear_5e4894();
}
