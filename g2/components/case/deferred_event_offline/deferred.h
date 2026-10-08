#ifndef CASE_DEFERRED_H
#define CASE_DEFERRED_H
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t count; uint8_t rest[16];} case_list;
typedef struct {uint8_t *head,*write,*tail,*read;case_list send_wait,receive_wait;uint32_t messages,length,item_size;int8_t rx_lock,tx_lock;uint8_t pad[2];} case_queue;
typedef struct {int32_t command;uint32_t callback,arg1,arg2;} case_deferred_message;
_Static_assert(sizeof(case_deferred_message)==16,"message ABI");
_Static_assert(offsetof(case_queue,messages)==0x38,"messages ABI");
_Static_assert(offsetof(case_queue,tx_lock)==0x45,"lock ABI");
void case_copy_from_queue(case_queue *,void *);
int32_t case_copy_to_queue(case_queue *,const void *,int32_t);
int32_t case_queue_send_isr(case_queue *,const void *,int32_t *,int32_t);
int32_t case_pend_from_isr(uint32_t,uint32_t,uint32_t,int32_t *);
#endif
