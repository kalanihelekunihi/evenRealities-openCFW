
undefined8 FUN_005b3570(undefined1 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  
  if (param_1 != (undefined1 *)0x0) {
    *param_1 = 1;
    puVar3 = param_1;
    iVar2 = param_2;
    iVar1 = osKernelGetTickCount();
    *(int *)(param_1 + 4) = param_2 + iVar1;
    iVar1 = FUN_0043d0ce();
    param_1 = puVar3;
    param_2 = iVar2;
    if (iVar1 << 0x1e < 0) {
      param_1 = (undefined1 *)0x66;
      param_2 = DAT_005b3e0c;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3e10,0x66,DAT_005b3e0c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__conversate_timer__s_timer_start_005b3e1c,
                          PTR_s__conversate_timer__s_timer_start_005b3e1c,param_3);
    }
  }
  return CONCAT44(param_2,param_1);
}

