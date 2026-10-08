/* Independent ARM32 reconstruction. Valid coherent queues required.
 * Task removal and mutex disinherit are unresolved original peer boundaries. */
#include "deferred.h"
extern uint32_t case_mask_save(void);
extern void case_mask_restore(uint32_t);
extern int32_t case_remove_waiter(case_list *);
extern int32_t case_disinherit(void *);
static void copy_bytes(uint8_t *d,const uint8_t *s,uint32_t n){while(n--)*d++=*s++;}
static void assertion(void){__asm volatile("cpsid i");for(;;){}}
int32_t case_copy_to_queue(case_queue *q,const void *item,int32_t pos){
 uint32_t count=q->messages;int32_t result=0;
 if(q->item_size==0){if(!q->head){result=case_disinherit(q->tail);q->tail=0;}}
 else if(pos==0){copy_bytes(q->write,item,q->item_size);q->write+=q->item_size;if(q->write>=q->tail)q->write=q->head;}
 else{copy_bytes(q->read,item,q->item_size);q->read-=q->item_size;if(q->read<q->head)q->read=q->tail-q->item_size;if(pos==2 && count)count--;}
 q->messages=count+1;return result;
}
int32_t case_queue_send_isr(case_queue *q,const void *item,int32_t *yield,int32_t pos){
 if(!q || (!item && q->item_size) || (pos==2 && q->length!=1))assertion();
 uint32_t saved=case_mask_save();int32_t result=0;
 if(q->messages<q->length || pos==2){int8_t lock=q->tx_lock;(void)case_copy_to_queue(q,item,pos);
  if(lock==-1){if(q->receive_wait.count && case_remove_waiter(&q->receive_wait) && yield)*yield=1;}
  else q->tx_lock=(int8_t)(lock+1);result=1;
 }
 case_mask_restore(saved);return result;
}
int32_t case_pend_from_isr(uint32_t callback,uint32_t arg1,uint32_t arg2,int32_t *yield){
 case_deferred_message message={-2,callback,arg1,arg2};
 return case_queue_send_isr(*(case_queue **)0x20000164u,&message,yield,0);
}
int32_t xEventGroupSetBitsFromISR(void *event,uint32_t flags,int32_t *yield){return case_pend_from_isr(0x0800bf8du,(uint32_t)event,flags,yield);}

void case_copy_from_queue(case_queue *q,void *out){if(q->item_size){q->read+=q->item_size;if(q->read>=q->tail)q->read=q->head;copy_bytes(out,q->read,q->item_size);}}
