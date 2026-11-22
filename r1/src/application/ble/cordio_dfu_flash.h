#ifndef R1_CORDIO_DFU_FLASH_H
#define R1_CORDIO_DFU_FLASH_H

#include <stdint.h>

void r1_cordio_dfu_flash_register(void);
void r1_cordio_dfu_flash_service(void);
uint32_t r1_cordio_dfu_flash_erase(uint32_t page_number);
uint32_t r1_cordio_dfu_flash_write(uint32_t *destination,
                                   const uint32_t *source, uint32_t words);

#endif
