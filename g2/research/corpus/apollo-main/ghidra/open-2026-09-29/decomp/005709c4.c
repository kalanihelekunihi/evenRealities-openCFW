
undefined4 pt_cmd_17_handler(int param_1,byte param_2,undefined1 *param_3,byte *param_4)

{
  int iVar1;
  undefined4 uVar2;
  byte bVar3;
  undefined2 local_24 [4];
  undefined2 local_1c;
  byte *pbStack_18;
  
  pbStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_00571358,0x501,DAT_00571354);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00570a14;
  }
  compress_log_output(0xc000000,DAT_0057135c,DAT_0057135c);
LAB_00570a14:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_00571358,0x504,DAT_0057105c,DAT_00571358);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00571060,DAT_00571060,DAT_00571358);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x18;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 8;
    bVar3 = 4;
    FUN_0043c0e4(local_24,10,0);
    FUN_0055b6a8(local_24);
    for (iVar1 = 0; iVar1 < 4; iVar1 = iVar1 + 1) {
      param_3[bVar3] = (char)local_24[iVar1];
      param_3[(byte)(bVar3 + 1)] = (char)((ushort)local_24[iVar1] >> 8);
      bVar3 = bVar3 + 2;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_00571358,0x517,DAT_00571360,local_24[0],
                   local_24[1],local_24[2],local_24[3],local_1c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xd400000,DAT_00571364,DAT_00571364,local_24[0],local_24[1],local_24[2],
                          local_24[3],local_1c);
    }
    *param_4 = bVar3;
    uVar2 = 0;
  }
  return uVar2;
}

