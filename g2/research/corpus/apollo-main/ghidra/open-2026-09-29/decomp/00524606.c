
uint FT_MulDiv(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint local_20;
  int local_1c;
  uint local_18;
  undefined4 local_14;
  
  iVar3 = 1;
  uVar4 = param_1;
  if ((int)param_1 < 0) {
    uVar4 = -param_1;
    iVar3 = -1;
  }
  iVar2 = param_2;
  if (param_2 < 0) {
    iVar2 = -param_2;
    iVar3 = -iVar3;
  }
  uVar1 = param_3;
  if ((int)param_3 < 0) {
    uVar1 = -param_3;
    iVar3 = -iVar3;
  }
  if (uVar1 == 0) {
    uVar1 = 0x7fffffff;
  }
  else if (DAT_00524f0c - (uVar1 >> 0x11) < iVar2 + uVar4) {
    local_20 = param_1;
    local_1c = param_2;
    local_18 = param_3;
    local_14 = param_4;
    ft_multo64(uVar4,iVar2,&local_20);
    local_14 = 0;
    local_18 = uVar1 >> 1;
    FT_Add64(&local_20,&local_18,&local_20);
    if (local_1c == 0) {
      uVar1 = local_20 / uVar1;
    }
    else {
      uVar1 = ft_div64by32(local_1c,local_20,uVar1);
    }
  }
  else {
    uVar1 = (iVar2 * uVar4 + (uVar1 >> 1)) / uVar1;
  }
  if (iVar3 < 0) {
    uVar1 = -uVar1;
  }
  return uVar1;
}

