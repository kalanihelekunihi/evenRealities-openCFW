
void hciEvtParseReadTxPwrLvlCmdCmpl(ushort *param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  *(undefined1 *)((int)param_1 + 5) = param_2[1];
  *(undefined1 *)(param_1 + 3) = param_2[3];
  *param_1 = (ushort)*(byte *)((int)param_1 + 5);
  *(char *)((int)param_1 + 3) = (char)param_1[2];
  return;
}

