#ifndef CASE_FRAME_DISPATCH_H
#define CASE_FRAME_DISPATCH_H
#include <stdint.h>
uint32_t case_hex_digit(uint32_t);
void case_dispatch_received_frame(void);
/* Selected polling bit8 action only; other poll actions/loop excluded. */
void case_poll_frame_action(uint32_t snapshot);
#endif
