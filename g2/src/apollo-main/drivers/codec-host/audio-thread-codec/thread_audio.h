/* Audio thread (stock D:\01_workspace\s200_ap510b_iar_git\platform\threads\
 * thread_audio.c, module tag "thread.audio"), native 0x53c2a4..0x53ce72,
 * literal pools 0x53cd8c..0x53cda9 and 0x53ce74..0x53cf77.
 *
 * One CMSIS thread ("audio", priority 47) owns a 50 x 12-byte message queue.
 * Producers post with AUD_SendMessage (0x53c638), which sets thread flag
 * 0x400000; flag 0x800000 is the thread-manager stop request. Messages are
 * dispatched through the 8-row table at RAM 0x20003fbc by low 16 bits of
 * the type:
 *   0 AUD_CodecCtr        codec power / DMIC / I2S route   (value = on/off/2)
 *   1 AUD_PdmCtr          PDM microphone path               (value = on/off)
 *   2 AUD_CodecDmaInt     I2S RX DMA block ready            (value = tick)
 *   3 aud_pdm_counter_sample  PDM DMA block ready
 *   4 aud_codec_check_trigger codec firmware check/upgrade  (value = force)
 *   5 AUD_CodecIntNotify  codec INT pin (voice event pending)
 *   6 AUD_CodecAudioCheck 2000-tick codec watchdog expiry
 *   8 AUD_PeerSyncMsg     peer (other temple) audio sync    (value = msg id) */
#ifndef G2_THREAD_AUDIO_LOCAL_H
#define G2_THREAD_AUDIO_LOCAL_H

#include <stdint.h>

typedef struct {
    uint32_t type;  /* +0 dispatch key (low 16 bits) */
    uint32_t mode;  /* +4 1 for the type 0/1/8 emitters, else 0 */
    uint32_t value; /* +8 control byte or tick count */
} g2_aud_msg_t;
_Static_assert(sizeof(g2_aud_msg_t) == 12u, "stock 12-byte audio message");

typedef void (*g2_aud_handler_t)(const g2_aud_msg_t *msg);

typedef struct {
    uint16_t type;            /* +0 */
    uint16_t pad;             /* +2 */
    g2_aud_handler_t handler; /* +4 */
} g2_aud_handler_row_t;
_Static_assert(sizeof(g2_aud_handler_row_t) == 8u, "stock dispatch row stride");

/* Head of the thread context at RAM 0x20003f98. */
typedef struct {
    void (*init)(void);      /* +0x00 AUD_ThreadInit */
    void (*terminate)(void); /* +0x04 aud_thread_terminate */
    void *thread;            /* +0x08 osThreadId_t */
    void *queue;             /* +0x0c osMessageQueueId_t */
} g2_audio_thread_context_t;

extern uint8_t g2_audio_dispatch_state[];               /* RAM 0x20003f98 */
#define AUD_CONTEXT ((g2_audio_thread_context_t *)(void *)g2_audio_dispatch_state)
extern g2_aud_handler_row_t g2_audio_message_table[8];  /* RAM 0x20003fbc */
extern void *g2_audio_codec_check_timer;                /* RAM 0x20074a98 */
extern volatile uint32_t g2_audio_codec_dma_count;      /* RAM 0x20074a9c, I2S blocks since last check */
extern volatile uint8_t g2_audio_codec_check_enabled;   /* RAM 0x2007502e */
extern volatile uint8_t g2_audio_pdm_variant;           /* RAM 0x20075019, 0 = production PDM driver */

#define AUD_FLAG_MESSAGE 0x400000u
#define AUD_FLAG_EXIT 0x800000u
#define AUD_THREAD_INDEX 3u           /* thread-manager slot (stop ack event 0x08) */
#define AUD_CODEC_CHECK_TICKS 2000u
#define AUD_CODEC_CHECK_MIN_BLOCKS 20u
#define AUD_DMA_MAX_AGE 40u           /* ticks between ISR post and consumption */
#define AUD_CODEC_INT_PIN 29u         /* GX8002 notify GPIO, active low */

/* Assigned stock functions in this directory. */
void AUD_ThreadInit(void);
void AUD_ResourceInit(void);
void aud_pdm_counter_reset_callback(void);
void aud_codec_counter_reset_callback(void);
void aud_codec_dfu_check(void);
void aud_codec_mode_init(void);
void AUD_ThreadHandler(void *argument);
void AUD_MessageProcesser(const g2_aud_msg_t *msg);
void aud_send_codec_dma_message(void);
void aud_send_codec_control_message(void);
void AUD_CodecDmaInt(const g2_aud_msg_t *msg);
void aud_pdm_counter_sample(const g2_aud_msg_t *msg);
void AUD_PdmCtr(const g2_aud_msg_t *msg);
void aud_codec_route_control(uint8_t on);
void AUD_CodecCtr(const g2_aud_msg_t *msg);
void AUD_CodecAudioCheck(const g2_aud_msg_t *msg);
void aud_codec_check_trigger(const g2_aud_msg_t *msg);
void aud_send_message_type4(uint8_t value);
void AUD_CodecIntNotify(const g2_aud_msg_t *msg);
void aud_send_message_type5(void);
void AUD_PeerSyncMsg(const g2_aud_msg_t *msg);
void aud_message_loop(void);
void aud_thread_flag_dispatch(uint32_t flags);
void AUD_ThreadExit(void);

/* Stock thread_audio.c functions reconstructed elsewhere in g2/src. */
extern void stock_audio_submit(const void *msg);       /* AUD_SendMessage 0x53c638 */
extern void audio_watchdog_start(void);                /* AUD_CodecAudioCheckTimerStart 0x53c2be */
extern void audio_watchdog_stop(void);                 /* aud_codec_audio_check_timer_stop 0x53c31c */
extern void audio_watchdog_emit_type0(uint32_t value); /* aud_send_message_type0 0x53ca10 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

/* Stock LOG expansion; uses the including file's `module` and `file`. */
#define AUD_LOG(level, mask, function, line, format, simple, ...)               \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

#endif
