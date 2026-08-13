/*
 * Freestanding declaration surface used only to compile the authenticated
 * cmsis_os2.c with Apple's arm-none-eabi Clang, which ships no target libc
 * sysroot.  The wrapper uses only memcpy; its implementation remains an
 * explicit external seam.
 */

#ifndef OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_STRING_H
#define OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_STRING_H

#include <stddef.h>

void *memcpy(void *destination, const void *source, size_t count);

#endif /* OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_STRING_H */
