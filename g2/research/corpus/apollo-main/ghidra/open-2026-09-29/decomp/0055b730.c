
undefined4 FUN_0055b730(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  iVar1 = FUN_0055b38e(DAT_0055ba00);
  if (iVar1 == 0) {
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba18,0x165,DAT_0055ba14,iVar1,in_r3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0055ba1c,DAT_0055ba1c,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

