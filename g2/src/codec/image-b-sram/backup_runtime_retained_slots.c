/* Source-owned image-B SRAM cells outside the native CRT clear range.
 * No initializer is asserted for any of these retained/shared cells.
 * The final linker must place each named section at its authenticated
 * address and mark it NOLOAD. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_process_energy_first_use_2002d79c
    __attribute__((section(".image_b_retained.energy"), used));
volatile uint32_t gx8002_image_b_process_ring_counter_2002d7a0
    __attribute__((section(".image_b_retained.ring"), used));
volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4]
    __attribute__((section(".image_b_retained.dsp_operations"), used));
volatile uint32_t gx8002_image_b_imcra_setting_2002d7b4
    __attribute__((section(".image_b_retained.imcra_setting"), used));

_Static_assert(sizeof(gx8002_image_b_dsp_config_2002d7a4) == 16,
               "native DSP operation table spans four words");
