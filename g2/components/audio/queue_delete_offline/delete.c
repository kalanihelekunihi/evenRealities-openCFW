/* Selected coherent allocated queue + heap_4 free; ARM32 offline reconstruction. */
#include <stdint.h>
typedef struct block {struct block *next;uint32_t size;} block;
extern int32_t audio_irq_context(void);
extern void audio_suspend(void),audio_resume(void);
void audio_heap_free(void *p){
 if(!p)return;block *b=(block*)((uint8_t*)p-8);
 /* Contract: allocated bit set, next=NULL, ordered coherent free list. */
 b->size &= 0x7fffffffu;audio_suspend();*(uint32_t*)0x20074660u+=b->size;
 block *prev=(block*)0x20074158u;
 while(prev->next<b)prev=prev->next;
 if((uint8_t*)prev+prev->size==(uint8_t*)b){prev->size+=b->size;b=prev;}
 if((uint8_t*)b+b->size==(uint8_t*)prev->next){
  if(prev->next!=*(block**)0x2007465cu){b->size+=prev->next->size;b->next=prev->next->next;}
  else b->next=*(block**)0x2007465cu;
 }else b->next=prev->next;
 if(prev!=b)prev->next=b;
 ++*(uint32_t*)0x2007466cu;audio_resume();
}
int32_t audio_queue_delete(void *q){
 if(audio_irq_context())return -6;if(!q)return -4;
 if(!((uint8_t*)q)[0x46])audio_heap_free(q);
 return 0;
}
