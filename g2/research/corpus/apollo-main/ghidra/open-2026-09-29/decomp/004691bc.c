
undefined8
SilentMode_SetStatus(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = settings_get_config();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_00469b30;
      local_10 = 0x4c;
      FUN_0043d574(1,DAT_00469b3c,DAT_00469b38,DAT_00469b34);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00469b40,DAT_00469b40);
    }
  }
  else {
    *(bool *)(iVar1 + 0x15) = param_1 != '\0';
  }
  return CONCAT44(local_c,local_10);
}

