
void FUN_00589cca(void)

{
  int iVar1;
  uint uVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0045a568();
  if (iVar1 != 1) {
    return;
  }
  if (*(char *)(DAT_0058a368 + 0x3c) == '\0') {
    iVar1 = osKernelGetTickCount();
    uVar2 = iVar1 - *DAT_0058a364;
    if (20000 < uVar2) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0058a320,DAT_0058a31c,DAT_0058a370,0xb2,DAT_0058a36c,uVar2,20000);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_0058a374,DAT_0058a374,uVar2,20000);
      }
      FUN_00589cb4();
      local_10 = *DAT_0058a378;
      uStack_c = DAT_0058a378[1];
      FUN_0048eb32(DAT_0058a37c,2,&local_10);
      FUN_00589b68(9,1);
      return;
    }
    return;
  }
  return;
}

