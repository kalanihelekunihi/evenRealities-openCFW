/* Session selector row image/style choice, stock 0x5eccc2..0x5ecd04. */
#include <stdint.h>

extern const uint8_t audio_terminal_session_icon_773060;
extern const uint8_t audio_terminal_query_image_770890;
extern const uint8_t audio_terminal_asset_7733a8;
extern uint8_t audio_terminal_output_style_20003f80[];
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern void audio_terminal_set_label_style_5e482a(void *,const void *,
                                                  uint32_t,uint32_t);

void audio_terminal_session_row_icon_5eccc2(void *image,uint32_t kind,
                                             uint32_t mode) {
    if (image==0) return;
    if ((uint8_t)kind==0u) {
        audio_terminal_image_set_5e47fe(image,&audio_terminal_session_icon_773060);
    } else if ((uint8_t)mode==1u) {
        audio_terminal_set_label_style_5e482a(
            image,audio_terminal_output_style_20003f80,6u,100u);
    } else if ((uint8_t)mode==2u) {
        audio_terminal_image_set_5e47fe(image,&audio_terminal_query_image_770890);
    } else {
        audio_terminal_image_set_5e47fe(image,&audio_terminal_asset_7733a8);
    }
}
