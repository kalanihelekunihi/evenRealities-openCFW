/* Native LV heap wrappers and pool accounting; no executable data retained. */
#include <stdint.h>
extern uint8_t audio_uart_lv_heap_pool[],audio_uart_lv_static_slot[];
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *g2_file_pool_allocate(void *,uint32_t);
extern void g2_file_pool_free(void *,void *);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* tlsf_block_size 0x4D05E4 is compiled from pinned TLSF 3.1 (alias). */
extern uint32_t audio_uart_lv_allocation_size_4d05e4(void *pointer);
void *audio_uart_lv_pool_allocate_484180(void *cell,uint32_t bytes) {
    volatile uint32_t *pool=cell;
    if(bytes==0u)return 0;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)!=1)return 0;
    void *result=g2_file_pool_allocate((void *)(uintptr_t)pool[1],bytes);
    if(result!=0) {
        uint32_t amount=audio_uart_lv_allocation_size_4d05e4(result);
        pool[2]=amount+pool[2];
        uint32_t high=pool[3];
        if(high<pool[2])high=pool[2];else high=pool[3];
        pool[3]=high;
    }
    (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0,0);
    return result;
}
void *audio_uart_lv_pool_allocate_48431e(uint32_t bytes) {
    return audio_uart_lv_pool_allocate_484180(audio_uart_lv_heap_pool,bytes);
}
void audio_uart_lv_pool_free_48429e(void *cell,void *pointer) {
    volatile uint32_t *pool=cell;
    if(pointer==0)return;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)!=1)return;
    uint32_t amount=audio_uart_lv_allocation_size_4d05e4(pointer);
    g2_file_pool_free((void *)(uintptr_t)pool[1],pointer);
    if(amount<pool[2])pool[2]=pool[2]-amount;else pool[2]=0u;
    (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0,0);
}
void audio_uart_lv_pool_free_484338(void *pointer) {
    audio_uart_lv_pool_free_48429e(audio_uart_lv_heap_pool,pointer);
}

/* Native heap startup and TLSF control composition. */
#include <stdint.h>
extern void *audio_uart_mutex_dynamic_create(uint32_t);
extern void g2_file_heap_error_log(const char *);
extern void audio_uart_heap_memory_configure_4840c8(void);
/* tlsf_create_with_pool 0x4D06EC is compiled from pinned TLSF 3.1 (alias). */
extern void *g2_tlsf_create_with_pool_4d06ec(void *memory,uint32_t bytes);
void audio_uart_lv_pool_initialize_48413c(void *cell,void *memory,uint32_t bytes) {
    volatile uint32_t *pool=cell;
    pool[1]=(uint32_t)(uintptr_t)g2_tlsf_create_with_pool_4d06ec(memory,bytes);
    if(pool[1]==0u) {
        g2_file_heap_error_log((const char *)(uintptr_t)0x75165cu);
        for(;;)__asm__ volatile("" ::: "memory");
    }
    pool[0]=(uint32_t)(uintptr_t)audio_uart_mutex_dynamic_create(1u);
    if(pool[0]==0u) {
        g2_file_heap_error_log((const char *)(uintptr_t)0x75d650u);
        for(;;)__asm__ volatile("" ::: "memory");
    }
    pool[2]=0u;pool[3]=0u;pool[4]=bytes;pool[5]=(uint32_t)(uintptr_t)memory;
}
void audio_uart_heap_initialize_4842e6(void) {
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000338u,(void *)(uintptr_t)0x20279670u,0x2d000u);
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000354u,(void *)(uintptr_t)0x2013be70u,0xcd000u);
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000370u,(void *)(uintptr_t)0x20378d9cu,0x400u);
    audio_uart_heap_memory_configure_4840c8();
    *(volatile uint8_t *)(uintptr_t)0x2000036cu=0u;
    *(volatile uint8_t *)(uintptr_t)0x20000388u=0u;
}

/* TLSF control_construct 0x4D0524, tlsf_create 0x4D06B4, block_set_free
 * 0x4CFDC0, block_set_used 0x4CFDCE and tlsf_add_pool 0x4D0608 are compiled
 * from pinned TLSF 3.1 (third-party/upstream/tlsf/tlsf.c). */

