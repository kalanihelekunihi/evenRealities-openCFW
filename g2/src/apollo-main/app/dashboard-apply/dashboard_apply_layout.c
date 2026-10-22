/* Native 0x502174, dashboard_ext_apply_layout_pb_to_layout.
 * The decoded protobuf object and its ready byte are shared with 0x501d5c.
 * Layout persistence (0x558376) and diagnostic literals remain typed children.
 */
#include <stdint.h>
#include <stddef.h>

extern volatile uint8_t audio_uart_dashboard_ready;
extern uint8_t audio_uart_dashboard_decoded[188];
extern const char audio_uart_dashboard_module[], audio_uart_dashboard_source[];
extern const char audio_uart_dashboard_apply_function[];
extern const char audio_uart_dashboard_apply_e_not_loaded[],audio_uart_dashboard_apply_c_not_loaded[];
extern const char audio_uart_dashboard_apply_e_position[],audio_uart_dashboard_apply_c_position[];
extern const char audio_uart_dashboard_apply_e_widget[],audio_uart_dashboard_apply_c_widget[];
extern const char audio_uart_dashboard_apply_e_missing_face[],audio_uart_dashboard_apply_c_missing_face[];
extern const char audio_uart_dashboard_apply_e_face[],audio_uart_dashboard_apply_c_face[];
extern const char audio_uart_dashboard_apply_e_set_failed[],audio_uart_dashboard_apply_c_set_failed[];
extern const char audio_uart_dashboard_apply_e_success[],audio_uart_dashboard_apply_c_success[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern int32_t audio_dashboard_layout_set(const void *); /* native 0x558376 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* native 0x48949c */
extern void *audio_dashboard_copy_limited(void *,const void *,uint32_t); /* native 0x44b5a0 */

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
static uint32_t rd32(const uint8_t *p) { return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24); }
static void wr32(uint8_t *p,uint32_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24); }
static int32_t fail0(uint32_t line,const char *e,const char *c,uint32_t compact,uint8_t level) {
    if(audio_log_flags()&2u) audio_log_extended(level,audio_uart_dashboard_module,audio_uart_dashboard_source,
        audio_uart_dashboard_apply_function,line,e);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,c,c);
    (void)audio_dashboard_layout_set(0);
    return -1;
}
static int32_t fail1(uint32_t line,const char *e,const char *c,uint32_t compact,uint32_t x) {
    if(audio_log_flags()&2u) audio_log_extended(2u,audio_uart_dashboard_module,audio_uart_dashboard_source,
        audio_uart_dashboard_apply_function,line,e,x);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,c,c,x);
    (void)audio_dashboard_layout_set(0);
    return -1;
}

/* Stock 0x00502174 (dashboard_ext_apply_layout_pb_to_runtime_502174) */
int32_t audio_dashboard_apply_layout_pb(void) {
    const uint8_t *p=audio_uart_dashboard_decoded;
    if(!audio_uart_dashboard_ready)
        return fail0(0x36du,audio_uart_dashboard_apply_e_not_loaded,audio_uart_dashboard_apply_c_not_loaded,0xc000000u,3u);
    uint8_t layout[128];
    audio_uart_buffer_zero(layout,128u,0u);
    uint8_t position=p[0x30u];
    if(position>2u) return fail1(0x382u,audio_uart_dashboard_apply_e_position,audio_uart_dashboard_apply_c_position,0x8400000u,position);
    layout[0]=position;
    uint32_t widget_count=p[0x34u];
    uint32_t n=rd16(p+0x38u);
    if((uint8_t)n<widget_count) widget_count=n;
    if(widget_count>5u) widget_count=5u;
    layout[1]=(uint8_t)widget_count;
    for(uint32_t i=0;i<widget_count;i++) {
        uint8_t w=p[0x3au+i];
        if(w>4u) {
            if(audio_log_flags()&2u) audio_log_extended(2u,audio_uart_dashboard_module,audio_uart_dashboard_source,
                audio_uart_dashboard_apply_function,0x3a7u,audio_uart_dashboard_apply_e_widget,i,w);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x8800000u,audio_uart_dashboard_apply_c_widget,
                    audio_uart_dashboard_apply_c_widget,i,w);
            (void)audio_dashboard_layout_set(0);
            return -1;
        }
        layout[2u+i]=w;
    }
    if(!p[0x3fu]) return fail0(0x3b2u,audio_uart_dashboard_apply_e_missing_face,
        audio_uart_dashboard_apply_c_missing_face,0x8000000u,2u);
    uint16_t face=rd16(p+0x40u);
    if(face<1u||face>4u) return fail1(0x3fdu,audio_uart_dashboard_apply_e_face,
        audio_uart_dashboard_apply_c_face,0x8400000u,face);
    layout[8]=(uint8_t)face;
    layout[12]=(uint8_t)rd32(p+0x44u);
    if(face==1u) {
        layout[13]=p[0x48u];layout[14]=p[0x49u];
    } else if(face==2u||face==3u) {
        layout[13]=(uint8_t)rd32(p+0x48u);layout[14]=(uint8_t)rd32(p+0x4cu);
        if(face==2u) {
            uint32_t count=(uint8_t)rd16(p+0x50u);
            if(count>3u) count=3u;
            layout[15]=(uint8_t)count;
            for(uint32_t i=0;i<count;i++) layout[16u+i]=p[0x52u+i];
        }
    } else {
        layout[13]=(uint8_t)rd32(p+0x48u);
        uint32_t count=(uint8_t)rd16(p+0xaeu);
        if(count>3u) count=3u;
        layout[14]=(uint8_t)count;
        for(uint32_t i=0;i<count;i++) wr32(layout+16u+4u*i,rd32(p+0xb0u+4u*i));
        count=(uint8_t)rd16(p+0x4cu);
        if(count>3u) count=3u;
        layout[28]=(uint8_t)count;
        for(uint32_t i=0;i<count;i++) {
            (void)audio_dashboard_copy_limited(layout+29u+32u*i,p+0x4eu+32u*i,31u);
            layout[60u+32u*i]=0u;
        }
    }
    if(audio_dashboard_layout_set(layout)!=0) {
        if(audio_log_flags()&2u) audio_log_extended(2u,audio_uart_dashboard_module,audio_uart_dashboard_source,
            audio_uart_dashboard_apply_function,0x409u,audio_uart_dashboard_apply_e_set_failed);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x8000000u,audio_uart_dashboard_apply_c_set_failed,
                audio_uart_dashboard_apply_c_set_failed);
        return -1;
    }
    if(audio_log_flags()&2u) audio_log_extended(3u,audio_uart_dashboard_module,audio_uart_dashboard_source,
        audio_uart_dashboard_apply_function,0x40eu,audio_uart_dashboard_apply_e_success,
        layout[0],layout[1],layout[8]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xcc00000u,audio_uart_dashboard_apply_c_success,
            audio_uart_dashboard_apply_c_success,layout[0],layout[1],layout[8]);
    return 0;
}
