
undefined8 FUN_0052fc04(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0052ff68;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0052ff68 != 0) {
    file_heap_free(*DAT_0052ff68);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_00530024;
      local_10 = 0x162;
      FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_00530028);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053002c,DAT_0053002c);
    }
    *piVar1 = 0;
    *DAT_0052ff64 = 0;
  }
  FUN_0043c0e4(DAT_0052ffc0,0x40,0);
  FUN_0043c0e4(DAT_0052ffe0,0x30,0);
  *DAT_0052ffd8 = 0;
  *DAT_0052fffc = 0;
  *DAT_00530000 = 0;
  *DAT_0052ffdc = 0;
  *DAT_0053000c = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_00530030;
    local_10 = 0x177;
    FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_00530028);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00530034,DAT_00530034);
  }
  return CONCAT44(local_c,local_10);
}

