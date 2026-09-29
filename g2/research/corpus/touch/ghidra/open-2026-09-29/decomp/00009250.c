
uint Cy_SCB_ReadArray(int param_1,undefined4 param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 0x308) & 0x1ff;
  if (uVar1 <= param_3) {
    param_3 = uVar1;
  }
  Cy_SCB_ReadArrayNoCheck(param_1,param_2,param_3);
  return param_3;
}

