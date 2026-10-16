/* Terminal query-permission dialog constructor, stock 0x5ec82a..0x5ec9bf. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* observed 0x2006e0d0 */
extern uint32_t audio_terminal_display_queue_handle; /* observed 0x20074a90 */
extern uint32_t audio_uart_ring_secondary_head_cell; /* observed 0x200746e0 */
struct terminal_query_image_descriptor {
    uint32_t header, dimensions, stride, data_size;
    const uint8_t *data;
    uint32_t reserved0, reserved1;
};
extern const struct terminal_query_image_descriptor
    audio_terminal_query_image_770890; /* stock 0x770890 */
extern uint32_t audio_uart_device_role_get(void);
extern void *audio_terminal_query_root_5e4f54(uint32_t queue, uint32_t mode);
extern void audio_uart_page_43f4c0(void *, uint32_t, uint32_t);
extern void audio_uart_page_44119c(void *, uint32_t, uint32_t);
extern void audio_uart_page_44120e(void *, uint32_t, uint32_t);
extern void audio_uart_page_44121c(void *, uint32_t, uint32_t);
extern void audio_uart_page_44122a(void *, uint32_t, uint32_t);
extern void audio_uart_page_441238(void *, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(void *, uint32_t);
extern void *audio_uart_page_498668(void *);
extern void audio_uart_page_498680(void *, const void *);
extern void audio_uart_page_43f6b8(void *, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *, uint32_t, uint32_t);
extern void audio_uart_page_44129e(void *, uint32_t, uint32_t);
extern void audio_uart_page_4413ce(void *, uint32_t, uint32_t);
extern const char *audio_terminal_query_session_name_5ec7f0(void);
extern void *audio_uart_page_499416(void *);
extern void audio_uart_page_441180(void *, uint32_t, uint32_t);
extern void audio_uart_page_layout_499678(void *, uint32_t);
extern void audio_lv_label_set_text_fmt_49954c(void *, const char *, ...);
extern void audio_uart_page_44140e(void *, uint32_t, uint32_t);
extern void audio_uart_page_44143e(void *, uint32_t, uint32_t);
extern void audio_uart_page_43f6d6(void *, void *, uint32_t, uint32_t,
                                    uint32_t);
extern void audio_uart_page_43f66c(void *);
extern void *audio_uart_page_overlay_44dca2(void *);
extern uint32_t audio_uart_lv_obj_width_43fd9e(void *);
extern void audio_uart_page_43f506(void *, uint32_t);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void store_u32(uint8_t *p, uint32_t v) {
    p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16); p[3]=(uint8_t)(v>>24);
}

void audio_terminal_query_visibility_5ec82a(void) {
    uint8_t *s=audio_terminal_ui_state_base;
    const uint32_t role=audio_uart_device_role_get();
    const uint32_t shift=role==1u ? (uint32_t)-8 : 8u;
    if (audio_terminal_display_queue_handle==0u ||
        load_u32(s+0x224u)!=0u) return;
    void *root=audio_terminal_query_root_5e4f54(
        audio_terminal_display_queue_handle,1u);
    store_u32(s+0x224u,(uint32_t)(uintptr_t)root);
    const uint32_t full=0x3fffffffu;
    audio_uart_page_43f4c0(root,full,full);
    audio_uart_page_44119c(root,0x44u,0u);
    audio_uart_page_44120e(root,6u,0u);
    audio_uart_page_44121c(root,6u,0u);
    audio_uart_page_44122a(root,12u,0u);
    audio_uart_page_441238(root,12u,0u);
    audio_uart_page_43dfa4(root,0x10u);
    void *image=audio_uart_page_498668(root);
    audio_uart_page_498680(image,&audio_terminal_query_image_770890);
    audio_uart_page_43f4c0(image,full,full);
    audio_uart_page_43f6b8(image,7u,0u,0u);
    audio_uart_page_44127e(image,audio_uart_page_44104c(0u),0u);
    audio_uart_page_44129e(image,0xffu,0u);
    audio_uart_page_4413ce(image,0xffu,0u);
    const uint32_t session=load_u32(s+0x288u);
    const char *name=audio_terminal_query_session_name_5ec7f0();
    void *label=audio_uart_page_499416(root);
    store_u32(s+0x228u,(uint32_t)(uintptr_t)label);
    audio_uart_page_441180(label,0x1e0u,0u);
    audio_uart_page_layout_499678(label,0u);
    if (name!=0)
        audio_lv_label_set_text_fmt_49954c(label,"%s\nPermission needed",name);
    else
        audio_lv_label_set_text_fmt_49954c(label,"Session %lu\nPermission needed",session);
    audio_uart_page_44140e(label,audio_uart_page_44104c(0x00ffffffu),0u);
    audio_uart_page_44143e(label,audio_uart_ring_secondary_head_cell,0u);
    audio_uart_page_43f6d6(label,image,0x14u,0xcu,0u);
    audio_uart_page_43f66c(root);
    void *parent=audio_uart_page_overlay_44dca2(root);
    if(parent!=0) {
        audio_uart_page_43f506(parent,audio_uart_lv_obj_width_43fd9e(label)+0x54u);
        audio_uart_page_43f6b8(root,2u,shift,0u);
    }
    store_u32(s+0x22cu,0u);
}
