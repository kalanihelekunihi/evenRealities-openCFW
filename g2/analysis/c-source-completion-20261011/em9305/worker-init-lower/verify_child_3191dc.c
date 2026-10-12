#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_child_3191dc(uint32_t context, uint32_t packet, uint32_t mode);
static uint32_t calls, last_context, last_payload, last_mode, last_identity;
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t context, uintptr_t packet)
{
    *(volatile uint8_t *)(context + 5u) = *(volatile uint8_t *)(packet + 1u);
    return (*(volatile uint8_t *)packet & 0x20u) ? 3u : 2u;
}
uint32_t opencfw_em9305_packet_entry_3191ac(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3191acu;
    return 0x3191acu;
}
uint32_t opencfw_em9305_packet_entry_3191c4(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3191c4u;
    return 0x3191c4u;
}
uint32_t opencfw_em9305_packet_entry_319204(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319204u;
    return 0x319204u;
}
uint32_t opencfw_em9305_packet_entry_319208(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319208u;
    return 0x319208u;
}
uint32_t opencfw_em9305_packet_entry_319234(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319234u;
    return 0x319234u;
}
uint32_t opencfw_em9305_packet_entry_319268(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319268u;
    return 0x319268u;
}
uint32_t opencfw_em9305_packet_entry_319298(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319298u;
    return 0x319298u;
}
uint32_t opencfw_em9305_packet_entry_3192c0(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3192c0u;
    return 0x3192c0u;
}
uint32_t opencfw_em9305_packet_entry_3192e8(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3192e8u;
    return 0x3192e8u;
}
uint32_t opencfw_em9305_packet_entry_319310(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319310u;
    return 0x319310u;
}
uint32_t opencfw_em9305_packet_entry_319338(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319338u;
    return 0x319338u;
}
uint32_t opencfw_em9305_packet_entry_31935c(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x31935cu;
    return 0x31935cu;
}
uint32_t opencfw_em9305_packet_entry_31936c(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x31936cu;
    return 0x31936cu;
}
uint32_t opencfw_em9305_packet_entry_3193d8(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3193d8u;
    return 0x3193d8u;
}
uint32_t opencfw_em9305_packet_entry_319400(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319400u;
    return 0x319400u;
}
uint32_t opencfw_em9305_packet_entry_319414(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319414u;
    return 0x319414u;
}
uint32_t opencfw_em9305_packet_entry_319420(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319420u;
    return 0x319420u;
}
uint32_t opencfw_em9305_packet_entry_319438(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319438u;
    return 0x319438u;
}
uint32_t opencfw_em9305_packet_entry_319450(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319450u;
    return 0x319450u;
}
uint32_t opencfw_em9305_packet_entry_31948c(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x31948cu;
    return 0x31948cu;
}
uint32_t opencfw_em9305_packet_entry_3194ac(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3194acu;
    return 0x3194acu;
}
uint32_t opencfw_em9305_packet_entry_3194cc(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3194ccu;
    return 0x3194ccu;
}
uint32_t opencfw_em9305_packet_entry_3194f4(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3194f4u;
    return 0x3194f4u;
}
uint32_t opencfw_em9305_packet_entry_319518(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319518u;
    return 0x319518u;
}
uint32_t opencfw_em9305_packet_entry_31953c(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x31953cu;
    return 0x31953cu;
}
uint32_t opencfw_em9305_packet_entry_319564(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319564u;
    return 0x319564u;
}
uint32_t opencfw_em9305_packet_entry_319574(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319574u;
    return 0x319574u;
}
uint32_t opencfw_em9305_packet_entry_3195a0(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3195a0u;
    return 0x3195a0u;
}
uint32_t opencfw_em9305_packet_entry_3195cc(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3195ccu;
    return 0x3195ccu;
}
uint32_t opencfw_em9305_packet_entry_3195f4(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3195f4u;
    return 0x3195f4u;
}
uint32_t opencfw_em9305_packet_entry_319620(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319620u;
    return 0x319620u;
}
uint32_t opencfw_em9305_packet_entry_319644(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319644u;
    return 0x319644u;
}
uint32_t opencfw_em9305_packet_entry_319698(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319698u;
    return 0x319698u;
}
uint32_t opencfw_em9305_packet_entry_3196ec(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x3196ecu;
    return 0x3196ecu;
}
uint32_t opencfw_em9305_packet_entry_319700(uint32_t context, uint32_t payload, uint32_t mode)
{
    ++calls; last_context=context; last_payload=payload; last_mode=mode; last_identity=0x319700u;
    return 0x319700u;
}

