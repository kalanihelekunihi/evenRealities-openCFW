#include <stdint.h>

/* Native 0x32b61c..0x32b82a: create the BIG (broadcast isochronous group)
 * of an advertising set. Clear the 148-byte group object (+380) and set up
 * its event descriptor (+428: callbacks 0x32b618/0x32b9a4, owner, header 8,
 * random seed +696, TX power +60 or default 0x805a9c, access address from
 * +372, CRC init from native 0x318960, PHY +63, ISO payload callback
 * 0x32c69c, timing words 0x805cc8/0x805ccc/0x805ca0/0x805ca4/0x805c28, max
 * retransmissions min(config +24, 10)); derive the subevent/BIS spacing
 * (+796 * 1250 us, +797 * 125 us) and their window widening for SCA 5 and
 * initialise the scheduler object. Compute the event duration (native
 * 0x312be4, optional extra time from the hook at 0x801a14 when +804 is set)
 * and reserve a slot (native 0x3133b4, id = set index + 4) within the
 * group's interval limits (+708/+712); fail with 0x45 when the event does
 * not fit, 0x43 when no slot is free. On success store the anchor
 * (+700/+400), start the group (native 0x32b82c) and return 0. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_random_31896c(void);
extern uint32_t opencfw_em9305_radio_crc_seed_318960(void);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_radio_duration_312be4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_slot_query_31b2fc(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_child_32b82c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_cycle_tail_32b618(uintptr_t);
extern uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t);
extern uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t,uint32_t);

#define BIG_U8(a) (*(volatile uint8_t *)(a))
#define BIG_U16(a) (*(volatile uint16_t *)(a))
#define BIG_U32(a) (*(volatile uint32_t *)(a))

uint32_t opencfw_em9305_callback_32b61c(uintptr_t set)
{
    uint32_t anchor;
    uintptr_t object = set + 380u;
    uintptr_t event = set + 428u;
    (void)opencfw_em9305_memset((void *)object, 0u, 0x94u);
    BIG_U8(set + 406u) = 1u;
    BIG_U8(set + 404u) = 1u;
    BIG_U32(set + 412u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_cycle_tail_32b618;
    BIG_U32(set + 408u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_cycle_callback_32b9a4;
    BIG_U32(set + 416u) = (uint32_t)set;
    BIG_U32(set + 424u) = (uint32_t)event;
    BIG_U32(set + 420u) = (uint32_t)(set + 1144u);
    uint32_t seed = opencfw_em9305_associated_random_31896c();
    uint32_t power = (uint32_t)(int32_t)BIG_U8(set + 60u);
    power = (uint32_t)(int32_t)(int8_t)power;
    uint32_t count = BIG_U8(set + 697u);
    BIG_U8(set + 696u) = (uint8_t)seed;
    BIG_U8(set + 428u) = 8u;
    BIG_U8(set + 429u) = (uint8_t)count;
    if (power == 0x7fu) power = BIG_U8(0x805a9cu);
    uint32_t access = BIG_U32(set + 372u);
    uint32_t base_crc = BIG_U32(set + 784u);
    BIG_U8(set + 430u) = (uint8_t)power;
    BIG_U32(set + 432u) = access;
    BIG_U32(set + 500u) = base_crc;
    BIG_U32(set + 436u) = opencfw_em9305_radio_crc_seed_318960();
    uint32_t phy = BIG_U8(set + 63u);
    uint32_t default_phy = BIG_U8(0x805bedu);
    BIG_U32(set + 568u) = (uint32_t)(set + 1077u);
    BIG_U32(set + 532u) = (uint32_t)(set + 1077u);
    uintptr_t config = BIG_U32(0x805cacu);
    BIG_U8(set + 440u) = (uint8_t)phy;
    BIG_U8(set + 441u) = (uint8_t)phy;
    BIG_U8(set + 442u) = (uint8_t)default_phy;
    uint32_t spacing = BIG_U8(set + 796u);
    uint32_t bis_spacing = BIG_U8(set + 797u);
    int32_t retries = (int32_t)BIG_U8(config + 0x18u);
    uint32_t timing0 = BIG_U32(0x805cc8u);
    uint32_t timing1 = BIG_U32(0x805cccu);
    uint32_t timing2 = BIG_U32(0x805ca0u);
    uint32_t timing3 = BIG_U32(0x805ca4u);
    uint32_t timing4 = BIG_U32(0x805c28u);
    BIG_U8(set + 654u) = (uint8_t)(retries < 10 ? retries : 10);
    BIG_U32(set + 588u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_packet_callback_32c69c;
    BIG_U16(set + 1154u) = 0u;
    BIG_U32(set + 580u) = timing0;
    BIG_U32(set + 592u) = timing1;
    BIG_U32(set + 596u) = timing2;
    BIG_U32(set + 600u) = timing3;
    BIG_U32(set + 660u) = timing4;
    BIG_U32(set + 672u) = spacing * 1250u;
    BIG_U32(set + 676u) = bis_spacing * 125u;
    uint32_t accuracy = opencfw_em9305_mode_callback_child_317ea4(5u);
    BIG_U32(set + 680u) = opencfw_em9305_init_secondary_time_317ebc(BIG_U32(set + 672u), accuracy);
    uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(BIG_U32(set + 676u), accuracy);
    uint32_t phases = BIG_U8(set + 798u);
    BIG_U32(set + 684u) = widening;
    BIG_U8(set + 656u) = (uint8_t)phases;
    (void)opencfw_em9305_init_callback_child_3246c0(event);
    (void)opencfw_em9305_associated_object_init_312918(object, 0u);
    config = BIG_U32(0x805cacu);
    uint32_t requested = BIG_U32(set + 72u);
    uint32_t maximum = BIG_U32(set + 712u);
    uint32_t minimum = BIG_U32(set + 708u);
    uint32_t length = BIG_U16(config + 0x14u);
    if (requested > length) length = requested;
    uint32_t extra = 0u;
    if (BIG_U8(set + 804u) != 0u) {
        uintptr_t hook = BIG_U32(0x801a14u);
        if (hook != 0u) extra = ((uint32_t (*)(void))hook)();
    }
    uint32_t duration = opencfw_em9305_radio_duration_312be4(BIG_U8(set + 63u), 0u, extra, (uint16_t)length,
                                                             BIG_U16(set + 1144u), 0u, 2u, 5u);
    uint32_t reserved = BIG_U32(set + 392u);
    if (duration > reserved) reserved = duration;
    BIG_U32(set + 392u) = reserved;
    if (maximum < duration) return 0x45u;
    if (duration > minimum) minimum = duration;
    uint32_t index = (uint32_t)((int32_t)(set - BIG_U32(0x805c38u)) / 0xb08);
    if (opencfw_em9305_associated_slot_allocate_3133b4((uint8_t)(index + 4u), 1u, minimum, maximum, reserved,
                                                       (uintptr_t)&anchor,
                                                       (uintptr_t)opencfw_em9305_associated_slot_query_31b2fc) == 0u)
        return 0x43u;
    BIG_U32(set + 700u) = anchor;
    BIG_U32(set + 400u) = anchor;
    (void)opencfw_em9305_child_32b82c(set, object);
    return 0u;
}
