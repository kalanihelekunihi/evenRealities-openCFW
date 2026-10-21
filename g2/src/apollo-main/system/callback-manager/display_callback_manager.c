/* Native callback manager 0x5100a0/0x510218/0x510240. */
#include <stdint.h>
struct callback_node {void *callback;struct callback_node *next;};
struct callback_manager {struct callback_node *head;uint8_t count;uint8_t pad[3];const char *name;};
_Static_assert(sizeof(struct callback_node)==8u,"callback node ABI");
_Static_assert(sizeof(struct callback_manager)==12u,"callback manager ABI");
extern void *codec_allocate(uint32_t); /* selected native 0x474cd2 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="callback.mgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\callback_manager.c";
static const char create_function[]="CALLBACK_MGR_CreateNode";
static const char register_function[]="CALLBACK_MGR_Register";
static const char alloc_fail[]="Failed to allocate memory for callback node";
static const char alloc_fail_short[]="[callback.mgr]Failed to allocate memory for callback node";
static const char bad_mgr[]="Invalid manager pointer";
static const char bad_mgr_short[]="[callback.mgr]Invalid manager pointer";
static const char bad_cb[]="Invalid callback function";
static const char bad_cb_short[]="[callback.mgr]Invalid callback function";
static const char duplicate[]="[%s] Callback already registered";
static const char duplicate_short[]="[callback.mgr][%s] Callback already registered";
static const char node_fail[]="[%s] Failed to create callback node";
static const char node_fail_short[]="[callback.mgr][%s] Failed to create callback node";
static const char success[]="[%s] Callback registered successfully, total callbacks: %d";
static const char success_short[]="[callback.mgr][%s] Callback registered successfully, total callbacks: %d";
static const char init_function[]="CALLBACK_MGR_Init";
static const char init_message[]="[%s] Callback manager initialized";
static const char init_message_short[]="[callback.mgr][%s] Callback manager initialized";
static void log_simple(uint8_t level,uint32_t line,uint32_t code,const char *function,
                       const char *extended,const char *short_text) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,path,function,line,extended);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(code,short_text,short_text);
}
static struct callback_node *create_node(void *callback) {
    struct callback_node *node=(struct callback_node *)codec_allocate(8u);
    if(node==0) {
        log_simple(1u,27u,0x04000000u,create_function,alloc_fail,alloc_fail_short);
        return 0;
    }
    node->callback=callback;
    node->next=0;
    return node;
}
static uint32_t is_registered(const struct callback_manager *manager,void *callback) {
    if(manager!=0&&callback!=0)
        for(const struct callback_node *node=manager->head;node!=0;node=node->next)
            if(node->callback==callback) return 1u;
    return 0u;
}
uint32_t audio_callback_mgr_init(void *manager_storage,const char *name) {
    struct callback_manager *manager=(struct callback_manager *)manager_storage;
    if(manager==0) {
        log_simple(1u,47u,0x04000000u,init_function,bad_mgr,bad_mgr_short);
        return 0u;
    }
    manager->head=0;
    manager->count=0;
    manager->name=name;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,init_function,55u,init_message,manager->name);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,init_message_short,init_message_short,manager->name);
    return 1u;
}
uint32_t audio_callback_mgr_register(void *manager_storage,void *callback) {
    struct callback_manager *manager=(struct callback_manager *)manager_storage;
    if(manager==0) {
        log_simple(1u,100u,0x04000000u,register_function,bad_mgr,bad_mgr_short);
        return 0u;
    }
    if(callback==0) {
        log_simple(1u,105u,0x04000000u,register_function,bad_cb,bad_cb_short);
        return 0u;
    }
    if(is_registered(manager,callback)!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,register_function,111u,duplicate,manager->name);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,duplicate_short,duplicate_short,manager->name);
        return 1u;
    }
    struct callback_node *node=create_node(callback);
    if(node==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,register_function,118u,node_fail,manager->name);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,node_fail_short,node_fail_short,manager->name);
        return 0u;
    }
    node->next=manager->head;
    manager->head=node;
    manager->count=(uint8_t)(manager->count+1u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,register_function,128u,success,manager->name,manager->count);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,success_short,success_short,manager->name,manager->count);
    return 1u;
}
