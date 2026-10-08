/* SPDX-License-Identifier: MIT
 * Locked416200,417fe4,417f0a,418ae8. Algorithm corroborated by pinned
 * CMSIS-FreeRTOS and FreeRTOS-Kernel; addresses/layout derived from bytes.
 */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_context_guard(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_boot_list_unlink(uint32_t *);
extern void opencfw_boot_next_unblock_refresh(void);
extern void opencfw_bl_rtos_free(void *);
extern uint32_t opencfw_bl_mask_interrupts(void);
static void fail(void) {
 (void)opencfw_bl_mask_interrupts();
 W(UINT32_MAX)=0;
 for(;;)__asm__ volatile("b .":::"memory");
}
uint32_t opencfw_boot_thread_state(uint32_t *tcb) {
 if(!tcb)fail();
 if((uintptr_t)tcb==W(0x20027134))return 0;
 opencfw_bl_kernel_enter();
 uint32_t state_list=tcb[5],delayed=W(0x20027138),overflow=W(0x2002713c);
 opencfw_bl_kernel_exit();
 if(state_list==delayed || state_list==overflow)return 2;
 if(state_list==0x20026f84u) {
  if(tcb[10])return 2;
  return ((volatile uint8_t *)tcb)[0x6c]==1 ? 2 : 3;
 }
 if(state_list==0x20026f70u || !state_list)return 4;
 return 1;
}
void opencfw_boot_thread_release_storage(uint32_t *tcb) {
 uint8_t ownership=((volatile uint8_t *)tcb)[0x6d];
 if(!ownership) {opencfw_bl_rtos_free((void *)(uintptr_t)tcb[12]);opencfw_bl_rtos_free(tcb);return;}
 /* Stock rereads ownership; do not replace volatile reads by cached value. */
 ownership=((volatile uint8_t *)tcb)[0x6d];
 if(ownership==1) {opencfw_bl_rtos_free(tcb);return;}
 if(((volatile uint8_t *)tcb)[0x6d]!=2)fail();
}
static void insert_end(uint32_t *list,uint32_t *item) {
 uint32_t *index=(uint32_t *)(uintptr_t)list[1];
 item[1]=(uintptr_t)index;item[2]=index[2];
 ((uint32_t *)(uintptr_t)index[2])[1]=(uintptr_t)item;
 index[2]=(uintptr_t)item;item[4]=(uintptr_t)list;list[0]++;
}
void opencfw_boot_thread_delete(uint32_t *tcb) {
 opencfw_bl_kernel_enter();
 if(!tcb)tcb=(uint32_t *)(uintptr_t)W(0x20027134);
 (void)opencfw_boot_list_unlink(tcb+1);
 if(tcb[10])(void)opencfw_boot_list_unlink(tcb+6);
 W(0x20027160)++;
 if((uintptr_t)tcb==W(0x20027134)) {
  insert_end((uint32_t *)(uintptr_t)0x20026f70,tcb+1);
  W(0x20027140)++;
 } else {W(0x20027144)--;opencfw_boot_next_unblock_refresh();}
 opencfw_bl_kernel_exit();
 if((uintptr_t)tcb!=W(0x20027134))opencfw_boot_thread_release_storage(tcb);
 if(W(0x20027150) && (uintptr_t)tcb==W(0x20027134)) {
  if(W(0x2002716c))fail();
  opencfw_bl_kernel_reschedule();
 }
}
/* Original416238 pops saved incomingR3 intoR1; model both return words. */
uint64_t opencfw_boot_runtime_action(uint32_t handle,uint32_t unused1,
                                    uint32_t unused2,uint32_t carry) {
 (void)unused1;(void)unused2;uint32_t result;
 if(opencfw_bl_context_guard())result=0xfffffffau;
 else if(!handle)result=0xfffffffcu;
 else if((uint8_t)opencfw_boot_thread_state((uint32_t *)(uintptr_t)handle)==4)result=0xfffffffdu;
 else {result=0;opencfw_boot_thread_delete((uint32_t *)(uintptr_t)handle);}
 return ((uint64_t)carry<<32)|result;
}
