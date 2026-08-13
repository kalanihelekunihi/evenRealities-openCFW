#include <stddef.h>
#include <stdarg.h>

void WsfTrace(const char *pStr, ...)
{
  (void) pStr;
}

void attsCheckPendDbHashReadRsp(void)
{
}

void *memcpy(void *restrict dst, const void *restrict src, size_t n)
{
  unsigned char *d = dst;
  const unsigned char *s = src;
  while (n-- != 0U)
  {
    *d++ = *s++;
  }
  return dst;
}

void *memset(void *dst, int value, size_t n)
{
  unsigned char *d = dst;
  while (n-- != 0U)
  {
    *d++ = (unsigned char) value;
  }
  return dst;
}
