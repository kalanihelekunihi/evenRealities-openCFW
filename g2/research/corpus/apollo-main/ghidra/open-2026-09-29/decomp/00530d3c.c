
ulonglong HciGetLeSupFeat(void)

{
  return *(ulonglong *)(DAT_00530d68 + 0x88) & 0xfffffffffffffffd;
}

