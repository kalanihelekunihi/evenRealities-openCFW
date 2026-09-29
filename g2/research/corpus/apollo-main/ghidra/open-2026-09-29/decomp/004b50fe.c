
void attDecodeMsgParam(ushort param_1,undefined1 *param_2,char *param_3)

{
  *param_3 = (char)param_1 + (char)(param_1 / 3) * -3;
  *param_2 = (char)(param_1 / 3);
  return;
}

