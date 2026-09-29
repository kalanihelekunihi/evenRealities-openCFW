
undefined4 FUN_0050a47e(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_0050aaf4;
  *DAT_0050aaf4 = param_1;
  *DAT_0050aaf0 = 1;
  if (*puVar1 < 6) {
    FUN_0050a094();
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = *puVar1;
      param_1 = 300;
      param_2 = DAT_0050af94;
      FUN_0043d574(1,DAT_0050ac28,DAT_0050ac24,DAT_0050af98,300,DAT_0050af94,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0050b03c,DAT_0050b03c,*puVar1,param_1,param_2,param_3);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

