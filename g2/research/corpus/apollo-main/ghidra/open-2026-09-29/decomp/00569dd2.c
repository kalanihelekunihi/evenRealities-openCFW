
undefined4
hciEvtParseLeEnhancedConnCmpl
          (undefined2 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  param_1[3] = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(undefined1 *)(param_1 + 4) = param_2[3];
  *(undefined1 *)((int)param_1 + 9) = param_2[4];
  FUN_004d293c(param_1 + 5,param_2 + 5);
  FUN_004d293c((int)param_1 + 0x17,param_2 + 0xb);
  FUN_004d293c((int)param_1 + 0x1d,param_2 + 0x11);
  param_1[8] = (ushort)(byte)param_2[0x18] * 0x100 + (ushort)(byte)param_2[0x17];
  param_1[9] = (ushort)(byte)param_2[0x1a] * 0x100 + (ushort)(byte)param_2[0x19];
  param_1[10] = (ushort)(byte)param_2[0x1c] * 0x100 + (ushort)(byte)param_2[0x1b];
  *(undefined1 *)(param_1 + 0xb) = param_2[0x1d];
  *param_1 = param_1[3];
  *(undefined1 *)((int)param_1 + 3) = *(undefined1 *)(param_1 + 2);
  return param_4;
}

