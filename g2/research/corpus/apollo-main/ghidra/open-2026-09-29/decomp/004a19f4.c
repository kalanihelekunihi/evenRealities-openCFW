
undefined8 APP_MasterHanderInit(undefined1 param_1,int param_2,undefined4 param_3)

{
  int *piVar1;
  int *piVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 local_18;
  undefined4 local_14;
  
  *DAT_004a2380 = DAT_004a237c;
  piVar1 = DAT_004a1b54;
  *DAT_004a1b54 = param_2;
  *DAT_004a2384 = param_3;
  _SetRingLinkState(0,DAT_004a2388);
  *DAT_004a238c = *piVar1;
  piVar2 = DAT_004a2390;
  *DAT_004a2390 = *piVar1 + 4;
  APP_BleRingHandlerInit(param_1,*piVar2);
  iVar4 = FUN_0045a568();
  if (iVar4 == 1) {
    uVar3 = APP_MasterRingMacIsSet();
    UX_SendBLEStatusReply(uVar3);
  }
  iVar4 = central_is_ring_owner_side_004a2914();
  local_18 = param_2;
  local_14 = param_3;
  if (iVar4 != 0) {
    iVar4 = APP_MasterRingMacIsSet();
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_14 = DAT_004a23a4;
        local_18 = 0x3f4;
        FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a2398);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a26b8,DAT_004a26b8);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_14 = DAT_004a2394;
        local_18 = 0x3f1;
        FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a2398);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a239c,DAT_004a239c);
      }
      fw_event_loop_push_delayed(DAT_004a23a0,0,15000);
    }
  }
  return CONCAT44(local_14,local_18);
}

