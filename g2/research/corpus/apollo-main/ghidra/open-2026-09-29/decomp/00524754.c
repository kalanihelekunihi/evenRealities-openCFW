
uint FT_DivFix(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int local_20;
  uint local_1c;
  uint local_18 [3];
  
  iVar1 = 1;
  if ((int)param_1 < 0) {
    param_1 = -param_1;
    iVar1 = -1;
  }
  if ((int)param_2 < 0) {
    param_2 = -param_2;
    iVar1 = -iVar1;
  }
  if (param_2 == 0) {
    param_2 = 0x7fffffff;
  }
  else if (0xffff - (param_2 >> 0x11) < param_1) {
    local_1c = param_1 >> 0x10;
    local_20 = param_1 << 0x10;
    local_18[1] = 0;
    local_18[0] = param_2 >> 1;
    local_18[2] = param_4;
    FT_Add64(&local_20,local_18,&local_20);
    param_2 = ft_div64by32(local_1c,local_20,param_2);
  }
  else {
    param_2 = ((param_2 >> 1) + param_1 * 0x10000) / param_2;
  }
  if (iVar1 < 0) {
    param_2 = -param_2;
  }
  return param_2;
}

