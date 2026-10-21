/* Independent target a3b0/a444 reconstruction; offline SRAM ABI. */
#include "callbacks.h"
#include <stddef.h>
_Static_assert(offsetof(touch_pm_callback,params)==12,"params");
_Static_assert(offsetof(touch_pm_callback,order)==24,"order");
#define ROOT ((touch_pm_callback * volatile *)0x20000f34u)
#define FAILED ((touch_pm_callback * volatile *)0x20000f28u)
#define LAST (*(touch_pm_callback * volatile *)0x20000f24u)
#define FAIL 0x4200ffu
bool touch_pm_register(touch_pm_callback *h)
{
 if (!h || !h->params || !h->callback) return false;
 uint32_t t=h->type; touch_pm_callback *cur=ROOT[t],*pos=cur;
 if (!cur) {ROOT[t]=h;h->prev=NULL;h->next=NULL;return true;}
 while(cur->next && cur!=h) {cur=cur->next;if(cur->order<=h->order)pos=cur;}
 if(cur==h)return false;
 if(!pos->prev && h->order<pos->order) {
  h->next=pos;h->prev=NULL;pos->prev=h;ROOT[t]=h;
 } else {
  h->next=pos->next;h->prev=pos;if(h->next)h->next->prev=h;pos->next=h;
 }
 return true;
}
uint32_t touch_pm_execute(uint32_t type,uint32_t mode)
{
 touch_pm_callback *cur=ROOT[type];uint32_t result=0;touch_pm_params params;
 if(mode==1 || mode==4) {
  while(cur && (result!=FAIL || mode!=1)) {
   if(!(cur->skip&mode)) {params=*cur->params;result=cur->callback(&params,mode);LAST=cur;}
   cur=cur->next;
  }
  if(mode==1)FAILED[type]=(result==FAIL)?LAST:NULL;
 } else {
  if(mode==2) {cur=LAST;if(cur)cur=cur->prev;}
  else {while(cur->next)cur=cur->next;}
  while(cur) {
   if(!(cur->skip&mode)) {params=*cur->params;result=cur->callback(&params,mode);}
   cur=cur->prev;
  }
 }
 return result;
}

extern uint32_t Cy_SysLib_EnterCriticalSection(void);
extern void Cy_SysLib_ExitCriticalSection(uint32_t);
static void deep_sleep_no_callbacks(void)
{
 *(volatile uint32_t *)0x40030004u=*(volatile const uint16_t *)0x0ffff152u;
 *(volatile uint32_t *)0xe000ed10u|=4u;
 __asm volatile("wfi");
}
uint32_t touch_pm_deep_sleep(void)
{
 uint32_t result=0,saved;
 if(ROOT[1])result=touch_pm_execute(1,1);
 if(result==0) {
  saved=Cy_SysLib_EnterCriticalSection();
  if(ROOT[1])(void)touch_pm_execute(1,4);
  deep_sleep_no_callbacks();
  Cy_SysLib_ExitCriticalSection(saved);
 }
 if(ROOT[1])(void)touch_pm_execute(1,result==0?8:2);
 return result;
}
