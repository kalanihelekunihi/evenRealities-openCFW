#ifndef AUDIO_XTAL_REQUEST_H
#define AUDIO_XTAL_REQUEST_H
#include <stdint.h>
/* Stock20-byte board layout. Padding copied unchanged; no SIP field. */
typedef struct {uint8_t hs_mode,pad_hs[3];uint32_t hs_hz;uint8_t ls_mode,pad_ls[3];uint32_t ls_hz,external_hz;} audio_clock_board_info;
uint32_t audio_clock_board_set(const void *info);
void audio_clock_counter_wait(volatile uint8_t *flag,volatile uint32_t *counter);
void audio_xtal_wait(volatile uint32_t *counter);
uint32_t audio_xtal_request(uint32_t user);
/* Stock HFRC configuration lead0x4C38A0, accepts frequency0 or48MHz. */
uint32_t audio_hfrc_config(uint32_t requested,const uint32_t *config);
#endif
