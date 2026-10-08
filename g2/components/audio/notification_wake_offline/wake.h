#ifndef AUDIO_WAKE_H
#define AUDIO_WAKE_H
#include <stdint.h>
#include <stddef.h>
typedef struct audio_item {uint32_t value;struct audio_item *next,*previous;void *owner,*container;} audio_item;
typedef struct {uint32_t count;audio_item *index;uint32_t end_value;audio_item *next,*previous;} audio_list;
typedef struct {uint32_t first;audio_item state_item,event_item;uint32_t priority;uint8_t opaque[56];uint32_t notification;uint8_t notification_state;} audio_tcb_prefix;
_Static_assert(offsetof(audio_tcb_prefix,notification)==0x68,"value ABI");
_Static_assert(offsetof(audio_tcb_prefix,notification_state)==0x6c,"state ABI");
int32_t audio_notify_isr(void *,uint32_t,uint32_t,uint32_t,uint32_t *,int32_t *);
#endif
