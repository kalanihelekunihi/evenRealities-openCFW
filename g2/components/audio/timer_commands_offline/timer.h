#ifndef OPENCFW_AUDIO_TIMER_OFFLINE_H
#define OPENCFW_AUDIO_TIMER_OFFLINE_H
#include <stdint.h>
typedef struct {uint32_t value,next,previous,owner,container;} audio_timer_list_item;
typedef struct {uint32_t name;audio_timer_list_item item;uint32_t period,id,callback,opaque_word;uint8_t status,padding[3];} audio_timer_prefix;
typedef struct {int32_t command;uint32_t value;audio_timer_prefix *timer;uint32_t union_padding;} audio_timer_message;
enum {AUDIO_TIMER_ACTIVE=1,AUDIO_TIMER_STATIC=2,AUDIO_TIMER_AUTORELOAD=4,AUDIO_TIMER_STOP=3,AUDIO_TIMER_DELETE=5};
_Static_assert(sizeof(audio_timer_prefix)==44,"ARM32 timer prefix");
_Static_assert(sizeof(audio_timer_message)==16,"ARM32 daemon message");
void audio_timer_drain_stop_delete(void);
#endif
