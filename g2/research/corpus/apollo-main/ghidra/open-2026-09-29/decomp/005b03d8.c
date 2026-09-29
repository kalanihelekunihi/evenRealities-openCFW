
void FUN_005b03d8(void)

{
  int iVar1;
  uint uVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0045a568();
  if (iVar1 != 1) {
    return;
  }
  iVar1 = osKernelGetTickCount();
  uVar2 = iVar1 - *DAT_005b0a38;
  if (60000 < uVar2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b09f4,DAT_005b09f0,DAT_005b0a40,0xa0,DAT_005b0a3c,uVar2,60000);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005b0a44,DAT_005b0a44,uVar2,60000);
    }
    FUN_005b03c2();
    local_10 = *DAT_005b0a48;
    uStack_c = DAT_005b0a48[1];
    FUN_0048eb32(DAT_005b0a4c,2,&local_10);
    FUN_005b02e4(0x13,1);
    return;
  }
  return;
}

