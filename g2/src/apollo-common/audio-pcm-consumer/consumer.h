/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AUDIO_PCM_CONSUMER_H
#define OPENCFW_AUDIO_PCM_CONSUMER_H
#include <stdint.h>
typedef struct { uint32_t type, reserved, tick; } opencfw_audio_message_t;
/* New observation seams: dispositions mark unexecuted provider boundaries. */
enum { AUDIO_RETURN=0, AUDIO_CALLBACK=1, AUDIO_DSP=2, AUDIO_STALE_LOG=3,
       AUDIO_WAKE=4, AUDIO_QUEUE_LOG=5 };
typedef struct { uint32_t disposition, mode, pcm, length, callback, age; } opencfw_audio_cut_t;
uint32_t opencfw_audio_tick(void);
uint32_t opencfw_audio_irq_context(void);
uint32_t opencfw_audio_scheduler_state(void);
void opencfw_pcm_dispatch_prefix(uint32_t mode,uint32_t pcm,uint32_t length,opencfw_audio_cut_t *cut);
void opencfw_audio_consume_prefix(const opencfw_audio_message_t *message,opencfw_audio_cut_t *cut);
void opencfw_audio_notify_prefix(opencfw_audio_cut_t *cut);
int32_t opencfw_audio_queue_put_isr(void *queue,const void *message);
int32_t opencfw_audio_queue_get_task_nowait(void *queue,void *message);
#endif
