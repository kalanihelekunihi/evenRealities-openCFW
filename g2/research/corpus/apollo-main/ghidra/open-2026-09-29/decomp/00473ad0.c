
undefined8 FUN_00473ad0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_00474484;
  iVar2 = osTimerNew(0x473b55,1,0,DAT_00474488);
  *piVar1 = iVar2;
  local_10 = param_3;
  local_c = param_4;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_0047448c;
      local_10 = 0x9f;
      FUN_0043d574(1,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_00474490);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00474494);
    }
  }
  return CONCAT44(local_c,local_10);
}

