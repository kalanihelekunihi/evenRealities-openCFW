
void notify_silent_mode_to_app
               (byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_74 [8];
  undefined2 local_6c;
  undefined2 local_68;
  uint local_64;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  FUN_0048949c(local_74,0x68);
  local_74[0] = 3;
  local_6c = 5;
  local_68 = 2;
  local_64 = (uint)param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0049c02c,DAT_0049c028,DAT_0049c068,0x1bd,DAT_0049c064,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0049c06c,DAT_0049c06c,param_1);
  }
  setting_notify_common(local_74);
  return;
}

