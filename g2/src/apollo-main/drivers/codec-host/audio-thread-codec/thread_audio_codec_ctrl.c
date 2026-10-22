/* Audio thread init/exit and codec control handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_audio.c.
 * Native AUD_ThreadInit 0x53c344, AUD_ResourceInit 0x53c3ee,
 * AUD_CodecDmaInt 0x53c6f2, AUD_PdmCtr 0x53c7b0, AUD_CodecCtr 0x53c860,
 * AUD_CodecAudioCheck 0x53c92e, AUD_ThreadExit 0x53cdc2.
 *
 * Full versions including every log site. Each supersedes an existing
 * logger-disabled or prefix-only copy in g2/src (rtos/task-configuration/
 * config.c, apollo-common/audio-pcm-consumer, system/control-callbacks/
 * control.c, drivers/power/watchdog-callback/watchdog.c, runtime/exit-cleanup/
 * exit.c); only one implementation per address may be linked. */
#include <stdint.h>
#include <stddef.h>
#include "g2_drv_gx8002b.h" /* DRV_Gx8002_I2SInit/I2SDeinit/Reboot 0x57a65c/0x57a734/0x57a816, gx8002_i2s_rx_buffer_get 0x57a7e0 */
#include "g2_drv_pdm.h"     /* DRV_Pdm[Production]Init/Deinit 0x57b770/0x57b86c/0x57b4a8/0x57b586 */
#include "thread_audio.h"

/* CMSIS-RTOS2 osThreadAttr_t / osTimerAttr_t. */
typedef struct {
    const char *name;    /* +0x00 */
    uint32_t attr_bits;  /* +0x04 */
    void *cb_mem;        /* +0x08 */
    uint32_t cb_size;    /* +0x0c */
    void *stack_mem;     /* +0x10 */
    uint32_t stack_size; /* +0x14 */
    int32_t priority;    /* +0x18 osPriority_t */
    uint32_t tz_module;  /* +0x1c */
    uint32_t reserved;   /* +0x20 */
} aud_thread_attr_t;
_Static_assert(sizeof(aud_thread_attr_t) == 36u, "osThreadAttr_t");

typedef struct {
    const char *name;   /* +0x0 */
    uint32_t attr_bits; /* +0x4 */
    void *cb_mem;       /* +0x8 */
    uint32_t cb_size;   /* +0xc */
} aud_timer_attr_t;
_Static_assert(sizeof(aud_timer_attr_t) == 16u, "osTimerAttr_t");

extern uint8_t g2_audio_thread_cb[];             /* RAM 0x20072300, static TCB 112 B */
extern uint8_t g2_audio_thread_stack[];          /* RAM 0x20360e18, 8192 B */
extern uint8_t g2_codec_audio_check_timer_cb[];  /* RAM 0x2007372c, 44 B */

static const char thread_name[] = "audio";             /* ROM 0x78ebb4 */
static const char timer_name[] = "codec_audio_check";  /* ROM 0x78411c */

static const aud_thread_attr_t audio_thread_attr = {
    thread_name, 0u, g2_audio_thread_cb, 0x70u,
    g2_audio_thread_stack, 0x2000u, 47 /* osPriorityHigh7 */, 1u, 0u,
}; /* ROM 0x75b8c8 */

static const aud_timer_attr_t codec_check_timer_attr = {
    timer_name, 0u, g2_codec_audio_check_timer_cb, 0x2cu,
}; /* ROM 0x789a40 */

extern void audio_watchdog_tick(void *argument); /* 0x53c2a4, posts {6,0,0} */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t index); /* 0x4c9c3c, thread-manager stop ack */

extern int32_t audio_dsp_enable(void);       /* SVC_CodecDMICOpen 0x57d6b4 */
extern int32_t audio_dsp_gate(uint32_t on);  /* SVC_I2SOutputCtrl 0x57d93c */
extern int32_t SVC_PcmAppProcessData(uint8_t source, const uint8_t *buffer, uint32_t length); /* 0x57adf8 */
extern uint32_t audio_uart_command_pending(void); /* productModeGet 0x4abe60 */

extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr); /* 0x449a32 */
extern void *osTimerNew(void (*func)(void *), uint32_t type, void *argument,
                        const void *attr);                                    /* 0x4493b0 */
extern int32_t osTimerStop(void *timer);                                      /* 0x4494d8 */
extern int32_t osTimerDelete(void *timer);                                    /* 0x44953e */
extern int32_t osMessageQueueDelete(void *queue);                             /* 0x449bec */
extern int32_t osDelay(uint32_t ticks);                                       /* 0x449376 */
extern uint32_t osKernelGetTickCount(void);                                   /* 0x4490cc */

static const char module[] = "thread.audio"; /* ROM 0x7899a0 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_audio.c"; /* ROM 0x706fec */

