
undefined8 FUN_00588d74(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (*(char *)(DAT_00589350 + 0x20) == '\x02') {
    iVar2 = *(int *)(DAT_00589354 + 0x20) * 1000;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x3b;
      param_2 = DAT_00589358;
      param_3 = iVar2;
      FUN_0043d574(3,DAT_00589364,DAT_00589360,DAT_0058935c,0x3b,DAT_00589358,iVar2,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00589368,DAT_00589368,iVar2,param_1,param_2,param_3);
    }
    *DAT_0058936c = 0;
    *DAT_00589370 = 1;
    iVar1 = osKernelGetTickCount();
    *DAT_00589374 = iVar2 + iVar1;
  }
  return CONCAT44(param_2,param_1);
}

