#ifndef CASE_FRAME_CALLBACK_OFFLINE_H
#define CASE_FRAME_CALLBACK_OFFLINE_H
#include "../uart_start_offline/start.h"
void case_frame_callback(case_start_handle *);
void case_frame_resync(void);
uint32_t case_frame_de_prefix(const uint8_t *);
#endif