static const char fn_init[] = "AUD_ThreadInit"; /* ROM 0x7899b0 */
static const char thread_fail[] = "osThreadNew fail"; /* ROM 0x784130 */
static const char thread_fail_s[] = "[thread.audio]osThreadNew fail"; /* ROM 0x766770 */
static const char thread_ok[] = "osThreadNew:0x%x, success"; /* ROM 0x77346c */
static const char thread_ok_s[] = "[thread.audio]osThreadNew:0x%x, success"; /* ROM 0x74fb04 */

static const char fn_resource[] = "AUD_ResourceInit"; /* ROM 0x784144 */
static const char queue_fail[] = "osMessageQueueNew fail"; /* ROM 0x77cafc */
static const char queue_fail_s[] = "[thread.audio]osMessageQueueNew fail"; /* ROM 0x74fb2c */
static const char queue_ok[] = "osMessageQueueNew:0x%x, success"; /* ROM 0x766790 */
static const char queue_ok_s[] = "[thread.audio]osMessageQueueNew:0x%x, success"; /* ROM 0x739b84 */
static const char timer_fail[] = "codec audio check timer create failed"; /* ROM 0x74fb54 */
static const char timer_fail_s[] = "[thread.audio]codec audio check timer create failed"; /* ROM 0x72ef88 */

static const char fn_dma[] = "AUD_CodecDmaInt"; /* ROM 0x7899e0 */
static const char dma_late[] = "codec i2s dma int timeout, diff = %dms"; /* ROM 0x74fb7c */
static const char dma_late_s[] = "[thread.audio]codec i2s dma int timeout, diff = %dms"; /* ROM 0x724730 */

static const char fn_pdm[] = "AUD_PdmCtr"; /* ROM 0x78c620 */
static const char pdm_ctr[] = "pdm ctr :%d"; /* ROM 0x78c62c */
static const char pdm_ctr_s[] = "[thread.audio]pdm ctr :%d"; /* ROM 0x7734a4 */

static const char fn_codec[] = "AUD_CodecCtr"; /* ROM 0x7899f0 */
static const char codec_ctr[] = "codec ctr :%d"; /* ROM 0x789a00 */
static const char codec_ctr_s[] = "[thread.audio]codec ctr :%d"; /* ROM 0x7734c0 */

static const char fn_check[] = "AUD_CodecAudioCheck"; /* ROM 0x78416c */
static const char check_fail[] = "codec audio check fail! low count: %u < %u in %ums, restart codec"; /* ROM 0x707030 */
static const char check_fail_s[] = "[thread.audio]codec audio check fail! low count: %u < %u in %ums, restart codec"; /* ROM 0x6f0628 */
static const char check_pass[] = "codec audio check pass, cnt=%u"; /* ROM 0x7667d0 */
static const char check_pass_s[] = "[thread.audio]codec audio check pass, cnt=%u"; /* ROM 0x739be4 */

static const char fn_exit[] = "AUD_ThreadExit"; /* ROM 0x789a30 */
static const char queue_deleted[] = "audio message queue deleted"; /* ROM 0x7734dc */
static const char queue_deleted_s[] = "[thread.audio]audio message queue deleted"; /* ROM 0x7451f8 */
static const char thread_exit[] = "thread audio exit"; /* ROM 0x784194 */
static const char thread_exit_s[] = "[thread.audio]thread audio exit"; /* ROM 0x766830 */

void AUD_ThreadInit(void)
{
    AUD_CONTEXT->thread = osThreadNew(AUD_ThreadHandler, NULL, &audio_thread_attr);
    if (AUD_CONTEXT->thread == NULL)
        AUD_LOG(1u, 0x04000000u, fn_init, 184u, thread_fail, thread_fail_s);
    else
        AUD_LOG(4u, 0x10400000u, fn_init, 186u, thread_ok, thread_ok_s, AUD_CONTEXT->thread);
}

/* Queue 50 x 12 bytes (heap), one-shot 2000-tick codec check timer. */
void AUD_ResourceInit(void)
{
    AUD_CONTEXT->queue = osMessageQueueNew(50u, sizeof(g2_aud_msg_t), NULL);
    if (AUD_CONTEXT->queue == NULL)
        AUD_LOG(1u, 0x04000000u, fn_resource, 194u, queue_fail, queue_fail_s);
    else
        AUD_LOG(4u, 0x10400000u, fn_resource, 196u, queue_ok, queue_ok_s, AUD_CONTEXT->queue);
    g2_audio_codec_check_timer = osTimerNew(audio_watchdog_tick, 0u /* osTimerOnce */, NULL,
                                            &codec_check_timer_attr);
    if (g2_audio_codec_check_timer == NULL)
        AUD_LOG(1u, 0x04000000u, fn_resource, 201u, timer_fail, timer_fail_s);
}

/* Type-2 handler: msg->value is the tick at which the I2S ISR posted. Blocks
 * older than 40 ticks are dropped; others go to the PCM consumers as
 * source 0 and count toward the codec watchdog. */
