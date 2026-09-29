
void FT_Stream_OpenMemory(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  *param_1 = param_2;
  param_1[1] = param_3;
  param_1[2] = 0;
  param_1[8] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  return;
}

