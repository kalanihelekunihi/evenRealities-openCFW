/* Native 0x558376 and direct 0x558148/0x558030/0x558040/0x558050
 * descendants. The live layout RAM is an externally placed product cell. */
#include <stdint.h>

extern uint8_t audio_dashboard_layout_current[128]; /* literal 0x5588a8 -> 0x200e7934 */
extern const uint8_t audio_dashboard_layout_default[128]; /* 0x5588ac -> 0x6d52d8 */
extern const char audio_dashboard_layout_module[],audio_dashboard_layout_source[];
extern const char audio_dashboard_layout_set_function[],audio_dashboard_layout_reset_function[];
extern const char audio_dashboard_layout_e_count[],audio_dashboard_layout_c_count[];
extern const char audio_dashboard_layout_e_center[],audio_dashboard_layout_c_center[];
extern const char audio_dashboard_layout_e_base[],audio_dashboard_layout_c_base[];
extern const char audio_dashboard_layout_e_widget[],audio_dashboard_layout_c_widget[];
extern const char audio_dashboard_layout_e_face[],audio_dashboard_layout_c_face[];
extern const char audio_dashboard_layout_e_success[],audio_dashboard_layout_c_success[];
extern const char audio_dashboard_layout_e_reset[],audio_dashboard_layout_c_reset[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char*,const char*,const char*,uint32_t,const char*,...);
extern uint32_t compressed_log_output(uint32_t,const char*,const char*,...);
extern void *audio_queue_copy_bytes(void*,const void*,uint32_t);

static void log0(uint8_t level,uint32_t line,const char *e,const char *c,uint32_t flag) {
    if(audio_log_flags()&2u) audio_log_extended(level,audio_dashboard_layout_module,audio_dashboard_layout_source,
        audio_dashboard_layout_set_function,line,e);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) (void)compressed_log_output(flag,c,c);
}
static void log1(uint8_t level,uint32_t line,const char *e,const char *c,uint32_t flag,uint32_t a) {
    if(audio_log_flags()&2u) audio_log_extended(level,audio_dashboard_layout_module,audio_dashboard_layout_source,
        audio_dashboard_layout_set_function,line,e,a);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) (void)compressed_log_output(flag,c,c,a);
}
static void log2(uint8_t level,uint32_t line,const char *e,const char *c,uint32_t flag,uint32_t a,uint32_t b) {
    if(audio_log_flags()&2u) audio_log_extended(level,audio_dashboard_layout_module,audio_dashboard_layout_source,
        audio_dashboard_layout_set_function,line,e,a,b);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) (void)compressed_log_output(flag,c,c,a,b);
}
void audio_dashboard_layout_reset(void) {
    (void)audio_queue_copy_bytes(audio_dashboard_layout_current,audio_dashboard_layout_default,128u);
    if(audio_log_flags()&2u) audio_log_extended(3u,audio_dashboard_layout_module,audio_dashboard_layout_source,
        audio_dashboard_layout_reset_function,0x8cu,audio_dashboard_layout_e_reset);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xc000000u,audio_dashboard_layout_c_reset,audio_dashboard_layout_c_reset);
}
uint32_t audio_dashboard_widget_valid(uint8_t v) {return v<5u;}
uint32_t audio_dashboard_face_slot_valid(uint8_t v) {return v<10u;}
uint32_t audio_dashboard_face_valid(const uint8_t *p) {
    if(p==0) return 0;
    if(p[0]==1u) return p[4]<2u&&audio_dashboard_face_slot_valid(p[5])&&audio_dashboard_face_slot_valid(p[6]);
    if(p[0]==3u) return p[4]<3u&&p[5]<2u&&p[6]<2u;
    if(p[0]==2u) {
        if(p[4]>=3u||p[5]>=2u||p[6]>=2u||p[7]>=4u) return 0;
        for(uint8_t i=0;i<p[7];i++) if(!audio_dashboard_face_slot_valid(p[8u+i])) return 0;
        return 1;
    }
    if(p[0]==4u) return p[4]<3u&&p[5]<4u&&p[6]<4u&&p[0x14u]<4u;
    return 0;
}
int32_t audio_dashboard_layout_set(const void *layout) {
    if(layout==0) {audio_dashboard_layout_reset();return 0;}
    uint8_t s[128];
    (void)audio_queue_copy_bytes(s,layout,128u);
    if(s[1]>5u) {
        log2(2u,0xe1u,audio_dashboard_layout_e_count,audio_dashboard_layout_c_count,0x8800000u,s[1],5u);
        s[1]=5u;
    }
    if(s[1]!=0u&&s[0]==1u) {
        log0(2u,0xe7u,audio_dashboard_layout_e_center,audio_dashboard_layout_c_center,0x8000000u);
        audio_dashboard_layout_reset();return -1;
    }
    if(s[0]>2u) {
        log1(2u,0xf0u,audio_dashboard_layout_e_base,audio_dashboard_layout_c_base,0x8400000u,s[0]);
        audio_dashboard_layout_reset();return -1;
    }
    for(uint8_t i=0;i<s[1];i++) {
        if(!audio_dashboard_widget_valid(s[2u+i])) {
            log2(2u,0xf9u,audio_dashboard_layout_e_widget,audio_dashboard_layout_c_widget,0x8800000u,i,s[2u+i]);
            audio_dashboard_layout_reset();return -1;
        }
    }
    for(uint8_t i=s[1];i<5u;i++) s[2u+i]=0;
    if(!audio_dashboard_face_valid(s+8u)) {
        log1(2u,0x107u,audio_dashboard_layout_e_face,audio_dashboard_layout_c_face,0x8400000u,s[8]);
        audio_dashboard_layout_reset();return -1;
    }
    (void)audio_queue_copy_bytes(audio_dashboard_layout_current,s,128u);
    if(audio_log_flags()&2u) audio_log_extended(3u,audio_dashboard_layout_module,audio_dashboard_layout_source,
        audio_dashboard_layout_set_function,0x110u,audio_dashboard_layout_e_success,s[0],s[1],s[8]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xcc00000u,audio_dashboard_layout_c_success,audio_dashboard_layout_c_success,
            s[0],s[1],s[8]);
    return 0;
}
