
undefined4
PB_RxPipeRoleChange(undefined4 param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (char *)0x0) {
    FUN_00439c04(&local_20,DAT_004bc414,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004bbd9c;
      local_20 = 0xd4;
      FUN_0043d574(1,DAT_004bbda8,DAT_004bbda4,DAT_004bc4a4);
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
      local_18 = DAT_004bc4ac;
      if (*param_2 == '\x01') {
        local_18 = DAT_004bc4a8;
      }
      local_1c = DAT_004bc4b0;
      local_20 = 0xd8;
      FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bc4a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004bc4ac;
      if (*param_2 == '\x01') {
        uVar2 = DAT_004bc4a8;
      }
      compress_log_output(0x10400000,DAT_004bc5ac,DAT_004bc5ac,uVar2);
    }
    APP_BleSlaveAsCmdRole(*param_2);
    uVar2 = 0;
  }
  return uVar2;
}

