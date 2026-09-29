
short semantic_TouchFrameChecksum16(int param_1,int param_2)

{
  ushort uVar1;
  
  uVar1 = 0;
  param_2 = param_2 + 4;
  while (param_2 != 0) {
    param_2 = param_2 + -1;
    uVar1 = uVar1 + *(byte *)(param_1 + param_2);
  }
  return ~uVar1 + 1;
}

