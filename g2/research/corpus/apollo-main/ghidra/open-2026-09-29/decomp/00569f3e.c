
void hciEvtParseReadRemoteVerInfoCmpl(undefined2 *param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  param_1[3] = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(undefined1 *)(param_1 + 4) = param_2[3];
  param_1[5] = (ushort)(byte)param_2[5] * 0x100 + (ushort)(byte)param_2[4];
  param_1[6] = (ushort)(byte)param_2[7] * 0x100 + (ushort)(byte)param_2[6];
  *param_1 = param_1[3];
  *(undefined1 *)((int)param_1 + 3) = *(undefined1 *)(param_1 + 2);
  return;
}

