
int ft_mem_qrealloc(int param_1,int param_2,int param_3,int param_4,int param_5,undefined4 *param_6)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = param_5;
  if (((param_3 < 0) || (param_4 < 0)) || (param_2 < 0)) {
    uVar2 = 6;
  }
  else if ((param_4 == 0) || (param_2 == 0)) {
    ft_mem_free(param_1,param_5);
    iVar1 = 0;
  }
  else if (0x7fffffff / param_2 < param_4) {
    uVar2 = 10;
  }
  else if (param_3 == 0) {
    iVar1 = (**(code **)(param_1 + 4))(param_1,param_2 * param_4);
    if (iVar1 == 0) {
      uVar2 = 0x40;
    }
  }
  else {
    iVar1 = (**(code **)(param_1 + 0xc))(param_1,param_2 * param_3,param_2 * param_4,param_5);
    if (iVar1 == 0) {
      uVar2 = 0x40;
      iVar1 = param_5;
    }
  }
  *param_6 = uVar2;
  return iVar1;
}

