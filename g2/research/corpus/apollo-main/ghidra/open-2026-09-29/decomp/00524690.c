
undefined8 FT_MulDiv_No_Round(int param_1,int param_2,uint param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  uint local_18;
  int local_14;
  
  iVar2 = 1;
  if (param_1 < 0) {
    param_1 = -param_1;
    iVar2 = -1;
  }
  if (param_2 < 0) {
    param_2 = -param_2;
    iVar2 = -iVar2;
  }
  uVar1 = param_3;
  if ((int)param_3 < 0) {
    uVar1 = -param_3;
    iVar2 = -iVar2;
  }
  local_18 = param_3;
  if (uVar1 == 0) {
    uVar1 = 0x7fffffff;
  }
  else if ((uint)(param_2 + param_1) < 0x20000) {
    uVar1 = (uint)(param_2 * param_1) / uVar1;
  }
  else {
    local_14 = param_4;
    ft_multo64(param_1,param_2,&local_18);
    if (local_14 == 0) {
      uVar1 = local_18 / uVar1;
    }
    else {
      uVar1 = ft_div64by32(local_14,local_18,uVar1);
    }
  }
  if (iVar2 < 0) {
    uVar1 = -uVar1;
  }
  return CONCAT44(local_18,uVar1);
}

