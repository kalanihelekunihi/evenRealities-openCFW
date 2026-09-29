
undefined8 FUN_00545c5a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_0043c0e4(DAT_00545cec,DAT_00545ce8,0);
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_00546618;
    local_10 = 0x206;
    FUN_0043d574(4,DAT_00545cc8,DAT_00545cc4,DAT_0054661c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_005467dc);
  }
  return CONCAT44(local_c,local_10);
}

