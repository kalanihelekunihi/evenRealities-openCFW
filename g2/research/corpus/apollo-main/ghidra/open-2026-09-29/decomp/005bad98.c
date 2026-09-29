
int * FUN_005bad98(float param_1,int param_2,int param_3,int *param_4,int *param_5)

{
  int iVar1;
  float fVar2;
  
  fVar2 = (float)FUN_00577d08(param_1 * DAT_005bafac);
  iVar1 = (((int)fVar2 + param_2 * 0x3c + param_3) % 0x5a0 + 0x5a0) % 0x5a0;
  if (param_4 != (int *)0x0) {
    *param_4 = iVar1 / 0x3c;
  }
  if (param_5 != (int *)0x0) {
    *param_5 = iVar1 % 0x3c;
  }
  return param_5;
}

