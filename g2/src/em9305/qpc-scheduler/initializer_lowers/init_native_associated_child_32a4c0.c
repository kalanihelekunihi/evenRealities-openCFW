#include <stdint.h>

/* Native 0x32a4c0..0x32a5aa: apply a pending connection-parameter update at
 * its instant. Advance the anchor (+208) by the events elapsed since the
 * last update (+262 + 1 - +202) times the old interval (+266, 1250 us units),
 * also recording that delta at +212 unless the instant (+682) matches; take
 * over interval (+676), latency (+678) and supervision timeout (+680, 10 ms
 * units) into +266/+260/+382 and the instant counter +202. Unless keep is
 * set, apply the transmit window offset/size (+674/+672) and the extra
 * window widening (native 0x317ebc) to the timing words. Restart the
 * supervision timer (+384) for timeout + 1.25 * old interval ms, flag a
 * parameter change in +636 bit 17, and clear +216 / set +628. */
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);

void opencfw_em9305_associated_child_32a4c0(uintptr_t record, uint32_t keep)
{
    uint32_t counter = *(volatile uint16_t *)(record + 262u);
    uint32_t last = *(volatile uint16_t *)(record + 202u);
    uint32_t interval = *(volatile uint16_t *)(record + 266u);
    uint32_t next = counter + 1u;
    uint32_t delta = interval * ((next - last) & 0xffffu) * 1250u;
    uint32_t instant = *(volatile uint16_t *)(record + 682u);
    volatile uint32_t *anchor = (volatile uint32_t *)(record + 208u);
    *anchor = *anchor + delta;
    if (instant != last) *(volatile uint32_t *)(record + 212u) = delta;
    uint32_t timeout = *(volatile uint16_t *)(record + 680u);
    uint32_t new_interval = *(volatile uint16_t *)(record + 676u);
    uint32_t new_latency = *(volatile uint16_t *)(record + 678u);
    uint32_t supervision = timeout * 10u;
    uint32_t old_supervision = *(volatile uint16_t *)(record + 382u);
    uint32_t old_latency = *(volatile uint16_t *)(record + 260u);
    *(volatile uint16_t *)(record + 202u) = (uint16_t)next;
    *(volatile uint16_t *)(record + 266u) = (uint16_t)new_interval;
    *(volatile uint16_t *)(record + 260u) = (uint16_t)new_latency;
    *(volatile uint16_t *)(record + 382u) = (uint16_t)supervision;
    if (keep == 0u) {
        uint32_t offset = *(volatile uint16_t *)(record + 674u) * 1250u;
        uint32_t size = *(volatile uint8_t *)(record + 672u) * 1250u;
        uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(
            size + offset, *(volatile uint16_t *)(record + 200u));
        uint32_t start = *anchor;
        uint32_t window_start = *(volatile uint32_t *)(record + 0x18u);
        uint32_t window_end = *(volatile uint32_t *)(record + 28u);
        uint32_t widen = *(volatile uint32_t *)(record + 164u);
        supervision = *(volatile uint16_t *)(record + 382u);
        *(volatile uint32_t *)(record + 204u) = size;
        *anchor = start + offset;
        *(volatile uint32_t *)(record + 0x18u) = window_start + (offset - widening);
        *(volatile uint32_t *)(record + 28u) = widening + window_end;
        *(volatile uint32_t *)(record + 164u) = size + widening * 2u + widen;
    }
    uint32_t grace = interval + (interval >> 2) + ((interval & 3u) != 0u ? 1u : 0u);
    (void)opencfw_em9305_wsf_timer_start_ms(record + 384u, (supervision & 0xffffu) + grace);
    if (*(volatile uint16_t *)(record + 266u) != interval ||
        *(volatile uint16_t *)(record + 260u) != old_latency ||
        *(volatile uint16_t *)(record + 382u) != old_supervision) {
        volatile uint32_t *flags = (volatile uint32_t *)(record + 636u);
        *flags = *flags | (1u << 17);
    }
    *(volatile uint8_t *)(record + 216u) = 0u;
    *(volatile uint8_t *)(record + 628u) = 1u;
}
