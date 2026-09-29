
uint FUN_10005070(void)

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
    return uStack_14 >> 10;
  }
  FUN_1000c5d0(&uStack_14,0x400);
  return uStack_14;
}

