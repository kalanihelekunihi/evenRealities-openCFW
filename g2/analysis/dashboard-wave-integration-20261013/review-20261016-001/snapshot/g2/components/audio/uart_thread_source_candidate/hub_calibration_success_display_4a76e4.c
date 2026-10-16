/* Native hub_calibration_success_display 0x4a76e4..0x4a774e. */
#include <stdint.h>

extern uint32_t audio_uart_calibration_success_primary_200749ac;
extern uint32_t audio_uart_calibration_success_secondary_200749b0;
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern void audio_uart_page_49942e(uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f66c(uint32_t);
extern uint32_t audio_uart_lv_obj_width_43fd9e(uint32_t);
extern void audio_uart_page_43f0e0(uint32_t, int32_t);

static const char primary_id[] = "ID_HEADUP_CALIBRATION_SUCCESSFUL_1";
static const char secondary_id[] = "ID_HEADUP_CALIBRATION_SUCCESSFUL_2";

void audio_uart_hub_calibration_success_display_4a76e4(void) {
    if (audio_uart_calibration_success_primary_200749ac != 0u) {
        const uint32_t length = audio_uart_page_460084(primary_id);
        const uint32_t text = audio_uart_page_45fffe(primary_id, length);
        audio_uart_page_49942e(audio_uart_calibration_success_primary_200749ac,
                                text);
    }
    if (audio_uart_calibration_success_secondary_200749b0 != 0u) {
        const uint32_t length = audio_uart_page_460084(secondary_id);
        const uint32_t text = audio_uart_page_45fffe(secondary_id, length);
        const uint32_t object = audio_uart_calibration_success_secondary_200749b0;
        audio_uart_page_49942e(object, text);
        audio_uart_page_43f506(object, 0x3fffffffu);
        audio_uart_page_43f66c(object);
        const uint32_t width = audio_uart_lv_obj_width_43fd9e(object);
        audio_uart_page_43f0e0(object, (int32_t)(0x240u - width) / 2);
    }
}
