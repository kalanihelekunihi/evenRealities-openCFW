
void hciEvtParseRemConnParamReq(undefined2 *param_1,byte *param_2)

{
  param_1[2] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  param_1[3] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
  param_1[4] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
  param_1[5] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
  param_1[6] = (ushort)param_2[9] * 0x100 + (ushort)param_2[8];
  *param_1 = param_1[2];
  return;
}

