#include <stddef.h>
#include <stdint.h>

unsigned char attsCb[512];
static unsigned char buffer_pool[512];

uint8_t DmConnSecLevel(uint8_t connId)
{
  (void) connId;
  return 0;
}

void WsfAssert(const char *file, uint16_t line)
{
  (void) file;
  (void) line;
}

void *WsfBufAlloc(uint16_t length)
{
  (void) length;
  return buffer_pool;
}

void WsfBufFree(void *buffer)
{
  (void) buffer;
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