int main(void)
{
    assert(mmap((void *)0x800000u, 0x2000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) == (void *)0x800000u);
    const uint32_t targets[43] = {
        0x31936cu, /* 0 */
        0x319268u, /* 1 */
        0x3196ecu, /* 2 */
        0x319204u, /* 3 */
        0x319204u, /* 4 */
        0x319204u, /* 5 */
        0x319204u, /* 6 */
        0x319700u, /* 7 */
        0x319414u, /* 8 */
        0x319420u, /* 9 */
        0x319204u, /* 10 */
        0x319204u, /* 11 */
        0x3191c4u, /* 12 */
        0x3191acu, /* 13 */
        0x3194ccu, /* 14 */
        0x319338u, /* 15 */
        0x31935cu, /* 16 */
        0x319620u, /* 17 */
        0x319204u, /* 18 */
        0x319204u, /* 19 */
        0x319438u, /* 20 */
        0x319438u, /* 21 */
        0x31953cu, /* 22 */
        0x319564u, /* 23 */
        0x319574u, /* 24 */
        0x319450u, /* 25 */
        0x3193d8u, /* 26 */
        0x319400u, /* 27 */
        0x3194f4u, /* 28 */
        0x31948cu, /* 29 */
        0x3194acu, /* 30 */
        0x3192c0u, /* 31 */
        0x3192e8u, /* 32 */
        0x319298u, /* 33 */
        0x319310u, /* 34 */
        0x3195ccu, /* 35 */
        0x3195f4u, /* 36 */
        0x3195a0u, /* 37 */
        0x319698u, /* 38 */
        0x319644u, /* 39 */
        0x319208u, /* 40 */
        0x319234u, /* 41 */
        0x319518u, /* 42 */
    };
    for (unsigned header = 0; header < 2; ++header)
    for (unsigned opcode = 0; opcode < 43; ++opcode) {
        memset((void *)0x800000u, 0, 0x2000u);
        *(volatile uint8_t *)0x801000u = header ? 0x20u : 0u;
        *(volatile uint8_t *)0x801001u = 0x5au;
        *(volatile uint8_t *)(uintptr_t)(0x801002u + header) = (uint8_t)opcode;
        calls=0u;
        uint32_t result=opencfw_em9305_child_3191dc(0x800000u,0x801000u,0xabcd1234u);
        assert(calls==1u && result==targets[opcode] && last_identity==targets[opcode]);
        assert(last_context==0x800000u && last_payload==0x801002u+header && last_mode==0xabcd1234u);
        assert(*(volatile uint8_t *)0x800008u==opcode && *(volatile uint8_t *)0x800005u==0x5au);
    }
    for (unsigned bad = 43; bad <= 255; bad += 212) {
        *(volatile uint8_t *)0x801000u = 0u;
        *(volatile uint8_t *)0x801002u = (uint8_t)bad;
        *(volatile uint8_t *)0x800008u = 0xa5u;
        calls=0u;
        assert(opencfw_em9305_child_3191dc(0x800000u,0x801000u,0u)==25u);
        assert(calls==0u && *(volatile uint8_t *)0x800008u==(uint8_t)bad);
    }
    puts("PASS child 3191dc 86 routed and two invalid opcodes");
    return 0;
}
