#include <stdint.h>
extern void case_uart_dma_abort_callback(uint8_t *);
extern uint32_t case_boot_sensor_cancel_callback(uint32_t);
_Static_assert(__builtin_types_compatible_p(__typeof__(&case_uart_dma_abort_callback),void (*)(uint8_t *)), "DMA target type");
_Static_assert(__builtin_types_compatible_p(__typeof__(&case_boot_sensor_cancel_callback),uint32_t (*)(uint32_t)), "cancel target type");
_Static_assert(!__builtin_types_compatible_p(void (*)(void *),void (*)(uint8_t *)), "original DMA call types differ");
_Static_assert(!__builtin_types_compatible_p(void (*)(uint32_t),uint32_t (*)(uint32_t)), "original cancel return types differ");
