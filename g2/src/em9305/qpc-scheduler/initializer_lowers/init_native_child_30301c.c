#include <stdint.h>

/* Native 0x30301c..0x30324e: advertising/scan address filter policy. The
 * PDU kind (request +16) must be enabled in the filter mask (filter +0;
 * kind 9 alone passes on filter flag 0x80). The advertiser address (request
 * +0/+4, type +18) is copied twice into the report (out +0/+8) and
 * classified (native 0x314470, resolving when asked): rejected (3), resolved
 * (2) or listed (1). An expected peer (filter flags bit 2, +0x10/+0x14,
 * type bit 3) and the white list (filter +2 bit per kind, natives 0x303e5c,
 * 0x303df8) decide whether the report passes and whether it counts as a
 * resolved/identity match (out +20); out +21 marks acceptance. With target
 * checking (request +17 bit 1) the target address (request +8/+12, type
 * +19) must match our own address (filter +8/+12, flags bits 0/1), be an
 * associated RPA (flags bit 4, natives 0x303b7c/0x303844/0x3039f0) or be an
 * unresolved RPA accepted by flags bit 5. Returns 1 when accepted. */
extern uint32_t opencfw_em9305_radio_classify_314470(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_address_mode_303e5c(void);
extern uint32_t opencfw_em9305_radio_address_match_303df8(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_address_associate_303844(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_peer_kind_3039f0(uint32_t,uint32_t,uint32_t);

#define AF_U8(a) (*(volatile uint8_t *)(a))
#define AF_U16(a) (*(volatile uint16_t *)(a))
#define AF_U32(a) (*(volatile uint32_t *)(a))

struct address_key {
    uint32_t low;
    uint32_t high;
    uint8_t reserved[3];
    uint8_t type;
};

uint32_t opencfw_em9305_child_30301c(uintptr_t request, uintptr_t filter, uint32_t resolve, uintptr_t out)
{
    struct address_key key;
    uint32_t kind = AF_U8(request + 16u);
    if (((AF_U16(filter) >> (kind & 31u)) & 1u) == 0u) {
        if (kind != 9u) return 0u;
        return (AF_U8(filter + 4u) & 0x80u) != 0u ? 1u : 0u;
    }
    uint32_t high = AF_U32(request + 4u);
    uint32_t flags = AF_U32(filter + 4u);
    uint32_t low = AF_U32(request + 0u);
    uint32_t type = AF_U8(request + 18u);
    uint32_t list_mask = AF_U16(filter + 2u);
    AF_U32(out + 12u) = high;
    AF_U32(out + 4u) = high;
    AF_U32(out + 8u) = low;
    AF_U32(out + 0u) = low;
    uint32_t listed = ((1u << (kind & 31u)) & list_mask) & 0xffu;
    AF_U8(out + 19u) = (uint8_t)type;
    AF_U8(out + 18u) = (uint8_t)type;
    uint32_t class = opencfw_em9305_radio_classify_314470((flags & 64u) >> 6, resolve, out + 19u, out + 8u);
    uint32_t expect_peer = flags & 4u;
    uint32_t accept = 1u, verdict = 0u, fallback = 1u;
    if (class == 1u) {
        verdict = 3u;
        if ((expect_peer | listed) != 0u) return 0u;
        fallback = 0u;
    } else if (class == 3u) {
        return 0u;
    } else if (class == 2u) {
        verdict = 2u;
        fallback = 0u;
        accept = 0u;
    }
    uint32_t a_high = AF_U32(out + 12u);
    uint32_t a_low = AF_U32(out + 8u);
    uint32_t a_type = AF_U8(out + 19u);
    uint32_t level = 0u;
    if (expect_peer != 0u) {
        level = 3u;
        if (AF_U32(filter + 0x14u) == a_high && AF_U32(filter + 0x10u) == a_low &&
            (a_type != 0u ? 1u : 0u) == ((AF_U8(filter + 4u) & 8u) >> 3))
            level = 2u;
    }
    uint32_t score = 0u;
    if (listed != 0u) {
        if ((a_low | a_high) == 0u && opencfw_em9305_radio_address_mode_303e5c() != 0u)
            score = 2u;
        else
            score = (opencfw_em9305_radio_address_match_303df8(a_type != 0u, a_low, a_high) == 0u) + 2u;
    }
    uint32_t b_high = AF_U32(out + 12u);
    uint32_t b_low = AF_U32(out + 8u);
    a_type = AF_U8(out + 19u);
    uint32_t code;
    if (score < level) {
        if (expect_peer == 0u) {
            code = fallback == 0u ? verdict : 2u;
        } else {
            uint32_t mismatch = (a_type != 0u ? 1u : 0u) ^ ((AF_U8(filter + 4u) & 8u) >> 3);
            if (((AF_U32(filter + 0x10u) ^ b_low) | (AF_U32(filter + 0x14u) ^ b_high)) != 0u) mismatch |= 1u;
            if (mismatch == 0u) verdict = 2u;
            if (((accept | ~mismatch) & 1u) == 0u) return 0u;
            code = verdict;
        }
    } else if (listed == 0u) {
        code = fallback == 0u ? verdict : 2u;
    } else if ((b_low | b_high) == 0u && opencfw_em9305_radio_address_mode_303e5c() != 0u) {
        code = 2u;
    } else {
        uint32_t matched = opencfw_em9305_radio_address_match_303df8(a_type != 0u, b_low, b_high);
        if (matched != 0u) verdict = 2u;
        if ((accept | matched) == 0u) return 0u;
        code = verdict;
    }
    uint32_t options = AF_U8(request + 17u);
    AF_U8(out + 21u) = 1u;
    AF_U8(out + 20u) = code == 2u;
    if ((options & 2u) == 0u) return 1u;
    uint32_t target_flags = AF_U32(filter + 4u);
    uint32_t o_high = AF_U32(out + 12u);
    uint32_t peer_high = AF_U32(request + 12u);
    uint32_t peer_low = AF_U32(request + 8u);
    uint32_t peer_type = AF_U8(request + 19u);
    uint32_t o_type = AF_U8(out + 19u);
    uint32_t o_low = AF_U32(out + 8u);
    key.type = (uint8_t)o_type;
    key.high = o_high;
    key.low = o_low;
    if ((target_flags & 0x10u) != 0u) {
        if (peer_type != 0u && (peer_high & 0xc000u) == 0x4000u) {
            uint32_t k_type = o_type, k_low = o_low, k_high = o_high;
            if (resolve != 0u) {
                (void)opencfw_em9305_radio_address_project_303b7c(peer_low, peer_high, (uintptr_t)&key.type,
                                                                  (uintptr_t)&key);
                k_high = key.high;
                k_low = key.low;
                k_type = key.type;
            }
            if (opencfw_em9305_radio_address_associate_303844(peer_low, peer_high, k_type, k_low, k_high) != 0u)
                return 1u;
        } else if ((opencfw_em9305_radio_peer_kind_3039f0(o_type != 0u, o_low, o_high) & 0xfeu) == 2u) {
            return 0u;
        }
    }
    uint32_t own = AF_U32(filter + 4u);
    if ((own & 1u) == 0u) return 1u;
    if ((((peer_type != 0u ? 1u : 0u) ^ (own >> 1)) & 1u) == 0u &&
        ((peer_low ^ AF_U32(filter + 8u)) | (AF_U32(filter + 12u) ^ peer_high)) == 0u)
        return 1u;
    if (peer_type == 0u) return 0u;
    if ((peer_high & 0xc000u) != 0x4000u) return 0u;
    if ((own & 0x20u) == 0u) return 0u;
    AF_U8(out + 21u) = 0u;
    return 1u;
}
