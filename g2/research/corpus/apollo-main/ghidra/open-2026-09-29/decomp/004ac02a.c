
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004ac02a(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004aca98;
  if (*DAT_004aca98 == 0) {
    iVar2 = osTimerNew(_DAT_004acaa8,0,0,_DAT_004aca9c,param_3,param_4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0xbb;
        param_4 = _DAT_004acabc;
        FUN_0043d574(1,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acac8,0xbb,_DAT_004acabc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_004acacc);
      }
    }
  }
  piVar1 = _DAT_004acb08;
  if (*_DAT_004acb08 == 0) {
    iVar2 = osTimerNew(PTR_LAB_004ac020_1_004acb10,0,0,PTR_DAT_004acb0c,param_3,param_4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0xc5;
        FUN_0043d574(1,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acac8,0xc5,
                     PTR_s_Failed_to_create_ring_reconnect_t_004acb14);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__box_detect_Failed_to_create_rin_004acb18);
      }
    }
  }
  return (ulonglong)param_3 << 0x20;
}

