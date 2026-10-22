/* Audio thread handler, dispatcher, emitters and codec event callbacks, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_audio.c.
 * Native 0x53c330..0x53c343, 0x53c50a..0x53c637, 0x53c6b2..0x53c6f1,
 * 0x53c776..0x53c7af, 0x53c838..0x53c85f, 0x53c9fa..0x53ca0f,
 * 0x53ca54..0x53cd37, 0x53cd62..0x53cd8b, 0x53cdac..0x53cdc1.
 * Thread/resource init, the type 0/1/2/6 handlers and exit are in
 * thread_audio_codec_ctrl.c. */
#include <stdint.h>
#include <stddef.h>
#include "g2_drv_gx8002b.h" /* gx8002_power_state_get 0x57a656, DRV_Gx8002_I2SInit/Deinit 0x57a65c/0x57a734 */
#include "g2_drv_pdm.h"     /* drv_pdm_production_buffer_get 0x57b640, drv_pdm_buffer_get 0x57b9ba */
#include "thread_audio.h"

/* GX8002 host (service_codec_host.c). */
typedef struct {
    uint8_t id;     /* +0 event TYPE byte */
    uint8_t pad;    /* +1 */
    uint16_t value; /* +2 */
} aud_voice_event_t;
extern int32_t GX8002_GetVoiceEvent(aud_voice_event_t *event); /* 0x57da40 */
extern int32_t audio_transaction_init(void); /* gx8002_host_init 0x57ba88 */
extern void audio_transaction_cleanup(void); /* semantic_gx8002_uart_cleanup 0x57baec */
extern int32_t audio_dsp_enable(void);       /* SVC_CodecDMICOpen 0x57d6b4 */
extern int32_t audio_dsp_disable(void);      /* SVC_CodecDMICClose 0x57d794 */
extern int32_t audio_dsp_gate(uint32_t on);  /* SVC_I2SOutputCtrl 0x57d93c */


/* Services. */
extern int32_t SVC_PcmAppProcessData(uint8_t source, const uint8_t *buffer, uint32_t length); /* 0x57adf8 */
extern int32_t SVC_CodecCheckAndUpgrade(uint8_t force); /* 0x579fb8 */
extern void AUDM_Init(void);                            /* 0x54f88e */
extern void AUDM_HandlePeerSyncMsg(uint8_t msg_id);     /* 0x54f6f4 */
extern uint32_t audio_uart_command_pending(void);       /* productModeGet 0x4abe60 */
extern uint32_t audio_settings_terminal_mode(void);     /* settings_get_terminal_mode 0x46c630 */
extern uint32_t audio_wear_child_46b0ec(void);          /* SVC_Settings_InputEventCheck 0x46b0ec */
extern void service_even_ai_fn_0049832e(uint32_t event, uint32_t arg); /* 0x49832e */
extern void service_even_ai_fn_00498528(uint32_t vad);  /* 0x498528 */
extern int32_t hal_gpio_input_get_53a590(uint32_t pin, uint8_t *level); /* 0x53a590 */
extern void audio_uart_buffer_zero(void *buffer, uint32_t length, uint32_t fill); /* 0x43c0e4 */

/* Thread manager (thread_manager.c). */
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index);    /* thread_manager_sysstart_sync */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index); /* thread_manager_sysstart_sync_end */

/* CMSIS-RTOS2. */
extern uint32_t osKernelGetTickCount(void);                                   /* 0x4490cc */
extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout); /* 0x4492c2 */
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout); /* 0x449b3c */

static const char module[] = "thread.audio"; /* ROM 0x7899a0 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_audio.c"; /* ROM 0x706fec */

static const char fn_handler[] = "AUD_ThreadHandler"; /* ROM 0x784158 */
static const char notify_error[] = "Notify error!"; /* ROM 0x7899c0 */
static const char notify_error_s[] = "[thread.audio]Notify error!"; /* ROM 0x773488 */

static const char fn_processer[] = "AUD_MessageProcesser"; /* ROM 0x77cb14 */
static const char bad_id[] = "Receive error message, id = [%d]"; /* ROM 0x75b97c */
static const char bad_id_s[] = "[thread.audio]Receive error message, id = [%d]"; /* ROM 0x739bb4 */

