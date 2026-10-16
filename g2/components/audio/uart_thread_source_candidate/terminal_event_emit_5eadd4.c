/* Stock Terminal mode/event dispatcher 0x5eadd4. */
#include <stdint.h>

extern void audio_terminal_event_type2_5eabde(const void *payload);
extern void audio_terminal_event_type4_5ea9f6(void);
extern void audio_terminal_event_default_5eaad4(const void *payload);
extern void audio_terminal_event_type3_mask_5eaca0(uint32_t mask);

void audio_terminal_event_emit_5eadd4(uint32_t mode,
                                       uint32_t mask,
                                       const void *payload) {
    switch ((uint8_t)mode) {
    case 2u:
        audio_terminal_event_type2_5eabde(payload);
        return;
    case 3u:
        if ((uint16_t)mask == 0xffffu)
            audio_terminal_event_default_5eaad4(payload);
        else
            audio_terminal_event_type3_mask_5eaca0((uint16_t)mask);
        return;
    case 4u:
        audio_terminal_event_type4_5ea9f6();
        return;
    default:
        audio_terminal_event_default_5eaad4(payload);
        return;
    }
}
