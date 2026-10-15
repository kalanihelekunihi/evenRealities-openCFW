/* Apollo Ambiq draw-unit and vector array state (native RAM address labels). */
#include <stdint.h>

/* Native 0x200746c0 and 0x200746c4. */
volatile uint32_t audio_uart_ambiq_unit_cell[1];
volatile uint32_t audio_uart_ambiq_vector_current_path_200746c4;

/* Native 0x20073cc0 and 0x20073cd4: 20-byte LV array headers. */
uint8_t audio_uart_ambiq_vector_path_segments_20073cc0[20]
    __attribute__((aligned(4)));
uint8_t audio_uart_ambiq_vector_path_data_20073cd4[20]
    __attribute__((aligned(4)));
_Static_assert(sizeof(audio_uart_ambiq_vector_path_segments_20073cc0)==20,
               "segment array header size");
_Static_assert(sizeof(audio_uart_ambiq_vector_path_data_20073cd4)==20,
               "data array header size");
