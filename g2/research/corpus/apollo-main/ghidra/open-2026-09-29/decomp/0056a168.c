
void hciEvtParseRemConnParamRepCmdCmpl(undefined2 *param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  param_1[3] = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(undefined1 *)((int)param_1 + 3) = *(undefined1 *)(param_1 + 2);
  *param_1 = param_1[3];
  return;
}

