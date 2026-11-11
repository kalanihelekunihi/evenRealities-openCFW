#ifndef R1_NATIVE_APPLICATION_MANAGER_H
#define R1_NATIVE_APPLICATION_MANAGER_H
#include <stdint.h>
extern volatile uint8_t r1_application_manager_ready;
void r1_application_manager_thread(void *argument);
#endif
