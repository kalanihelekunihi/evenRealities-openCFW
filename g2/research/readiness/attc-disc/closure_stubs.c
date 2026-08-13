#include <stddef.h>
#include <stdint.h>

const uint8_t attChUuid[16] = {0};
const uint8_t attIncUuid[16] = {0};

void AttcFindByTypeValueReq(uint8_t connId, uint16_t start, uint16_t end,
                            uint16_t uuid, uint16_t valueLen, uint8_t *value)
{
  (void) connId; (void) start; (void) end; (void) uuid; (void) valueLen; (void) value;
}

void AttcFindInfoReq(uint8_t connId, uint16_t start, uint16_t end)
{
  (void) connId; (void) start; (void) end;
}

void AttcReadByTypeReq(uint8_t connId, uint16_t start, uint16_t end,
                       uint8_t uuidLen, uint8_t *uuid)
{
  (void) connId; (void) start; (void) end; (void) uuidLen; (void) uuid;
}

void AttcReadReq(uint8_t connId, uint16_t handle)
{
  (void) connId; (void) handle;
}

void AttcWriteReq(uint8_t connId, uint16_t handle, uint16_t length, uint8_t *value)
{
  (void) connId; (void) handle; (void) length; (void) value;
}

void WsfTrace(const char *format, ...)
{
  (void) format;
}

uint8_t attUuidCmp16to128(const uint8_t *uuid16, const uint8_t *uuid128)
{
  (void) uuid16; (void) uuid128;
  return 0;
}

int memcmp(const void *a, const void *b, size_t n)
{
  const unsigned char *left = a;
  const unsigned char *right = b;
  while (n-- != 0U)
  {
    if (*left != *right)
    {
      return (int) *left - (int) *right;
    }
    ++left; ++right;
  }
  return 0;
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
