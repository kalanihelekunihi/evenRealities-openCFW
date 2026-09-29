
void L2cDataReq(undefined2 param_1,undefined2 param_2,ushort param_3,undefined1 *param_4)

{
  *param_4 = (char)param_2;
  param_4[1] = (char)((ushort)param_2 >> 8);
  param_4[2] = (char)param_3 + '\x04';
  param_4[3] = (char)(param_3 + 4 >> 8);
  param_4[4] = (char)param_3;
  param_4[5] = (char)(param_3 >> 8);
  param_4[6] = (char)param_1;
  param_4[7] = (char)((ushort)param_1 >> 8);
  HciSendAclData(param_4);
  return;
}

