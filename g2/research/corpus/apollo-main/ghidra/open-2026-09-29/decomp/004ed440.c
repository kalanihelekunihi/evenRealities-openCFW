
undefined8 FUN_004ed440(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_004ed764;
    local_10 = 0x79e;
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed768);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004ed76c,DAT_004ed76c);
  }
  *(undefined1 *)(DAT_004ed770 + 0x124) = 0;
  *DAT_004ed774 = 0;
  piVar1 = DAT_004ed778;
  if (*DAT_004ed778 != 0) {
    ui_common_api_fn_00509c96(*DAT_004ed778);
    *piVar1 = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_004ed77c;
      local_10 = 0x7a7;
      FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed768);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ed780,DAT_004ed780);
    }
  }
  for (iVar2 = 0; iVar2 < 3; iVar2 = iVar2 + 1) {
    *(undefined4 *)(DAT_004ed754 + iVar2 * 4) = 0;
  }
  *DAT_004ed748 = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_004ed784;
    local_10 = 0x7b0;
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed768);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004ed788,DAT_004ed788);
  }
  return CONCAT44(local_c,local_10);
}

