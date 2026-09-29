
int FUN_005b9f06(int param_1,int param_2,undefined1 *param_3,int param_4)

{
  int iVar1;
  int local_18;
  
  local_18 = param_4;
  if ((param_3 != (undefined1 *)0x0) && (param_4 != 0)) {
    *param_3 = 0;
    iVar1 = FUN_0046650c();
    if ((iVar1 == 1) && (param_1 = param_1 % 0xc, param_1 == 0)) {
      param_1 = 0xc;
    }
    if (param_2 < 0) {
      param_2 = 0;
    }
    if (0x3b < param_2) {
      param_2 = 0x3b;
    }
    FUN_0044b728(param_3,param_4,PTR_s__02d__02d_005baa88,param_1);
    local_18 = param_2;
  }
  return local_18;
}