/* Native memory-protection configuration sequence and descriptors. */
#include <stdint.h>
extern uint32_t audio_uart_mpu_reset_4d44e2(void);
extern uint32_t audio_uart_mpu_attributes_4d450c(const void *,uint32_t);
extern uint32_t audio_uart_mpu_region_4d4596(const void *,uint32_t);
extern uint32_t audio_uart_mpu_enable_4d44ec(uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t);
/* Authenticated non-executable descriptor words at789fec/774bc4/774bdc. */
static const uint32_t secondary[6]={6u,0x2013be70u,0x10100u,0x20208e6fu,0u,1u};
static const uint32_t small[6]={7u,0x20378d9cu,0x10100u,0x2037919bu,0u,1u};
void audio_uart_heap_memory_configure_4840c8(void) {
    uint32_t attributes[3];
    uint32_t secondary_copy[6],small_copy[6];
    (void)audio_uart_mpu_reset_4d44e2();
    attributes[0]=0x1000100u;attributes[1]=0x1000000u;attributes[2]=0u;
    (void)audio_uart_mpu_attributes_4d450c(attributes,1u);
    audio_uart_checksum_copy(secondary_copy,secondary,24u);
    (void)audio_uart_mpu_region_4d4596(secondary_copy,1u);
    audio_uart_checksum_copy(small_copy,small,24u);
    (void)audio_uart_mpu_region_4d4596(small_copy,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x200007bcu,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x200007d4u,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x20000630u,1u);
    (void)audio_uart_mpu_region_4d4596((const void *)(uintptr_t)0x20000c20u,1u);
    audio_ble_privacy_cache_maintenance(0,1u);
    (void)audio_uart_mpu_enable_4d44ec(1u,1u);
}

/* Native MPU control registers and wrappers. */
#include <stdint.h>
static volatile uint32_t *const mpu_control=(volatile uint32_t *)(uintptr_t)0xe000ed94u;
static volatile uint32_t *const system_handler_control=(volatile uint32_t *)(uintptr_t)0xe000ed24u;
void audio_uart_mpu_enable_registers_4d43b4(uint32_t flags) {
    __asm__ volatile("dmb sy" ::: "memory");
    *mpu_control=flags|1u;
    *system_handler_control|=0x10000u;
    __asm__ volatile("dsb sy" ::: "memory");
    __asm__ volatile("isb sy" ::: "memory");
}
void audio_uart_mpu_disable_registers_4d43d4(void) {
    __asm__ volatile("dmb sy" ::: "memory");
    *system_handler_control&=~0x10000u;
    *mpu_control&=~1u;
    __asm__ volatile("dsb sy" ::: "memory");
    __asm__ volatile("isb sy" ::: "memory");
}
uint32_t audio_uart_mpu_reset_4d44e2(void) {
    audio_uart_mpu_disable_registers_4d43d4();
    return 0u;
}
uint32_t audio_uart_mpu_enable_4d44ec(uint32_t privileged_default,uint32_t fault_enable) {
    uint32_t flags=((uint32_t)(uint8_t)privileged_default<<2)|((uint32_t)(uint8_t)fault_enable<<1);
    if((*mpu_control&1u)!=0u)return 3u;
    audio_uart_mpu_enable_registers_4d43b4(flags);
    return 0u;
}

