/* ui_display_thread_handler, native 0x4437e0. Product RAM cells and the
 * hardware/UI child routines retain explicit provenance and ownership. */
#include <stdint.h>
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* 0x449b3c */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* 0x44981c */
extern void task_vote_acquire_current(void),task_vote_release_current(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_display_service_init(void); /* 0x4425a6 */
extern void audio_uart_display_ring_init(void); /* 0x46d464 */
extern uint32_t audio_uart_display_ring_read(void *,void *,uint32_t); /* 0x46d9ac */
extern void audio_uart_display_connected(void); /* 0x46f32c */
extern void audio_uart_display_brightness_open(void); /* 0x46f68a */
extern void audio_uart_display_brightness_close(void); /* 0x46f6a2 */
extern void SVC_Settings_AutoBrightnessOpen(void);
extern void SVC_Settings_AutoBrightnessClose(void);
extern void SVC_Settings_SaveSettingConfigToKVCheck(void);
extern void audio_uart_display_service_prepare(void); /* 0x44227e */
extern void audio_uart_display_application_init(void); /* 0x44ff38 */
extern uint32_t audio_uart_display_audio_new(void); /* 0x45f15a */
extern void audio_uart_display_audio_release(uint32_t); /* 0x45f7be */
extern void audio_uart_display_audio_stop(uint32_t,uint32_t,uint32_t); /* 0x45faa8 */
extern void audio_uart_display_context_set(const void *); /* 0x60090 */
extern void audio_uart_display_context_commit(void); /* 0x600b4 */
extern void audio_uart_display_layer_init(void); /* 0x71164 */
extern void audio_uart_display_layer_prepare(uint32_t); /* 0x71cd6 */
extern uint32_t audio_uart_display_start(uint32_t); /* 0x471d58 */
extern void audio_uart_display_service_sync(void); /* 0x4228a */
extern void audio_uart_display_current_set(uint32_t,uint32_t); /* 0x42456 */
extern void audio_uart_display_channel_set(uint32_t); /* 0x65d7c */
extern uint32_t audio_uart_display_process(void); /* 0x64344 */
extern void audio_uart_display_sync_info(void); /* 0x71fa4 */
extern int32_t audio_uart_display_housekeep(void); /* 0x7243a */
extern void audio_uart_display_notify(uint32_t,uint32_t,const void *,uint32_t); /* 0x4228a */
extern void audio_uart_display_quiesce(void); /* 0x65b10 */
extern uint32_t audio_uart_display_upgrade(uint32_t,const void *,uint32_t); /* 0x4264e */
extern uint32_t audio_uart_display_input_check(const void *,uint32_t); /* 0x442d86 */
extern void audio_uart_task_delay(uint32_t); /* 0x454b4c */

extern uint8_t audio_uart_display_state[2]; /* RAM0x20074f2c */
extern void *audio_uart_display_driver_interface; /* RAM0x200744cc */
extern uint8_t audio_uart_display_message[12]; /* RAM0x20073fcc */
extern uint32_t audio_uart_display_wait; /* RAM0x20000654 */
extern void *g2_display_queue; /* RAM0x200744e4 */
extern void *audio_uart_display_mutex; /* RAM0x200744e8 */
extern uint8_t audio_uart_display_framebuffer[0x2800]; /* RAM0x2034dc30 */
extern void *audio_uart_display_ring; /* RAM0x20073b60 */
extern uint32_t audio_uart_display_active; /* RAM0x200744d8 */
extern uint32_t audio_uart_display_mode; /* RAM0x200744dc */
extern uint32_t audio_uart_display_background; /* RAM0x200744e0 */
extern uint32_t audio_uart_display_audio_handle; /* RAM0x200744d0 */
extern const void *audio_uart_display_context; /* DAT_004444b4 */

static const char module[]="display_thread";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char fn[]="ui_display_thread_handler";
static void log0(uint8_t level,uint32_t line,const char *e,const char *c) {
    if(audio_log_flags()&2u) audio_log_extended(level,module,source,fn,line,e);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,c,c);
}
static void log1(uint8_t level,uint32_t line,const char *e,const char *c,
                 uint32_t word) {
    if(audio_log_flags()&2u) audio_log_extended(level,module,source,fn,line,e,word);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(((uint32_t)level<<26)|0x400000u,c,c,word);
}
static void clear(void *p,uint32_t n) {
    uint8_t *b=(uint8_t *)p;
    for(uint32_t i=0u;i<n;++i) b[i]=0u;
}
static void driver_call(uint32_t offset) {
    void (*callback)(void)=*(void (**)(void))(void *)
        ((uint8_t *)audio_uart_display_driver_interface+offset);
    callback();
}
static uint32_t message_id(void) {
    return *(uint32_t *)(void *)(audio_uart_display_message+4u);
}
static uint32_t message_length(void) {
    return *(uint32_t *)(void *)(audio_uart_display_message+8u);
}
static void delay_refresh(void) {
    for(uint32_t i=0u;i<24u;++i) {
        audio_uart_display_process();
        audio_uart_task_delay(16u);
    }
}
static void shutdown_display(void) {
    static const char e[]="display thread switch display close ,release resouce...";
    static const char c[]="[display_thread]display thread switch display close ,release resouce...";
    log0(3u,0x343u,e,c);
    SVC_Settings_AutoBrightnessClose();
    driver_call(4u);driver_call(16u);
    audio_uart_display_quiesce();
    audio_uart_display_active=0u;
    audio_uart_display_mode=0u;
    audio_uart_display_background=0u;
    audio_uart_display_wait=UINT32_MAX;
    (void)audio_uart_display_start(0u);
    clear(audio_uart_display_state,2u);
    audio_uart_display_brightness_close();
    SVC_Settings_SaveSettingConfigToKVCheck();
    audio_uart_display_housekeep();
}
static void handle_start(void) {
    static const char e[]="startup applicationID = %d";
    static const char c[]="[display_thread]startup applicationID = %d";
    audio_uart_display_connected();
    audio_uart_display_state[0]=1u;
    audio_uart_display_brightness_open();
    SVC_Settings_AutoBrightnessOpen();
    driver_call(12u);driver_call(8u);
    audio_uart_display_active=0u;
    audio_uart_display_mode=0u;
    audio_uart_display_background=0u;
    log1(3u,0x2a0u,e,c,message_id());
    audio_uart_display_service_prepare();
    audio_uart_display_application_init();
    audio_uart_display_audio_handle=audio_uart_display_audio_new();
    audio_uart_display_context_set(audio_uart_display_context);
    audio_uart_display_layer_init();
    audio_uart_display_context_commit();
    audio_uart_display_notify(message_id(),2u,audio_uart_display_framebuffer,
                              message_length());
    audio_uart_display_active=message_id();
    audio_uart_display_current_set(2u,message_id());
    audio_uart_display_wait=16u;
    audio_uart_display_channel_set(audio_uart_display_active&0xffffu);
    audio_uart_display_layer_prepare(0u);
    audio_uart_display_process();
    audio_uart_display_sync_info();
    audio_uart_display_housekeep();
}
static void handle_exit(void) {
    static const char e_msg[]="received display exit message";
    static const char c_msg[]="[display_thread]received display exit message";
    static const char e_close[]="display thread close ....";
    static const char c_close[]="[display_thread]display thread close ....";
    static const char e_fore[]="foreground exist, can't close background app!!!";
    static const char c_fore[]="[display_thread]foreground exist, can't close background app!!!";
    static const char e_bg[]="exit foregroundAppID = %d";
    static const char c_bg[]="[display_thread]exit foregroundAppID = %d";
    static const char e_unknown[]="unknow display exit message,id = %d,drop it";
    static const char c_unknown[]="[display_thread]unknow display exit message,id = %d,drop it";
    log0(4u,0x2cdu,e_msg,c_msg);
    uint32_t id=message_id();
    if(audio_uart_display_background!=0u && audio_uart_display_mode==1u &&
       (id==audio_uart_display_background||id==0u)) {
        audio_uart_display_notify(audio_uart_display_background,5u,
                                  audio_uart_display_framebuffer,message_length());
        audio_uart_display_audio_stop(audio_uart_display_audio_handle,0u,
                                       audio_uart_display_background);
        log1(4u,0x2d1u,e_bg,c_bg,audio_uart_display_background);
        audio_uart_display_background=0u;
        delay_refresh();
        audio_uart_display_sync_info();
        return;
    }
    if(audio_uart_display_background!=0u && audio_uart_display_mode==1u &&
       id==audio_uart_display_active) {
        log0(3u,0x2dau,e_fore,c_fore);
        return;
    }
    log0(4u,0x2ddu,e_close,c_close);
    if((id==audio_uart_display_background||id==0u) &&
       audio_uart_display_mode==2u) {
        audio_uart_display_notify(audio_uart_display_background,5u,
                                  audio_uart_display_framebuffer,message_length());
        audio_uart_display_audio_stop(audio_uart_display_audio_handle,0u,
                                       audio_uart_display_background);
        delay_refresh();
        audio_uart_display_audio_release(audio_uart_display_audio_handle);
        audio_uart_display_audio_handle=0u;
        audio_uart_display_state[0]=2u;
        audio_uart_display_sync_info();
        shutdown_display();
        return;
    }
    if((id==audio_uart_display_active||id==0u) &&
       audio_uart_display_mode==1u && audio_uart_display_background==0u) {
        audio_uart_display_notify(audio_uart_display_active,5u,
                                  audio_uart_display_framebuffer,message_length());
        audio_uart_display_process();
        audio_uart_display_audio_release(audio_uart_display_audio_handle);
        audio_uart_display_audio_handle=0u;
        audio_uart_display_state[0]=2u;
        audio_uart_display_sync_info();
        shutdown_display();
        return;
    }
    log1(2u,0x2f1u,e_unknown,c_unknown,id);
}
static void handle_close_all(void) {
    static const char e[]="display thread switch display close all apps.";
    static const char c[]="[display_thread]display thread switch display close all apps.";
    static const char e_fg[]="close foreground appID = %d";
    static const char c_fg[]="[display_thread]close foreground appID = %d";
    static const char e_bg[]="close startup background appID = %d";
    static const char c_bg[]="[display_thread]close startup background appID = %d";
    log0(4u,0x320u,e,c);
    if(audio_uart_display_background!=0u) {
        log1(4u,0x322u,e_fg,c_fg,audio_uart_display_background);
        audio_uart_display_notify(audio_uart_display_background,5u,0,0u);
        audio_uart_display_audio_stop(audio_uart_display_audio_handle,0u,
                                       audio_uart_display_background);
        delay_refresh();
        audio_uart_display_background=0u;
    }
    if(audio_uart_display_active!=0u &&
       audio_uart_display_active!=audio_uart_display_background &&
       audio_uart_display_mode==1u) {
        log1(4u,0x32du,e_bg,c_bg,audio_uart_display_active);
        audio_uart_display_notify(audio_uart_display_active,5u,0,0u);
        audio_uart_display_active=0u;
    }
    audio_uart_display_audio_release(audio_uart_display_audio_handle);
    audio_uart_display_audio_handle=0u;
    audio_uart_display_sync_info();
    audio_uart_display_state[0]=2u;
    shutdown_display();
}
static void handle_running(void) {
    static const char e_received[]="received message queue message";
    static const char c_received[]="[display_thread]received message queue message";
    log0(4u,0x2cau,e_received,c_received);
    uint8_t type=audio_uart_display_message[0];
    if(type==5u) {handle_exit();return;}
    if(type==3u) {
        if(message_id()==audio_uart_display_active||
           message_id()==audio_uart_display_background) {
            audio_uart_display_notify(message_id(),3u,
                                      audio_uart_display_framebuffer,message_length());
            audio_uart_display_process();
        }
        return;
    }
    if(type==2u) {
        static const char e[]="display thread switch display upgrade.";
        static const char c[]="[display_thread]display thread switch display upgrade.";
        log0(3u,0x2feu,e,c);
        audio_uart_display_service_prepare();
        uint32_t changed=audio_uart_display_upgrade(message_id(),
                                    audio_uart_display_framebuffer,message_length());
        audio_uart_display_sync_info();
        if(changed==1u) delay_refresh();
        else audio_uart_display_process();
        return;
    }
    if(type==7u) {
        if(audio_uart_display_input_check(audio_uart_display_framebuffer,
                                           message_length())!=1u) {
            audio_uart_display_process();return;
        }
        static const char e[]="input event data handler, display close.";
        static const char c[]="[display_thread]input event data handler, display close.";
        log0(3u,0x30fu,e,c);
        audio_uart_display_sync_info();
        audio_uart_display_state[0]=2u;
        audio_uart_display_notify(audio_uart_display_background,5u,0,0u);
        audio_uart_display_audio_stop(audio_uart_display_audio_handle,0u,
                                       audio_uart_display_background);
        delay_refresh();
        audio_uart_display_audio_release(audio_uart_display_audio_handle);
        audio_uart_display_audio_handle=0u;
        return;
    }
    if(type==8u) {handle_close_all();return;}
}
void audio_uart_display_thread(void *argument) {
    (void)argument;
    static const char e_start[]="ui display thread startup";
    static const char c_start[]="[display_thread]ui display thread startup";
    static const char e_driver[]="display drv interface not initialized";
    static const char c_driver[]="[display_thread]display drv interface not initialized";
    static const char e_close[]="display thread switch display close .";
    static const char c_close[]="[display_thread]display thread switch display close .";
    static const char e_all[]="display thread switch display close all apps.";
    static const char c_all[]="[display_thread]display thread switch display close all apps.";
    static const char e_unknown[]="unknow display thread command";
    static const char c_unknown[]="[display_thread]unknow display thread command";
    log0(3u,0x279u,e_start,c_start);
    audio_uart_display_service_init();
    clear(audio_uart_display_state,2u);
    if(*(const uint8_t *)audio_uart_display_driver_interface!=1u) {
        log0(1u,0x27eu,e_driver,c_driver);
        return;
    }
    audio_uart_display_ring_init();
    for(;;) {
        clear(audio_uart_display_message,12u);
        int32_t received=audio_uart_queue_receive(g2_display_queue,
                          audio_uart_display_message,0u,audio_uart_display_wait);
        if(received==0) {
            clear(audio_uart_display_framebuffer,0x2800u);
            (void)audio_file_mutex_acquire(audio_uart_display_mutex,UINT32_MAX);
            (void)audio_uart_display_ring_read(audio_uart_display_ring,
                       audio_uart_display_framebuffer,message_length());
            (void)audio_file_mutex_release(audio_uart_display_mutex);
        }
        task_vote_acquire_current();
        uint8_t state=audio_uart_display_state[0];
        if(state==0u) {
            if(received==0) {
                uint8_t type=audio_uart_display_message[0];
                if(type==2u) handle_start();
                else if(type==5u||type==8u) {
                    log0(4u,type==5u?0x2b9u:0x2c0u,
                         type==5u?e_close:e_all,type==5u?c_close:c_all);
                    clear(audio_uart_display_state,2u);
                    audio_uart_display_active=0u;
                    audio_uart_display_wait=UINT32_MAX;
                }
            }
        } else if(state==1u) {
            if(received==0) handle_running();
            else {
                audio_uart_display_notify(audio_uart_display_background!=0u?
                    audio_uart_display_background:audio_uart_display_active,4u,0,0u);
                audio_uart_display_process();
            }
        } else if(state==2u) shutdown_display();
        else {
            log0(2u,0x359u,e_unknown,c_unknown);
            driver_call(4u);driver_call(16u);
            SVC_Settings_AutoBrightnessClose();
            clear(audio_uart_display_state,2u);
            audio_uart_display_active=0u;
            audio_uart_display_wait=UINT32_MAX;
        }
        task_vote_release_current();
    }
}
