/* Independent selected event-set body; actual scheduler/list peers execute. */
#include <stdint.h>
#include <stddef.h>
typedef struct item {uint32_t value;struct item *next,*prev;void *owner,*container;} item;
typedef struct {uint32_t bits,count;item *index;uint32_t sentinel_value;item *next,*prev;} event_group;
extern void case_suspend_scheduler(void),case_resume_scheduler(void);
extern void case_unblock_waiter(item *,uint32_t);
uint32_t case_event_set_waiters(event_group *e,uint32_t flags){
 uint32_t clear=0;case_suspend_scheduler();e->bits|=flags;
 item *sentinel=(item *)&e->sentinel_value;
 for(item *p=e->next;p!=sentinel;){item *next=p->next;uint32_t requested=p->value&0xffffffu;
  int match=(p->value&0x04000000u)?((requested&~e->bits)==0):((requested&e->bits)!=0);
  if(match){if(p->value&0x01000000u)clear|=requested;case_unblock_waiter(p,e->bits|0x02000000u);}p=next;
 }
 e->bits&=~clear;case_resume_scheduler();return e->bits;
}
