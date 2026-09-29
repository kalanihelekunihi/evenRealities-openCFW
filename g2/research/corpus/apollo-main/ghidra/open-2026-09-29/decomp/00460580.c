
undefined8 FUN_00460580(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_00460fb0;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_00460fb0 != 1) goto LAB_00460618;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_00461034;
    local_10 = 0x158;
    FUN_0043d574(3,DAT_0046062c,DAT_00460628,DAT_00461038);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004605be:
    compress_log_output(0xc000000,DAT_0046103c,DAT_0046103c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004605be;
  }
  iVar2 = SVC_KvdbWriteMenuConfigureValue();
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_00461040;
      local_10 = 0x15b;
      FUN_0043d574(1,DAT_0046062c,DAT_00460628,DAT_00461038);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004611b0);
    }
  }
  *piVar1 = 0;
LAB_00460618:
  return CONCAT44(local_c,local_10);
}

