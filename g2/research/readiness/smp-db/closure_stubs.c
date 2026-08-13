#include <stddef.h>
#include <stdint.h>

void *pSmpCfg;
unsigned char smpCb[256];

uint8_t BdaCmp(const uint8_t *a, const uint8_t *b)
{
  (void) a;
  (void) b;
  return 0;
}

void BdaCpy(uint8_t *dst, const uint8_t *src)
{
  (void) dst;
  (void) src;
}

uint8_t *DmConnPeerAddr(uint8_t connId)
{
  (void) connId;
  return 0;
}

uint8_t DmConnPeerAddrType(uint8_t connId)
{
  (void) connId;
  return 0;
}

uint8_t DmHostAddrType(uint8_t addrType)
{
  return addrType;
}

void WsfTimerStartMs(void *timer, uint32_t ms)
{
  (void) timer;
  (void) ms;
}

void WsfTimerStop(void *timer)
{
  (void) timer;
}

void WsfTrace(const char *format, ...)
{
  (void) format;
}

void *memset(void *dst, int value, size_t n)
{
  unsigned char *out = dst;
  while (n-- != 0U)
  {
    *out++ = (unsigned char) value;
  }
  return dst;
}
