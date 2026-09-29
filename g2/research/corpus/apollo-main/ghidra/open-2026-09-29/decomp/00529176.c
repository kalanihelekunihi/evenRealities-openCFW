
undefined8 ft_mem_qalloc(int param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = 0;
  if (param_2 < 1) {
    if (param_2 < 0) {
      uVar2 = 6;
    }
  }
  else {
    iVar1 = (**(code **)(param_1 + 4))(param_1);
    if (iVar1 == 0) {
      uVar2 = 0x40;
    }
  }
  *param_3 = uVar2;
  return CONCAT44(param_4,iVar1);
}

