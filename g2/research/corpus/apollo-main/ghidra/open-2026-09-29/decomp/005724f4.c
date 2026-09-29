
undefined4 pt_cmd_30_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined2 local_24;
  undefined2 local_22;
  undefined2 local_20;
  undefined2 local_1e;
  undefined2 local_1c;
  undefined1 *puStack_18;
  
  puStack_18 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00573028,0x77d,DAT_00573024);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0057302c,DAT_0057302c);
  }
  if ((((param_3 != (undefined1 *)0x0) && (param_4 != (undefined1 *)0x0)) && (param_1 != 0)) &&
     (3 < param_2)) {
    *param_3 = 0x42;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 3;
    uVar1 = FUN_00502dae();
    param_3[4] = uVar1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar1 = FUN_00502dae();
      FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00573028,0x78c,DAT_00573030,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar1 = FUN_00502dae();
      compress_log_output(0xc400000,DAT_00573034,DAT_00573034,uVar1);
    }
    FUN_0043c0e4(&local_24,10,0);
    FUN_0055b6a8(&local_24);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00573028,0x790,DAT_00573038,local_24,local_22,
                   local_20,local_1e,local_1c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xd400000,DAT_005732fc,DAT_005732fc,local_24,local_22,local_20,local_1e,
                          local_1c);
    }
    param_3[5] = (char)local_1c;
    param_3[6] = (char)((ushort)local_1c >> 8);
    *param_4 = 7;
    return 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_00573028,0x780,DAT_005726ec,DAT_00573028);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4400000,DAT_00572850,DAT_00572850,DAT_00573028);
  }
  return 0xffffffff;
}

