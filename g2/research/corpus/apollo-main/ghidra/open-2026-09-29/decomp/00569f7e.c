
undefined4
hciEvtParseReadLeRemoteFeatCmpl
          (undefined2 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  param_1[3] = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  FUN_00439be4(param_1 + 4,param_2 + 3,8);
  *param_1 = param_1[3];
  *(undefined1 *)((int)param_1 + 3) = *(undefined1 *)(param_1 + 2);
  return param_4;
}

