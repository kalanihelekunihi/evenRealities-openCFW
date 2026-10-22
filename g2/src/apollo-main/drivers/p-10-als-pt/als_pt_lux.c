/* Product-test raw ambient-light reading, native 0x58f8e4..0x58f921, used by the
 * pt_protocol_procsr handlers at 0x57200c and 0x5738d0 (stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c).
 *
 * Only when the service state byte (0x45a570) is 1 is the OPT3007 result
 * register 0x00 read: raw = mantissa[11:0] << exponent[15:12] in 0.01 lux. Any
 * other state returns -1.0. The value returns in D0 (IAR VFP convention); compile
 * with a double-precision FPU (profile g2-apollo-main-20). */
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))
#define OPT3007_RESULT_REGISTER 0u
#define SERVICE_STATE_ACTIVE 1u

extern uint32_t audio_uart_service_mode(void); /* 0x45a570, service state byte */
extern uint16_t opt3007_register_read_513748(uint8_t reg);

IAR_VFP double pt_als_raw_lux_get_58f8e4(void)
{
    double lux = -1.0;
    if ((uint8_t)audio_uart_service_mode() == SERVICE_STATE_ACTIVE) {
        uint32_t result = opt3007_register_read_513748(OPT3007_RESULT_REGISTER);
        uint32_t mantissa = (uint16_t)(result & 0xfffu);
        int32_t raw = (int32_t)((1u << ((uint16_t)result >> 12)) * mantissa);
        lux = (double)raw;
    }
    return lux;
}
