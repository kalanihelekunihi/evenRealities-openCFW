
uint gx8002_clock_time_us(void)

{
  uint uStack_14;
  int iStack_10;
  int iStack_c;
  undefined4 uStack_8;
  
  iStack_c = iRam00000048;
  uStack_8 = 0;
  uStack_14 = (uint)((ulonglong)uRam00000044 * 1000);
  iStack_10 = (int)((ulonglong)uRam00000044 * 1000 >> 0x20) + iRam00000048 * 1000;
  if (iStack_10 == 0) {
    uStack_14 = uStack_14 >> 10;
  }
  else {
    func_0x102098b4(&uStack_14,0x400);
  }
  return uStack_14;
}