static const char fn_int[] = "AUD_CodecIntNotify"; /* ROM 0x784180 */
static const char int_power[] = "codec is not power on, no need to recv voice event"; /* ROM 0x72efbc */
static const char int_power_s[] = "[thread.audio]codec is not power on, no need to recv voice event"; /* ROM 0x707074 */
static const char int_level[] = "codec int gpio level is not low, no need to recv voice event"; /* ROM 0x7103a4 */
static const char int_level_s[] = "[thread.audio]codec int gpio level is not low, no need to recv voice event"; /* ROM 0x6f6c9c */
static const char int_parse[] = "parse voice event failed: %d"; /* ROM 0x7667f0 */
static const char int_parse_s[] = "[thread.audio]parse voice event failed: %d"; /* ROM 0x7451cc */
static const char int_input[] = "input event check failed, no need to recv voice event"; /* ROM 0x724768 */
static const char int_input_s[] = "[thread.audio]input event check failed, no need to recv voice event"; /* ROM 0x7070b8 */
static const char int_terminal[] = "terminal mode is enabled, no need to recv voice event"; /* ROM 0x7247a0 */
static const char int_terminal_s[] = "[thread.audio]terminal mode is enabled, no need to recv voice event"; /* ROM 0x7070fc */
static const char int_vad[] = "vad report: %d"; /* ROM 0x789a10 */
static const char int_vad_s[] = "[thread.audio]vad report: %d"; /* ROM 0x766810 */

static const char fn_peer[] = "AUD_PeerSyncMsg"; /* ROM 0x789a20 */
static const char peer_null[] = "invalid peer sync msg"; /* ROM 0x77cb2c */
static const char peer_null_s[] = "[thread.audio]invalid peer sync msg"; /* ROM 0x75b9a0 */
static const char peer_msg[] = "processing peer sync msg in audio thread: msg_id=%d"; /* ROM 0x72eff0 */
static const char peer_msg_s[] = "[thread.audio]processing peer sync msg in audio thread: msg_id=%d"; /* ROM 0x707140 */

/* 0x53c330: thread-manager start barrier for slot 3 (waits for system start). */
void aud_pdm_counter_reset_callback(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(AUD_THREAD_INDEX);
}

/* 0x53c33a: thread-manager "start done" for slot 3. */
void aud_codec_counter_reset_callback(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(AUD_THREAD_INDEX);
}

/* 0x53c50a */
void aud_codec_dfu_check(void)
{
    (void)SVC_CodecCheckAndUpgrade(0u);
}

/* 0x53c514: product mode 1 checks/upgrades the codec firmware, every other
 * mode starts the audio manager instead. */
void aud_codec_mode_init(void)
{
    if (audio_uart_command_pending() == 1u)
        aud_codec_dfu_check();
    else
        AUDM_Init();
}

/* 0x53c52c: thread entry. A zeroed 12-byte local message is unused. Any
 * wait result of 0 or an osError code is logged and the wait repeats. */
void AUD_ThreadHandler(void *argument)
{
    uint32_t flags;

    (void)argument;
    aud_pdm_counter_reset_callback();
    aud_codec_mode_init();
    AUD_ResourceInit();
    aud_codec_counter_reset_callback();
    for (;;) {
        flags = osThreadFlagsWait(0x00ffffffu, 0u, 0xffffffffu);
        if (flags != 0u && flags < 0x80000000u) {
            aud_thread_flag_dispatch(flags);
            continue;
        }
        AUD_LOG(1u, 0x04000000u, fn_handler, 252u, notify_error, notify_error_s);
    }
}

/* 0x53c5ac: first row whose type matches and whose handler is set wins. */
void AUD_MessageProcesser(const g2_aud_msg_t *msg)
{
    uint32_t type = msg->type;
    uint32_t row;

    for (row = 0u; row < 8u; row++) {
        if ((uint16_t)type == g2_audio_message_table[row].type &&
            g2_audio_message_table[row].handler != NULL) {
            g2_audio_message_table[row].handler(msg);
            return;
        }
    }
    if (row == 8u)
        AUD_LOG(1u, 0x04400000u, fn_processer, 269u, bad_id, bad_id_s, (uint16_t)type);
}

/* 0x53c6b2: called from the I2S ISR (0x57a4d8) on RX DMA completion. */
void aud_send_codec_dma_message(void)
{
    g2_aud_msg_t msg = {0u, 0u, 0u};

    msg.type = 2u;
    msg.value = osKernelGetTickCount();
    stock_audio_submit(&msg);
}

/* 0x53c6d2: type-3 notifier called from PDM0_IRQHandler, despite its TSV name. */
void aud_send_codec_control_message(void)
{
    g2_aud_msg_t msg = {0u, 0u, 0u};

    msg.type = 3u;
    msg.value = osKernelGetTickCount();
    stock_audio_submit(&msg);
}

/* 0x53c776: type-3 handler; forwards the current PDM DMA block as source 1.
 * Production driver only when product mode 1 and variant byte 0. */
void aud_pdm_counter_sample(const g2_aud_msg_t *msg)
{
    uint8_t *buffer = NULL;
    uint32_t length = 0u;

    (void)msg;
    if (audio_uart_command_pending() == 1u && g2_audio_pdm_variant == 0u)
        drv_pdm_production_buffer_get(&buffer, &length);
    else
        drv_pdm_buffer_get(&buffer, &length);
    (void)SVC_PcmAppProcessData(1u, buffer, length);
}

