
undefined8
SilentMode_ToggleByLocalLongPress
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  char cVar1;
  int iVar2;
  undefined *puVar3;
  int iVar4;
  int local_c;
  
  if (*DAT_00469b44 == '\0') {
    local_c = param_4;
    cVar1 = silent_mode_status_get();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      if (cVar1 == '\0') {
        puVar3 = &LAB_0046957c;
      }
      else {
        puVar3 = &DAT_00469578;
      }
      param_2 = DAT_00469b68;
      FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469b6c,0x8d,DAT_00469b68,puVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      if (cVar1 == '\0') {
        puVar3 = &LAB_0046957c;
      }
      else {
        puVar3 = &DAT_00469578;
      }
      compress_log_output(0x10400000,DAT_00469b70,DAT_00469b70,puVar3);
    }
    if (cVar1 == '\0') {
      local_c = CONCAT31(local_c._1_3_,1);
    }
    else {
      local_c = (uint)local_c._1_3_ << 8;
    }
    param_1 = 4;
    iVar2 = FUN_00464f76(0x10a,&local_c,1,0);
    if (iVar2 != 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_1 = 0x96;
        param_2 = DAT_00469b74;
        FUN_0043d574(1,DAT_00469b3c,DAT_00469b38,DAT_00469b6c,0x96,DAT_00469b74,iVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00469b78,DAT_00469b78,iVar2);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

