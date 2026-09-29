
void hciEvtParseLeCisReq(undefined2 *param_1,byte *param_2)

{
  param_1[2] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  param_1[3] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
  *(byte *)(param_1 + 4) = param_2[4];
  *(byte *)((int)param_1 + 9) = param_2[5];
  *param_1 = param_1[3];
  return;
}

