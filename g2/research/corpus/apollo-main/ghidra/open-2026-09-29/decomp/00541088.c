
undefined8
_flashDBMutexInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0054129c;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0054129c == 0) {
    iVar2 = osMutexNew(DAT_005412a0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = DAT_005412a4;
        local_10 = 0x8a;
        FUN_0043d574(1,DAT_00541268,DAT_00541264,DAT_005412a8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005412ac,DAT_005412ac);
      }
    }
  }
  return CONCAT44(local_c,local_10);
}

