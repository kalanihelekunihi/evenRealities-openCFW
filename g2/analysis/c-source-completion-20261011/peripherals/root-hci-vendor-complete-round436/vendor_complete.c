/* Experimental Cordio vendor command-complete provider for Apollo Main.
 * Pinned hci_vs_apollo3.c returns HCI_VENDOR_SPEC_CMD_CMPL_CBACK_EVT (18).
 * Native 0x56b310..0x56b328 selects event type 0x12 for vendor OGF.
 * The stock implementation inlines this case, so this source is a
 * behavior-qualified dependency provider, not a stock separate function.
 */
#include <stdint.h>

uint8_t hciCoreVsCmdCmplRcvd(uint16_t opcode, uint8_t *parameters, uint8_t length)
{
    (void)opcode;
    (void)parameters;
    (void)length;
    return 0x12u;
}
