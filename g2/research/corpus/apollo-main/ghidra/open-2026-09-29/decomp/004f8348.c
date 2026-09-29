
void FUN_004f8348(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  
  uVar1 = FUN_004f6770();
  iVar3 = DAT_004f8fc4;
  if (*(short *)(DAT_004f8fc4 + 0x280) == 0) {
    return;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004f8918,DAT_004f8914,DAT_004f8fcc,0xc0d,DAT_004f8fc8,
                 *(undefined2 *)(iVar3 + 0x280),uVar1,in_r3);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_004f8fd0,DAT_004f8fd0,*(undefined2 *)(iVar3 + 0x280),uVar1);
  }
  iVar2 = FUN_004f6328();
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f8918,DAT_004f8914,DAT_004f8fcc,0xc13,DAT_004f8fd4,
                   *(undefined2 *)(iVar3 + 0x280));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f8fd8,DAT_004f8fd8,*(undefined2 *)(iVar3 + 0x280));
    }
    FUN_004f84cc();
    return;
  }
  if (iVar2 == -2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f8918,DAT_004f8914,DAT_004f8fcc,0xc18,DAT_004f8fdc,
                   *(undefined2 *)(iVar3 + 0x280));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f8fe0,DAT_004f8fe0,*(undefined2 *)(iVar3 + 0x280));
    }
    FUN_004f84cc();
    return;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(1,DAT_004f8918,DAT_004f8914,DAT_004f8fcc,0xc1e,DAT_004f8fe4,iVar2);
  }
  iVar3 = FUN_0043d0ce();
  if ((-1 < iVar3 << 0x1f) && (iVar3 = FUN_0043d0ce(), -1 < iVar3 << 0x1d)) {
    return;
  }
  compress_log_output(0x4400000,DAT_004f8fe8,DAT_004f8fe8,iVar2);
  return;
}

