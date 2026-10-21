/* Native Conversate UI callback's directly accessed RAM cells. The registry
   context reservation covers the observed first eight bytes only. */
#include <stdint.h>

__attribute__((used, section(".g2_conversate_registry_context_200004d8")))
uint8_t audio_uart_registry_context_200004d8[8];

__attribute__((used, section(".g2_conversate_ui_start_tick_20074390")))
uint32_t audio_conversate_ui_start_tick_20074390;

__attribute__((used, section(".g2_conversate_ui_app_id_200743a0")))
uint32_t audio_conversate_ui_app_id_200743a0;
