
void FUN_0059ed1c(void)

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
  uVar2 = iVar1 - *DAT_0059f458;
  if (20000 < uVar2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059f414,DAT_0059f410,DAT_0059f460,0xa4,DAT_0059f45c,uVar2,20000);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0059f464,DAT_0059f464,uVar2,20000);
    }
    FUN_0059ed06();
    local_10 = *DAT_0059f468;
    uStack_c = DAT_0059f468[1];
    FUN_0048eb32(DAT_0059f46c,2,&local_10);
    FUN_0059ec28(7,1);
    return;
  }
  return;
}

