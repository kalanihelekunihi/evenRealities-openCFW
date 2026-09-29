
undefined4 PB_RxSecAuth(undefined4 param_1,byte *param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004bbd98,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004bbd9c;
      local_20 = 0x40;
      FUN_0043d574(1,DAT_004bbda8,DAT_004bbda4,DAT_004bbda0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bbdac);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_18 = (uint)*param_2;
      local_1c = DAT_004bbdb0;
      local_20 = 0x44;
      FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bbda0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004bbdb4,DAT_004bbdb4,*param_2);
    }
    uVar2 = DAT_004bbdb8;
    if (*param_2 != 0) {
      fw_event_loop_remove_delayed(DAT_004bbdb8);
      fw_event_loop_push_delayed(uVar2,1,500);
    }
    FUN_004b8140(param_2[1]);
    fw_event_loop_remove_delayed(DAT_004bbf2c);
    if (*DAT_004bc188 == '\0') {
      pairMgrSecAuthFlagSet(1);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_1c = DAT_004bbf94;
        local_20 = 0x55;
        FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bbda0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bc18c,DAT_004bc18c);
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_1c = DAT_004bbf30;
        local_20 = 0x4f;
        FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bbda0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bbf34,DAT_004bbf34);
      }
      fw_event_loop_remove_delayed(&LAB_004bb92c_1);
      fw_event_loop_push_delayed(&LAB_004bb92c_1,1,100);
      fw_event_loop_push_delayed(&LAB_004bb92c_1,1,2000);
    }
    uVar2 = 0;
  }
  return uVar2;
}

