
undefined8
teleprompt_preload_timer_ensure_created
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  piVar1 = DAT_0058b358;
  if (*DAT_0058b358 == 0) {
    iVar3 = osTimerNew(0x58b059,0,0,DAT_0058b35c,param_3,param_4);
    *piVar1 = iVar3;
    if (*piVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x70;
        FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b364,0x70,DAT_0058b360);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058b368);
      }
      uVar2 = 0xffffffff;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x73;
        FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058b364,0x73,DAT_0058b36c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0058b52c);
      }
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

