
undefined8 HUB_Open(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  uint local_c;
  
  local_10 = param_3;
  local_c = param_4;
  iVar1 = hub_role_get();
  if (iVar1 == 2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_004a73b4;
      local_10 = 0x187;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,DAT_004a73b8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a73bc,DAT_004a73bc);
    }
    uVar2 = 0xffffffff;
  }
  else {
    local_10 = CONCAT22((short)((uint)*DAT_004a73c0 >> 0x10),5);
    local_c = param_1 & 0xff;
    HUB_SendMessage(&local_10);
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

