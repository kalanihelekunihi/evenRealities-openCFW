
undefined8 INP_HardwareInit(undefined4 param_1,undefined4 param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 local_14;
  uint local_10;
  uint local_c;
  
  local_18 = param_1;
  local_14 = param_2;
  local_10 = param_3;
  local_c = param_4;
  FUN_0043c0e4(&local_c,2,0);
  DRV_BuzzerInit();
  FUN_0055b66a();
  TouchUpdateFirmwareCheck(0);
  iVar1 = FUN_0055b92a(&local_c);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_10 = local_c & 0xffff;
      local_14 = DAT_005134ec;
      local_18 = 0x89;
      FUN_0043d574(3,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_005134f0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_005134f4,DAT_005134f4,local_c & 0xffff);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = DAT_005134f8;
      local_18 = 0x8b;
      FUN_0043d574(2,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_005134f0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005134fc);
    }
  }
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    local_18 = 0;
    FUN_0055b6dc(&local_18);
  }
  return CONCAT44(local_14,local_18);
}

