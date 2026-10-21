#include <stdint.h>

extern uintptr_t opencfw_em9305_init_connection_allocate_316c58(void);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_connection_query_31b21c(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_access_raw_318878(void);
extern uint32_t opencfw_em9305_radio_crc_seed_318960(void);
extern uint32_t opencfw_em9305_associated_random_31896c(void);
extern uint32_t opencfw_em9305_compose_accuracy_318988(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_transition_finish_325eb4(uintptr_t,uint32_t);

struct native_product_pair { uint32_t low, high; };
static struct native_product_pair native_mpydu(uint32_t left,uint32_t right)
{
#ifdef __arc__
    register uint32_t low __asm__("r4");
    register uint32_t high __asm__("r5");
    __asm__ volatile("mpydu r4,%2,%3":"=r"(low),"=r"(high):
        "r"(left),"r"(right));
    struct native_product_pair result={low,high};
#else
    uint64_t product=(uint64_t)left*right;
    struct native_product_pair result={(uint32_t)product,
        (uint32_t)(product>>32u)};
#endif
    return result;
}

/* Full native 0x31a700..0x31a858. Initial R4/R5 are fifth/sixth ABI
 * arguments. Native request/nested pointers are deliberately reloaded after
 * allocator and random helpers where the machine does so. */
uint32_t opencfw_em9305_init_transition_prepare_31a700(
    uintptr_t request,uint32_t fresh,uint32_t address_low,
    uint32_t address_high,uint32_t extra,uint32_t mode)
{
    uintptr_t request_slot=request+0xafcu;
    uintptr_t nested=*(volatile uint32_t *)request_slot;
    const uintptr_t initial_nested=nested; /* Native R18 survives children. */
    uintptr_t connection=opencfw_em9305_init_connection_allocate_316c58();
    uint32_t status=9u;
    if(connection!=0u) {
        uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
        uint32_t minimum=*(volatile uint16_t *)(nested+82u)*1250u;
        uint32_t maximum=*(volatile uint16_t *)(nested+84u)*1250u;
        uint32_t id=(uint8_t)((int32_t)(connection-base)/912);
        uint32_t extent=*(volatile uint16_t *)(connection+592u);
        uint32_t allocation;
        uint32_t accepted=opencfw_em9305_associated_slot_allocate_3133b4(
            id,0u,minimum,maximum,extent,(uintptr_t)&allocation,
            (uintptr_t)opencfw_em9305_init_connection_query_31b21c);
        if(accepted!=0u) {
            base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
            uint32_t selected=allocation;
            nested=*(volatile uint32_t *)request_slot;
            uint32_t relative=(uint32_t)(connection-base);
            uint32_t req_high=*(volatile uint32_t *)(request+20u);
            uint32_t req_low=*(volatile uint32_t *)(request+16u);
            struct native_product_pair product=native_mpydu(selected,0x1a36e3u);
            uint32_t connection_id=(uint8_t)((int32_t)relative/912);
            *(volatile uint32_t *)(nested+104u)=req_high;
            *(volatile uint32_t *)(nested+100u)=req_low;
            uint32_t saved_high=*(volatile uint32_t *)(nested+72u);
            uint32_t saved_low=*(volatile uint32_t *)(nested+68u);
            /* Native two-operand `asl r1,r5` is high<<1 (not an
             * operand-variable shift of saved_low). */
            uint32_t scaled=(product.high<<1u)|(product.low>>31u);
            *(volatile uint16_t *)(nested+96u)=(uint16_t)scaled;
            *(volatile uint32_t *)(nested+112u)=saved_high;
            *(volatile uint32_t *)(nested+108u)=saved_low;
            *(volatile uint16_t *)(nested+94u)=(uint8_t)connection_id;
            uint32_t access=opencfw_em9305_radio_access_raw_318878();
            *(volatile uint32_t *)(nested+116u)=access;
            uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
            uintptr_t fresh_nested=*(volatile uint32_t *)request_slot;
            uint16_t request_second=*(volatile uint16_t *)(initial_nested+88u);
            uint16_t request_first=*(volatile uint16_t *)(initial_nested+86u);
            *(volatile uint32_t *)(nested+120u)=crc;
            *(volatile uint16_t *)(nested+136u)=request_second;
            uint32_t shared_high=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
            uint32_t shared_low=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
            uint16_t nested_value=*(volatile uint16_t *)(fresh_nested+96u);
            *(volatile uint8_t *)(nested+138u)=1u;
            *(volatile uint16_t *)(nested+134u)=request_first;
            *(volatile uint32_t *)(nested+128u)=shared_high;
            *(volatile uint32_t *)(nested+124u)=shared_low;
            *(volatile uint16_t *)(nested+132u)=nested_value;
            uint32_t random=opencfw_em9305_associated_random_31896c();
            *(volatile uint8_t *)(nested+142u)=(uint8_t)random;
            uint32_t accuracy=opencfw_em9305_compose_accuracy_318988();
            fresh_nested=*(volatile uint32_t *)request_slot;
            base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
            *(volatile uint8_t *)(nested+143u)=(uint8_t)accuracy;
            uint16_t target_id=*(volatile uint16_t *)(fresh_nested+94u);
            *(volatile uint8_t *)(request+2262u)=0u;
            *(volatile uint8_t *)(fresh_nested+65u)=(uint8_t)mode;
            uintptr_t target=base+(uint32_t)target_id*912u;
            *(volatile uint32_t *)(target+520u)=address_high;
            *(volatile uint32_t *)(target+516u)=address_low;
            *(volatile uint8_t *)(target+524u)=(uint8_t)fresh;
            (void)opencfw_em9305_common_request_30455c(1u);
            uint8_t pending=*(volatile uint8_t *)(uintptr_t)0x805a74u;
            *(volatile uint8_t *)(uintptr_t)0x805a74u=(uint8_t)(pending+1u);
            (void)opencfw_em9305_command_count_30e4bc();
            return 0u;
        }
        (void)opencfw_em9305_init_connection_release_31ad90(connection);
        status=13u;
    }
    uint8_t identity=*(volatile uint8_t *)(request+1u);
    (void)opencfw_em9305_init_transition_report_316908(
        identity,status,fresh,address_low,address_high);
    (void)opencfw_em9305_init_transition_finish_325eb4(request,2u);
    (void)extra;
    return status;
}
