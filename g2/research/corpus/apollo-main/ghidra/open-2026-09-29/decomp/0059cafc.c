
undefined4
mspi_transfer_build(undefined1 *param_1,undefined4 *param_2,undefined1 param_3,undefined4 param_4)

{
  if ((param_1 != (undefined1 *)0x0) && (param_2 != (undefined4 *)0x0)) {
    FUN_0043c0e4(param_2,0x18,0);
    *param_2 = *(undefined4 *)(param_1 + 0xc);
    *(undefined1 *)(param_2 + 4) = param_1[0x10];
    param_2[5] = *(undefined4 *)(param_1 + 0x14);
    *(undefined1 *)((int)param_2 + 5) = 0;
    *(undefined1 *)((int)param_2 + 0x11) = 0;
    *(undefined1 *)((int)param_2 + 6) = param_3;
    *(undefined1 *)((int)param_2 + 7) = *param_1;
    param_2[2] = *(undefined4 *)(param_1 + 4);
    *(undefined1 *)(param_2 + 3) = param_1[8];
    *(ushort *)((int)param_2 + 0xe) = (ushort)(byte)param_1[9];
  }
  return param_4;
}

