/* Native accessor 0x5b476a..0x5b476f reads byte 0x200d86cc. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[0xb4b1];

uint32_t audio_conversate_prep_note_finish_5b476a(void) {
    return audio_conversate_prep_note_ram_200d7630[0x109c];
}
