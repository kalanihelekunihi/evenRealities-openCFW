
void hciEvtParseAuthTimeoutExpiredEvt(undefined2 *param_1,byte *param_2)

{
  param_1[2] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  *param_1 = param_1[2];
  return;
}

