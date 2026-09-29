
void hciEvtParseLeLtkReq(undefined2 *param_1,byte *param_2)

{
  param_1[2] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  FUN_00439be4(param_1 + 3,param_2 + 2,8);
  param_1[7] = (ushort)param_2[0xb] * 0x100 + (ushort)param_2[10];
  *param_1 = param_1[2];
  return;
}

