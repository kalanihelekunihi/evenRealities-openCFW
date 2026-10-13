#include <stdint.h>
extern void *audio_uart_font_outline_context(void);
extern void audio_uart_ambiq_vector_font_create_53d8fc(void *);
extern void audio_uart_ambiq_vector_font_insert_53da54(void *);
extern void audio_uart_ambiq_vector_font_release_53db3c(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char vector270_message[]="unknown event code: %d";
static const char vector270_function[]="lv_draw_ambiq_vector_font_ft_cb";
static const char vector270_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
/* Native53d82c..53d87c: event-code accessor masks bit15; user-data always loaded. */
void audio_uart_ambiq_vector_font_callback_53d82c(void *event) {
 const volatile uint32_t *e=event;
 uint32_t code=e[2]&~32768u;
 void *data=(void *)(uintptr_t)e[4];
 if(code==36u)audio_uart_ambiq_vector_font_create_53d8fc(data);
 else if(code==40u)audio_uart_ambiq_vector_font_insert_53da54(data);
 else if(code==41u)audio_uart_ambiq_vector_font_release_53db3c((void *)(uintptr_t)*(volatile uint32_t *)data);
 else audio_uart_lvgl_log(2u,vector270_file,186u,vector270_function,vector270_message,code);
}
/* Native529bf2..529bfe: only callback is stored; two incoming args are unused. */
void audio_uart_font_outline_register_529bf2(uintptr_t callback,uint32_t unused,void *unit) {
 (void)unused;(void)unit;
 volatile uint32_t *context=audio_uart_font_outline_context();
 context[4]=(uint32_t)callback;
}
/* Native53d6da..53d6ea: registers the source callback with the original arguments. */
void audio_uart_ambiq_vector_font_init_53d6da(void *unit) {
 audio_uart_font_outline_register_529bf2((uintptr_t)audio_uart_ambiq_vector_font_callback_53d82c,0u,unit);
}
