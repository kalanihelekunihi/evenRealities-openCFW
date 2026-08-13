#include <stdint.h>

unsigned char dmAdvCb[1024];
unsigned char dmCb[1024];
unsigned char dmDevCb[1024];
unsigned char dmFcnIfTbl[256];

void BdaCpy(uint8_t *dst, const uint8_t *src) { (void) dst; (void) src; }
uint8_t DmLlAddrType(uint8_t type) { return type; }
void HciLeSetAdvDataCmd(uint8_t len, uint8_t *data) { (void) len; (void) data; }
void HciLeSetAdvEnableCmd(uint8_t enable) { (void) enable; }
void HciLeSetAdvParamCmd(uint16_t min, uint16_t max, uint8_t type, uint8_t ownType,
                         uint8_t peerType, uint8_t *peer, uint8_t channels, uint8_t filter)
{
  (void) min; (void) max; (void) type; (void) ownType; (void) peerType;
  (void) peer; (void) channels; (void) filter;
}
void HciLeSetScanRespDataCmd(uint8_t len, uint8_t *data) { (void) len; (void) data; }
void HciVsInit(uint8_t param) { (void) param; }
void WsfAssert(const char *file, uint16_t line) { (void) file; (void) line; }
void WsfTaskLock(void) {}
void WsfTaskUnlock(void) {}
void WsfTimerStartMs(void *timer, uint32_t ms) { (void) timer; (void) ms; }
void WsfTimerStop(void *timer) { (void) timer; }
void WsfTrace(const char *format, ...) { (void) format; }
void dmAdvGenConnCmpl(uint8_t status) { (void) status; }
void dmAdvInit(void) {}
void dmDevPassEvtToDevPriv(void *event) { (void) event; }
