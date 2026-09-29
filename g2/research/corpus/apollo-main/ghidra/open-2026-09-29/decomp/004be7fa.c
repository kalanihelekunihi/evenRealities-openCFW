
undefined8
APP_BleNusHandlerInit(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_004be9d4;
    local_10 = 0xa6;
    FUN_0043d574(4,DAT_004be9c4,DAT_004be9c0,DAT_004be9d8);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004be9dc,DAT_004be9dc);
  }
  puVar1 = DAT_004be9cc;
  DAT_004be9cc[1] = param_1;
  *puVar1 = 0;
  puVar1[2] = 0;
  puVar1[3] = 0;
  return CONCAT44(local_c,local_10);
}

