/* Locked bootloader service record initialization; kernel mutex calls remain
 * explicit dependencies. Success does not certify allocation or ownership. */
#include "service_records.h"
#include <stddef.h>
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t opencfw_bl_mutex_create(uint32_t attributes);
extern int32_t opencfw_boot_fs_mutex_acquire(uint32_t handle,uint32_t timeout);
extern int32_t opencfw_boot_fs_mutex_release(uint32_t handle);
extern void *memset(void *destination,int value,size_t count);
/* am/os mutex attributes: pinned name, flags0, supplied static80-byte buffer.
 * The name is source-owned at its stock address; no executable bytes retained. */
__attribute__((section(".boot_service_mutex_attributes"),used))
const uint32_t opencfw_boot_service_mutex_attributes[4]={0x433f50,0,0x20026cb0,80};
__attribute__((section(".boot_service_mutex_name"),used))
const char opencfw_boot_service_mutex_name[]="elogMutex";
NI void opencfw_boot_service_mutex_initialize(void) {
    if(!R(0x200270e8))R(0x200270e8)=opencfw_bl_mutex_create(0x433d28);
}
NI uint32_t opencfw_bl_service_guard(void) {
    opencfw_boot_service_mutex_initialize();return 0;
}
NI void opencfw_boot_service_mutex_acquire(void) {
    if(R(0x200270e8))(void)opencfw_boot_fs_mutex_acquire(R(0x200270e8),1000);
}
NI void opencfw_boot_service_mutex_release(void) {
    if(R(0x200270e8))(void)opencfw_boot_fs_mutex_release(R(0x200270e8));
}
NI void opencfw_bl_service_wake(void) {opencfw_boot_service_mutex_acquire();}
NI void opencfw_bl_service_sleep(void) {opencfw_boot_service_mutex_release();}
NI void opencfw_bl_service_commit(void) {
    for(uint32_t i=0;i<5;i++){
        uint32_t p=0x20026700+33*i;
        memset((void *)(uintptr_t)(p+0x32),0,31);
        B(p+0x31)=0;B(p+0x51)=0;
    }
}