/* Native MPU descriptor parsing and packing. */
#include <stdint.h>
extern void audio_uart_mpu_attribute_write_4d4434(uint32_t,uint32_t);
extern void audio_uart_mpu_regions_write_4d44d2(uint32_t,const uint32_t *,uint32_t);
uint32_t audio_uart_mpu_attributes_4d450c(const void *descriptors,uint32_t count) {
    const volatile uint8_t *d=descriptors;
    if((*(volatile uint32_t *)(uintptr_t)0xe000ed94u&1u)!=0u)return 3u;
    for(uint32_t i=0;i<count;i++,d+=11u) {
        uint32_t id=d[0];
        if(id>=8u)return 5u;
        uint32_t outer,inner;
        if(d[1]==0u) {outer=0;inner=(uint32_t)d[10]<<2;}
        else {
            uint32_t a=d[2],b=d[3];outer=(a<<3)|(b<<2);
            outer|=(uint32_t)d[4]<<1;outer|=d[5];
            a=d[6];b=d[7];inner=(a<<3)|(b<<2);
            inner|=(uint32_t)d[8]<<1;inner|=d[9];
        }
        if((outer&15u)==0u)inner=((uint32_t)(uint8_t)inner<<2)&12u;
        else inner=(uint32_t)(uint8_t)inner&15u;
        audio_uart_mpu_attribute_write_4d4434((uint8_t)id,(uint8_t)(inner|(outer<<4)));
    }
    return 0u;
}
uint32_t audio_uart_mpu_region_4d4596(const void *descriptors,uint32_t count) {
    const volatile uint8_t *d=descriptors;
    uint32_t start=*(const volatile uint32_t *)(const void *)d;
    if((*(volatile uint32_t *)(uintptr_t)0xe000ed94u&1u)!=0u)return 3u;
    if(count+start>=17u)return 5u;
    uint32_t packed[32];
    for(uint32_t i=0;i<count;i++,d+=24u) {
        uint32_t base=*(const volatile uint32_t *)(const void *)(d+4u)&~31u;
        base|=(uint32_t)d[8]<<3;base|=(uint32_t)d[9]<<1;base|=d[10];
        packed[i*2u]=base;
        uint32_t limit=*(const volatile uint32_t *)(const void *)(d+12u)&~31u;
        limit|=*(const volatile uint32_t *)(const void *)(d+16u)<<1;limit|=d[20];
        packed[i*2u+1u]=limit;
    }
    audio_uart_mpu_regions_write_4d44d2(start,packed,count);
    return 0u;
}

/* Native MPU attribute, word-copy and bulk-region writers. */
#include <stdint.h>
void audio_uart_mpu_attribute_write_raw_4d43f6(void *registers,uint32_t id,uint32_t attribute) {
    uint32_t bank=(uint8_t)id>>2;
    uint32_t shift=((uint32_t)(uint8_t)id<<3)&24u;
    uint32_t mask=255u<<shift;
    uint32_t value=(uint32_t)(uint8_t)attribute<<shift;
    if(bank<2u) {
        volatile uint32_t *cell=(volatile uint32_t *)((uint8_t *)registers+48u+bank*4u);
        *cell=(*cell&~mask)|(value&mask);
    }
}
void audio_uart_mpu_attribute_write_4d4434(uint32_t id,uint32_t attribute) {
    audio_uart_mpu_attribute_write_raw_4d43f6((void *)(uintptr_t)0xe000ed90u,(uint8_t)id,(uint8_t)attribute);
}
void audio_uart_mpu_copy_words_4d4446(void *destination,const void *source,uint32_t count) {
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    for(uint32_t i=0;i<count;i++)d[i]=s[i];
}
void audio_uart_mpu_regions_write_raw_4d445e(void *registers,uint32_t start,const uint32_t *packed,uint32_t count) {
    volatile uint32_t *region_number=(volatile uint32_t *)((uint8_t *)registers+8u);
    if(count==1u) {
        *region_number=start;
        audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u,packed,2u);
        return;
    }
    uint32_t aligned=start&~3u;
    uint32_t index=start&3u;
    *region_number=aligned;
    while(count+index>=5u) {
        uint32_t chunk=4u-index;
        audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u+index*8u,packed,2u*chunk);
        packed+=2u*chunk;
        count-=chunk;index=0u;aligned+=4u;
        *region_number=aligned;
    }
    audio_uart_mpu_copy_words_4d4446((uint8_t *)registers+12u+index*8u,packed,2u*count);
}
void audio_uart_mpu_regions_write_4d44d2(uint32_t start,const uint32_t *packed,uint32_t count) {
    audio_uart_mpu_regions_write_raw_4d445e((void *)(uintptr_t)0xe000ed90u,start,packed,count);
}
