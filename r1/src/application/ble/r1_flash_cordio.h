#ifndef R1_FLASH_CORDIO_H
#define R1_FLASH_CORDIO_H

#include <stdbool.h>

void r1_cordio_flash_register(void);
void r1_cordio_flash_service(void);
void r1_cordio_flash_disable(void);
bool r1_cordio_flash_busy(void);
void r1_cordio_flash_wait_for_shutdown(void);

#endif
