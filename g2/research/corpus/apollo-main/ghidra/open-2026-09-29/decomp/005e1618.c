
void FUN_005e1618(int param_1,int param_2,int param_3)

{
  byte bVar1;
  
  if (param_2 < *(int *)(param_1 + 0x88)) {
    param_2 = *(int *)(param_1 + 0x88) + -1;
  }
  if ((*(int *)(param_1 + 0xa0) == 0) &&
     ((*(int *)(param_1 + 0x98) != 0 || (*(int *)(param_1 + 0x9c) != 0)))) {
    FUN_005e1594(param_1);
  }
  *(undefined4 *)(param_1 + 0x98) = 0;
  *(undefined4 *)(param_1 + 0x9c) = 0;
  *(int *)(param_1 + 0x80) = param_2;
  *(int *)(param_1 + 0x84) = param_3;
  if (((param_3 < *(int *)(param_1 + 0x94)) && (*(int *)(param_1 + 0x90) <= param_3)) &&
     (param_2 < *(int *)(param_1 + 0x8c))) {
    bVar1 = 0;
  }
  else {
    bVar1 = 1;
  }
  *(uint *)(param_1 + 0xa0) = (uint)bVar1;
  return;
}

