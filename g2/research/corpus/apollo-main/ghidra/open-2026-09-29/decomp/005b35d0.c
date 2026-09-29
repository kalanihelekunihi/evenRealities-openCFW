
undefined8
FUN_005b35d0(undefined1 *param_1,undefined *param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  
  puVar2 = param_2;
  if (param_1 != (undefined1 *)0x0) {
    *param_1 = 0;
    *(undefined4 *)(param_1 + 4) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = (undefined1 *)0x70;
      puVar2 = PTR_s__s_timer_stop_005b3e20;
      param_3 = param_2;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_deadline_timer_stop_005b3e24,0x70,
                   PTR_s__s_timer_stop_005b3e20,param_2,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__conversate_timer__s_timer_stop_005b3e28,
                          PTR_s__conversate_timer__s_timer_stop_005b3e28,param_2,param_1,puVar2,
                          param_3);
    }
  }
  return CONCAT44(puVar2,param_1);
}

