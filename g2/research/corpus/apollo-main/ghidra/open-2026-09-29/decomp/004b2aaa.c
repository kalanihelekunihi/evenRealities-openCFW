
undefined4 appSlaveNextLegAdvState(void)

{
  int iVar1;
  char cVar2;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004b2dc8;
  *(char *)(DAT_004b2dc8 + 0x57) = *(char *)(DAT_004b2dc8 + 0x57) + '\x01';
  if (*(byte *)(iVar1 + 0x57) < 3) {
    cVar2 = FUN_004bac4e(0);
    if (cVar2 == '\0') {
      appSlaveLegAdvStart();
    }
    else if (*DAT_004b2dd0 == '\0') {
      *DAT_004b2dd0 = '\x01';
      iVar1 = DAT_004b2dd4;
      *(undefined1 *)(DAT_004b2dd4 + 10) = 0x22;
      *(undefined2 *)(iVar1 + 8) = 0;
      *(undefined1 *)(iVar1 + 0xc) = *DAT_004b2dd8;
      WsfTimerStartMs(iVar1,200);
    }
  }
  return unaff_r7;
}

