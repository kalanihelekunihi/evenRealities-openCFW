/* Native CALLBACK_MGR_Unregister 0x5103c4. */
#include <stdint.h>
extern void audio_callback_mgr_delete_node(void *); /* 0x5100fc */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="callback.mgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\callback_manager.c";
static const char function[]="CALLBACK_MGR_Unregister";
static const char bad_manager[]="Invalid manager pointer";
static const char bad_manager_short[]="[callback.mgr]Invalid manager pointer";
static const char bad_callback[]="Invalid callback function";
static const char bad_callback_short[]="[callback.mgr]Invalid callback function";
static const char empty[]="[%s] No callbacks registered";
static const char empty_short[]="[callback.mgr][%s] No callbacks registered";
static const char success[]="[%s] Callback unregistered successfully, total callbacks: %d";
static const char success_short[]="[callback.mgr][%s] Callback unregistered successfully, total callbacks: %d";
static const char absent[]="[%s] Callback not found";
static const char absent_short[]="[callback.mgr][%s] Callback not found";
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_word(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
static void log_plain(uint8_t level,uint32_t line,uint32_t code,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(code,short_message,short_message);
}
static void log_named(uint8_t level,uint32_t line,uint32_t code,const char *message,
                      const char *short_message,const char *name) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,path,function,line,message,name);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(code,short_message,short_message,name);
}
/* Stock 0x5103C4 (CALLBACK_MGR_Unregister) */
void audio_callback_mgr_unregister(void *manager_storage,void *callback) {
    uint8_t *manager=(uint8_t *)manager_storage;
    if(manager==0) {log_plain(1u,135u,0x04000000u,bad_manager,bad_manager_short);return;}
    if(callback==0) {log_plain(1u,140u,0x04000000u,bad_callback,bad_callback_short);return;}
    const char *name=(const char *)(uintptr_t)word(manager+8u);
    uint32_t node=word(manager);
    if(node==0u) {log_named(2u,145u,0x08400000u,empty,empty_short,name);return;}
    uint32_t previous=0u;
    while(node!=0u) {
        uint8_t *item=(uint8_t *)(uintptr_t)node;
        uint32_t next=word(item+4u);
        if(word(item)==(uint32_t)(uintptr_t)callback) {
            if(previous==0u) put_word(manager,next);
            else put_word((uint8_t *)(uintptr_t)previous+4u,next);
            audio_callback_mgr_delete_node(item);
            manager[4u]=(uint8_t)(manager[4u]-1u);
            uint8_t count=manager[4u];
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(4u,module,path,function,169u,success,name,count);
            if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x10800000u,success_short,success_short,name,count);
            return;
        }
        previous=node;
        node=next;
    }
    log_named(2u,176u,0x08400000u,absent,absent_short,name);
}
