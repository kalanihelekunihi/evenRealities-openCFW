/* Stock LVGL animimage factory 0x597e90..0x597ea5 and class 0x7550dc. */
#include <stdint.h>
extern const uint8_t audio_uart_image_class_756108[];
extern void audio_terminal_voice_anim_ctor_597fae(void);
extern void *audio_uart_page_create_44cf98(const void *,void *);
extern void audio_uart_page_initialize_44d0f0(void *);

struct terminal_voice_anim_class_layout {
    uintptr_t base_class,constructor,destructor,event;
    uint32_t reserved;
    uintptr_t name;
    uint32_t default_width,default_height,instance_size;
};
_Static_assert(sizeof(struct terminal_voice_anim_class_layout)==36u,
               "Apollo animimage class record size");
const char audio_terminal_voice_anim_class_name_78ac04[]="lv_animimg";
const struct terminal_voice_anim_class_layout
audio_terminal_voice_anim_class_7550dc={
    (uintptr_t)audio_uart_image_class_756108,
    (uintptr_t)&audio_terminal_voice_anim_ctor_597fae,
    0u,0u,0u,
    (uintptr_t)audio_terminal_voice_anim_class_name_78ac04,
    0u,0u,0xc40u
};

void *audio_terminal_voice_anim_create_597e90(void *parent) {
    void *object=audio_uart_page_create_44cf98(
        &audio_terminal_voice_anim_class_7550dc,parent);
    audio_uart_page_initialize_44d0f0(object);
    return object;
}
