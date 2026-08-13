#include <stddef.h>
#include <stdint.h>
unsigned char dmCb[2048];
void BdaCpy(uint8_t *dst, const uint8_t *src) { (void)dst; (void)src; }
uint8_t *DmFindAdType(uint8_t type, uint16_t len, uint8_t *data) { (void)type; (void)len; return data; }
void *WsfMsgAlloc(uint16_t len) { (void)len; return 0; }
void WsfMsgSend(uint8_t id, void *msg) { (void)id; (void)msg; }
void WsfTaskLock(void) {}
void WsfTaskUnlock(void) {}
void dmDevPassHciEvtToConn(void *evt) { (void)evt; }
void *memcpy(void *d, const void *s, size_t n) { (void)s; (void)n; return d; }
void *memmove(void *d, const void *s, size_t n) { (void)s; (void)n; return d; }
void *memset(void *d, int c, size_t n) { (void)c; (void)n; return d; }
