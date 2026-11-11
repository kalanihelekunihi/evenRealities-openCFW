#include <stdint.h>

/* Native 0x32a230..0x32a47c: associated-link receive callback (owner,
 * packet, kind). Records the kind (+269) and finishes a pending
 * termination (+628: hook 0x801314 with the link index in mode 1, then
 * reason 0x6e). Kind 2, kind 1/3 and a role-3 link that is not ready
 * drop the packet (kinds 3/4 also count +900). Otherwise the header is
 * decoded; kind 4 retries at most twice (+218, +908), kind 6 with even
 * sequence parity (+337/+346) terminates with reason 0x48, and an accepted
 * packet updates the receive counters, state and gate, may answer an
 * LL control PDU (31b7bc), prepares the radio and checks the response
 * timing before finishing the packet. */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t, uintptr_t);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);
extern uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t);
extern uint32_t opencfw_em9305_receive_state_324ea4(uintptr_t);
extern uint32_t opencfw_em9305_receive_gate_324f68(uintptr_t);
extern uint32_t opencfw_em9305_radio_prepare_32780c(uintptr_t, uint32_t, uint32_t);
extern uint32_t opencfw_em9305_auxiliary_start_303f50(void);
extern uint32_t opencfw_em9305_dispatch_child_312bc0(uint32_t, uint32_t);
extern uint32_t opencfw_em9305_receive_check_319838(uintptr_t, uint32_t, uint32_t);
extern uint32_t opencfw_em9305_associated_child_31b7bc(uint32_t);
extern uint32_t opencfw_em9305_receive_finish_324fb0(uintptr_t);
extern uint32_t opencfw_em9305_receive_packet_finish_3253c4(uintptr_t, uintptr_t, uint32_t, uint32_t);

uint32_t opencfw_em9305_associated_callback_32a230(uintptr_t owner, uintptr_t packet,
                                                   uint32_t kind)
{
    uintptr_t link = U32(owner + 36u);
    U8(link + 269u) = (uint8_t)kind;
    if (U8(link + 628u) != 0u) {
        uint32_t mode = U8(link + 635u);
        U8(link + 628u) = 0u;
        if (mode == 1u) {
            uintptr_t hook = U32(0x801314u);
            if (hook != 0u) {
                int32_t index = (int32_t)(link - U32(0x805c70u)) / 912;
                ((void (*)(uint32_t, int32_t))hook)((uint8_t)index, index);
            }
        }
        (void)opencfw_em9305_receive_terminate_325c08(link, 0x6eu);
    }
    if (kind == 2u)
        goto release;
    if (U8(link + 1u) == 3u) {
        int not_ready = U8(link + 629u) != 0u
            ? U8(link + 630u) != 0u
            : (U8(link + 620u) == 0u || U32(link + 360u) == 0u);
        if (not_ready) {
            if (kind == 3u || kind == 4u)
                goto count;
            goto signal;
        }
    }
    if (kind == 1u)
        goto signal;
    if (kind == 3u)
        goto count;
    if (U8(link + 219u) == 0u &&
        (kind == 0u || (kind == 4u && (U32(link + 4u) & 0x80000u) == 0u))) {
        uint32_t anchor = U32(link + 192u);
        U8(link + 219u) = 1u;
        U32(link + 224u) = anchor;
    }

    uint32_t header = U8(packet + opencfw_em9305_short_header_decode_32dedc(link + 344u, packet));
    uint32_t state = 0u, checked = 0u;
    if (kind == 4u) {
        uint32_t tries = (uint8_t)(U8(link + 218u) + 1u);
        U8(link + 218u) = (uint8_t)tries;
        U16(link + 908u) = (uint16_t)(U16(link + 908u) + 1u);
        if (tries >= 2u) {
            (void)opencfw_em9305_auxiliary_signal_304394();
            (void)opencfw_em9305_receive_packet_release_3253bc(packet);
            return 1u;
        }
    } else {
        if (kind == 0u) {
            U8(link + 218u) = 0u;
            U8(link + 220u) = 1u;
        }
        if (kind == 6u && ((U8(link + 337u) ^ U8(link + 346u)) & 1u) == 0u) {
            (void)opencfw_em9305_receive_terminate_325c08(link, 0x48u);
            (void)opencfw_em9305_auxiliary_signal_304394();
            return opencfw_em9305_receive_packet_release_3253bc(packet);
        }
        U16(link + 906u) = (uint16_t)(U16(link + 906u) + 1u);
        if (U8(link + 349u) != 0u)
            U16(0x805690u) = (uint16_t)(U16(0x805690u) + 1u);
        if (U8(link + 632u) == 0u && U8(link + 344u) != 3u && (U8(link + 5u) & 2u) != 0u)
            U8(link + 633u) = 1u;
        uint32_t idle;
        state = opencfw_em9305_receive_state_324ea4(link);
        if (state == 0xffffffffu) {
            idle = 1u;
            state = 0u;
        } else {
            idle = opencfw_em9305_receive_gate_324f68(link) ^ 1u;
        }
        if (U8(link + 216u) == 0u && idle == 0u)
            U8(link + 216u) = 1u;
        if (kind == 0u && U8(link + 344u) == 3u && header == 6u &&
            U8(link + 620u) == 1u && U8(link + 635u) == 0x13u &&
            opencfw_em9305_associated_child_31b7bc(link) != 0u)
            goto finish_signal;
    }

    uint32_t radio = opencfw_em9305_radio_prepare_32780c(link, kind, 1u);
    if (radio == 0u)
        goto finish_signal;
    if (U8(link + 632u) == 0u && U8(link + 633u) != 0u && (U8(link + 5u) & 2u) != 0u &&
        U8(link + 336u) == 3u)
        U8(link + 633u) = 0u;
    if (opencfw_em9305_auxiliary_start_303f50() == 0u &&
        (kind == 4u || U8(link + 347u) != 0u || U8(link + 339u) != 0u)) {
        uint32_t channel = U8(link + 76u);
        uint32_t anchor = U32(link + 192u);
        uint32_t delay = opencfw_em9305_dispatch_child_312bc0(channel, radio);
        checked = opencfw_em9305_receive_check_319838(link, anchor, U16(link + 592u) + delay) ^ 1u;
    }
    goto finish;

finish_signal:
    (void)opencfw_em9305_auxiliary_signal_304394();
finish:
    (void)opencfw_em9305_receive_finish_324fb0(link);
    if (U8(link + 344u) == 3u)
        U8(link + 630u) = 0u;
    return opencfw_em9305_receive_packet_finish_3253c4(link, packet, state, checked);

count:
    U32(link + 900u) = U32(link + 900u) + 1u;
signal:
    (void)opencfw_em9305_auxiliary_signal_304394();
release:
    (void)opencfw_em9305_receive_packet_release_3253bc(packet);
    return 0u;
}
