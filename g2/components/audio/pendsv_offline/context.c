#include <stdint.h>
typedef struct item{uint32_t value;struct item *next,*prev;uint8_t *owner;void *container;}item;
typedef struct list{uint32_t count;item *index;uint32_t max;item *next,*prev;}list;
/* Valid ready/canary fixture contract; stack-overflow/error branch excluded. */
void audio_context_select_ready(void){
 if(*(uint32_t*)0x20074a58u){*(uint32_t*)0x20074a44u=1;return;}
 *(uint32_t*)0x20074a44u=0;uint8_t **current=(void*)0x20074a20u;
 uint32_t *index=(void*)0x20074a5cu,*history=(void*)0x2006f348u;
 history[2*(*index)]=*(uint32_t*)(*current+0x58);
 uint32_t p=*(uint32_t*)0x20074a38u;list *ready=(void*)0x2006a49cu;
 while(!ready[p].count)p--;list *l=ready+p;l->index=l->index->next;
 if(l->index==(item*)&l->max)l->index=l->index->next;
 *current=l->index->owner;*(uint32_t*)0x20074a38u=p;
 history[2*(*index)+1]=*(uint32_t*)(*current+0x58);
 *index=(*index+1)&63u;
}
/* Functional context model, not an interrupt handler. FP register bits supplied after r4-r11. */
void audio_pendsv_integer_model(uint32_t *psp,uint32_t psplim,uint32_t exc_return,const uint32_t *r4_r11,uint32_t *restored){
 if(!(exc_return&16u)){psp-=16;for(unsigned i=0;i<16;i++)psp[i]=r4_r11[i+8];}
 uint32_t *saved=psp-10;saved[0]=psplim;saved[1]=exc_return;
 for(unsigned i=0;i<8;i++)saved[i+2]=r4_r11[i];
 **(uint32_t**)0x20074a20u=(uint32_t)saved;
 audio_context_select_ready();uint32_t *next=(void*)**(uint32_t**)0x20074a20u;
 for(unsigned i=0;i<10;i++)restored[i]=next[i];uint32_t *tail=next+10;
 if(!(next[1]&16u)){for(unsigned i=0;i<16;i++)restored[i+11]=tail[i];tail+=16;}
 restored[10]=(uint32_t)tail;
}
/* Explicit offline architectural fixture setup/readback, outside firmware execution. */
void audio_fixture_seed_psplim(uint32_t value){__asm__ volatile("msr psplim, %0"::"r"(value):"memory");}
uint32_t audio_fixture_read_psplim(void){uint32_t v;__asm__ volatile("mrs %0, psplim":"=r"(v));return v;}
