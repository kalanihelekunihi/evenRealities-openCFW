
undefined4 SmpDbInit(void)

{
  int iVar1;
  undefined4 in_r3;
  
  iVar1 = DAT_005429f4;
  if (*(char *)(DAT_005429f4 + 0xfd) == '\x01') {
    WsfTimerStop(DAT_005429f4 + 0xf0);
  }
  FUN_0043c0e4(iVar1,0x100,0);
  *(undefined1 *)(iVar1 + 0xfc) = *(undefined1 *)(DAT_00542a14 + 0xec);
  *(undefined1 *)(iVar1 + 0xfa) = 0x20;
  return in_r3;
}

