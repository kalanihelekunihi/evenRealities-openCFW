#include <stdint.h>
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void *volatile r1_r_size_kv_handle;
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_ble_thread_message_encode(uint32_t,uint32_t,uint32_t,const void *);
/* Native push{r3,lr} supplies the existing word. Cached read failure leaves the
 * byte intact, and pop restores that same word into r3. No default is invented. */
__attribute__((used,noinline)) static uint32_t recovery_needed_kernel(volatile uint8_t *frame)
{
 (void)r1_kv_class_read(r1_r_size_kv_handle,(void *)(uintptr_t)frame,1);
 uint32_t value=frame[0];return value==0 || value==255;
}
__attribute__((naked,noinline)) uint32_t r1_nv_recovery_needed_query_boundary(void)
{
 __asm__ volatile("push {r3,lr}\nmov r0,sp\nbl recovery_needed_kernel\npop {r3,pc}");
}
__attribute__((used,noinline)) static uint32_t timeout_byte_kernel(uint32_t argument,volatile uint8_t *frame)
{
 frame[0]=(uint8_t)argument;
 uint32_t handle=r1_phone_connection_handle_get();
 return r1_ble_thread_message_encode(handle,8,1,(const void *)(uintptr_t)frame);
}
/* Callback has void public semantics; the native lower return word remains in
 * r0. The saved word's other three bytes and the restored r3 remain observable. */
__attribute__((naked,noinline)) void r1_protocol_time_timeout_callback(uint32_t argument __attribute__((unused)))
{
 __asm__ volatile("push {r3,lr}\nmov r1,sp\nbl timeout_byte_kernel\npop {r3,pc}");
}
