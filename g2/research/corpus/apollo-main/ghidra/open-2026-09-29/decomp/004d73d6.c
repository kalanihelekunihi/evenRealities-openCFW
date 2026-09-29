
undefined4
PB_RxNotifWhitelistCtrl(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004d7940,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004d7944;
      local_20 = 0xf5;
      FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7948);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d794c);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_18 = (uint)*param_2;
      local_1c = DAT_004d7950;
      local_20 = 0xf9;
      FUN_0043d574(4,DAT_004d7694,DAT_004d7690,DAT_004d7948);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d7954,DAT_004d7954,*param_2);
    }
    service_ancc_state_byte4_set(*param_2 != 0);
    uVar2 = 0;
  }
  return uVar2;
}