void AUD_CodecDmaInt(const g2_aud_msg_t *msg)
{
    uint8_t *buffer = NULL;
    uint32_t length = 0u;
    uint32_t posted = msg->value;
    uint32_t age = osKernelGetTickCount() - posted;

    if (age <= AUD_DMA_MAX_AGE) {
        gx8002_i2s_rx_buffer_get(&buffer, &length);
        g2_audio_codec_dma_count = g2_audio_codec_dma_count + 1u;
        (void)SVC_PcmAppProcessData(0u, buffer, length);
    } else {
        AUD_LOG(2u, 0x08400000u, fn_dma, 313u, dma_late, dma_late_s, age);
    }
}

/* Type-1 handler. Production PDM driver when product mode 1 and variant 0. */
void AUD_PdmCtr(const g2_aud_msg_t *msg)
{
    uint32_t value = msg->value;

    AUD_LOG(3u, 0x0c400000u, fn_pdm, 349u, pdm_ctr, pdm_ctr_s, (uint8_t)value);
    if (audio_uart_command_pending() == 1u && g2_audio_pdm_variant == 0u) {
        if ((uint8_t)value != 0u)
            DRV_PdmProductionInit();
        else
            DRV_PdmProductionDeinit();
    } else if ((uint8_t)value != 0u) {
        DRV_PdmInit();
    } else {
        DRV_PdmDeinit();
    }
}

/* Type-0 handler. Product mode 1 uses the symmetric route helper. Otherwise
 * value 2 first reboots the codec, any non-zero value opens DMIC, enables
 * codec I2S output, starts host I2S and arms the watchdog; 0 stops the
 * watchdog and host I2S and disables codec I2S output but leaves the DMIC
 * open. */
void AUD_CodecCtr(const g2_aud_msg_t *msg)
{
    uint32_t value = msg->value;

    AUD_LOG(3u, 0x0c400000u, fn_codec, 382u, codec_ctr, codec_ctr_s, (uint8_t)value);
    if (audio_uart_command_pending() == 1u) {
        aud_codec_route_control((uint8_t)value);
        return;
    }
    if ((uint8_t)value == 2u)
        DRV_Gx8002_Reboot(0u);
    if ((uint8_t)value != 0u) {
        g2_audio_codec_check_enabled = 1u;
        g2_audio_codec_dma_count = 0u;
        (void)audio_dsp_enable();
        (void)osDelay(50u);
        (void)audio_dsp_gate(1u);
        (void)osDelay(50u);
        DRV_Gx8002_I2SInit();
        audio_watchdog_start();
    } else {
        g2_audio_codec_check_enabled = 0u;
        g2_audio_codec_dma_count = 0u;
        audio_watchdog_stop();
        DRV_Gx8002_I2SDeinit();
        (void)osDelay(50u);
        (void)audio_dsp_gate(0u);
    }
}

/* Type-6 handler (one-shot timer expiry). Fewer than 20 I2S blocks in the
 * 2000-tick window posts codec control value 2 (reboot + restart). The timer
 * is re-armed only by that restart. */
void AUD_CodecAudioCheck(const g2_aud_msg_t *msg)
{
    uint32_t count;

    (void)msg;
    if (g2_audio_codec_check_enabled == 0u)
        return;
    count = g2_audio_codec_dma_count;
    g2_audio_codec_dma_count = 0u;
    if (count < AUD_CODEC_CHECK_MIN_BLOCKS) {
        AUD_LOG(2u, 0x08c00000u, fn_check, 429u, check_fail, check_fail_s, count,
                AUD_CODEC_CHECK_MIN_BLOCKS, AUD_CODEC_CHECK_TICKS);
        audio_watchdog_emit_type0(2u);
    } else {
        AUD_LOG(3u, 0x0c400000u, fn_check, 432u, check_pass, check_pass_s, count);
    }
}

/* Stop request (flag 0x800000): acknowledge to the thread manager first,
 * release timer and queue, then park forever. */
void AUD_ThreadExit(void)
{
    audio_uart_ring_sync_exit_4c9c3c(AUD_THREAD_INDEX);
    if (g2_audio_codec_check_timer != NULL) {
        (void)osTimerStop(g2_audio_codec_check_timer);
        (void)osTimerDelete(g2_audio_codec_check_timer);
        g2_audio_codec_check_timer = NULL;
    }
    if (AUD_CONTEXT->queue != NULL) {
        (void)osMessageQueueDelete(AUD_CONTEXT->queue);
        AUD_CONTEXT->queue = NULL;
        AUD_LOG(4u, 0x10000000u, fn_exit, 602u, queue_deleted, queue_deleted_s);
    }
    AUD_LOG(4u, 0x10000000u, fn_exit, 605u, thread_exit, thread_exit_s);
    for (;;)
        (void)osDelay(0xffffffffu);
}
