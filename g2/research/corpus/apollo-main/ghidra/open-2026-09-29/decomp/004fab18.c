
void FUN_004fab18(void)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  uVar4 = 0;
  uVar5 = *DAT_004fac70;
  if (*DAT_004fac60 != 0) {
    uVar4 = FUN_0044e498(*DAT_004fac60);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fb13c,DAT_004fb07c,DAT_004fb138,0x11b1,DAT_004fb134,*DAT_004fb130,uVar5,
                 uVar4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_004fb140,DAT_004fb140,*DAT_004fb130,uVar5,uVar4);
  }
  iVar2 = DAT_004fac4c;
  bVar1 = *(byte *)(DAT_004fac4c + 0x2e4e);
  if (bVar1 == 1) {
    FUN_004fa314(uVar4,uVar5);
    return;
  }
  if (bVar1 != 0) {
    if (bVar1 == 3) {
      if (*(short *)(DAT_004fac4c + 0x2e48) == 0) {
        return;
      }
      FUN_004fa72c(uVar4,uVar5);
      return;
    }
    if (bVar1 < 3) {
      if (*(short *)(DAT_004fac4c + 0x2e48) == 0) {
        return;
      }
      FUN_004fa404(uVar4,uVar5);
      return;
    }
    if (bVar1 == 4) {
      if (*(short *)(DAT_004fac4c + 0x2e48) == 0) {
        return;
      }
      FUN_004faa44(uVar4,uVar5);
      return;
    }
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004fb13c,DAT_004fb07c,DAT_004fb138,0x11cb,DAT_004fb144,
                 *(undefined1 *)(iVar2 + 0x2e4e));
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x8400000,DAT_004fb148,DAT_004fb148,*(undefined1 *)(iVar2 + 0x2e4e));
  }
  return;
}

