
uint Cy_SCB_WriteArray(uint *param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  
  if ((*param_1 & 0xc000) == 0) {
    iVar1 = 0x10;
  }
  else {
    iVar1 = 8;
  }
  uVar2 = iVar1 - (param_1[0x82] & 0x1ff);
  if (uVar2 <= param_3) {
    param_3 = uVar2;
  }
  Cy_SCB_WriteArrayNoCheck(param_1,param_2,param_3);
  return param_3;
}

