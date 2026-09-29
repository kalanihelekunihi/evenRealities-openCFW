
undefined4 FUN_004727aa(int param_1,ushort param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else if (param_2 < 6) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00472bbc,DAT_00472bb8,DAT_00472c0c,0x22b,DAT_00472c08,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00472c10,DAT_00472c10,param_2);
    }
    uVar1 = 0xffffffff;
  }
  else {
    local_10 = 0x20004;
    local_c = CONCAT22((short)((uint)*(undefined4 *)(DAT_00472c14 + 4) >> 0x10),
                       *(undefined2 *)(param_1 + 4));
    device_mgr_fn_004c659a(&local_10);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472c0c,0x237,DAT_00472c18,local_c & 0xff,
                   local_c >> 8 & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_00472c1c,DAT_00472c1c,local_c & 0xff,local_c >> 8 & 0xff);
    }
    uVar1 = 0;
  }
  return uVar1;
}