/* 0x53c838: product-mode-1 codec route, DMIC + codec I2S output + host I2S. */
void aud_codec_route_control(uint8_t on)
{
    if (on != 0u) {
        (void)audio_dsp_enable();
        (void)audio_dsp_gate(1u);
        DRV_Gx8002_I2SInit();
    } else {
        (void)audio_dsp_disable();
        (void)audio_dsp_gate(0u);
        DRV_Gx8002_I2SDeinit();
    }
}

/* 0x53c9fa: type-4 handler. */
void aud_codec_check_trigger(const g2_aud_msg_t *msg)
{
    (void)SVC_CodecCheckAndUpgrade(msg->value != 0u ? 1u : 0u);
}

/* 0x53ca54 */
void aud_send_message_type4(uint8_t value)
{
    g2_aud_msg_t msg = {0u, 0u, 0u};

    msg.type = 4u;
    msg.value = value;
    stock_audio_submit(&msg);
}

/* 0x53ca72: type-5 handler for the GX8002 notify interrupt. The codec drives
 * Apollo GPIO 29 low before sending an asynchronous event frame. The UART is
 * opened here and closed only after a successful read. Event 0x0c (wake word)
 * reaches the Even AI service; event 0x0d is a VAD report (1 voice, 0 quiet). */
void AUD_CodecIntNotify(const g2_aud_msg_t *msg)
{
    uint8_t level;
    aud_voice_event_t event;
    int32_t status;

    (void)msg;
    if (gx8002_power_state_get() == 0u) {
        AUD_LOG(2u, 0x08000000u, fn_int, 470u, int_power, int_power_s);
        return;
    }
    /* level is left unwritten (stale stack byte in stock) if the read fails. */
    (void)hal_gpio_input_get_53a590(AUD_CODEC_INT_PIN, &level);
    if (level != 0u) {
        AUD_LOG(2u, 0x08000000u, fn_int, 477u, int_level, int_level_s);
        return;
    }
    (void)audio_transaction_init();
    audio_uart_buffer_zero(&event, sizeof event, 0u);
    status = GX8002_GetVoiceEvent(&event);
    if (status != 0) {
        AUD_LOG(1u, 0x04400000u, fn_int, 487u, int_parse, int_parse_s, status);
        return;
    }
    audio_transaction_cleanup();
    if (audio_wear_child_46b0ec() == 0u) {
        AUD_LOG(2u, 0x08000000u, fn_int, 494u, int_input, int_input_s);
        return;
    }
    if (audio_settings_terminal_mode() != 0u) {
        AUD_LOG(3u, 0x0c000000u, fn_int, 499u, int_terminal, int_terminal_s);
        return;
    }
    if (event.id == 0x0cu) {
        service_even_ai_fn_0049832e(1u, 0u);
    } else if (event.id == 0x0du) {
        if (event.value == 1u)
            service_even_ai_fn_00498528(1u);
        else if (event.value == 0u)
            service_even_ai_fn_00498528(2u);
        AUD_LOG(2u, 0x08400000u, fn_int, 516u, int_vad, int_vad_s, event.value);
    }
}

/* 0x53cc8c: posts {5,0,0}; called by the drv_gx8002b codec-INT handler. */
void aud_send_message_type5(void)
{
    g2_aud_msg_t msg = {0u, 0u, 0u};

    msg.type = 5u;
    stock_audio_submit(&msg);
}

/* 0x53cca6: type-8 handler. */
void AUD_PeerSyncMsg(const g2_aud_msg_t *msg)
{
    uint32_t value;

    if (msg == NULL) {
        AUD_LOG(1u, 0x04000000u, fn_peer, 539u, peer_null, peer_null_s);
        return;
    }
    value = msg->value;
    AUD_LOG(4u, 0x10400000u, fn_peer, 546u, peer_msg, peer_msg_s, (uint8_t)value);
    AUDM_HandlePeerSyncMsg((uint8_t)value);
}

/* 0x53cd62: drains the queue without waiting. */
void aud_message_loop(void)
{
    g2_aud_msg_t msg = {0u, 0u, 0u};

    while (osMessageQueueGet(AUD_CONTEXT->queue, &msg, NULL, 0u) == 0)
        AUD_MessageProcesser(&msg);
}

/* 0x53cdac: messages first, then the stop request (does not return). */
void aud_thread_flag_dispatch(uint32_t flags)
{
    if (flags & AUD_FLAG_MESSAGE)
        aud_message_loop();
    if (flags & AUD_FLAG_EXIT)
        AUD_ThreadExit();
}
