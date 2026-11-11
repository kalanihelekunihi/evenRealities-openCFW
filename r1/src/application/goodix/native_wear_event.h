#ifndef R1_NATIVE_WEAR_EVENT_H
#define R1_NATIVE_WEAR_EVENT_H
#include <stdint.h>

/* The generated Goodix hook unit includes this declaration where its demo
 * implementation was removed. The single implementation is compiled from C
 * in native_wear_event.c with its own frame-pointer profile. */
void Gh3x2x_WearEventHook(uint16_t event, uint8_t extra);

#endif
