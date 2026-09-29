
undefined4 FUN_00441ed8(uint *param_1,undefined4 param_2,int param_3)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  uVar1 = param_1[0xe];
  if (param_1[0x10] == 0) {
    if (*param_1 == 0) {
      uVar2 = FUN_0045596e(param_1[2]);
      param_1[2] = 0;
    }
  }
  else if (param_3 == 0) {
    FUN_00439be4(param_1[1],param_2,param_1[0x10]);
    param_1[1] = param_1[1] + param_1[0x10];
    if (param_1[2] <= param_1[1]) {
      param_1[1] = *param_1;
    }
  }
  else {
    FUN_00439be4(param_1[3],param_2,param_1[0x10]);
    param_1[3] = param_1[3] - param_1[0x10];
    if (param_1[3] < *param_1) {
      param_1[3] = param_1[2] - param_1[0x10];
    }
    if ((param_3 == 2) && (uVar1 != 0)) {
      uVar1 = uVar1 - 1;
    }
  }
  param_1[0xe] = uVar1 + 1;
  return uVar2;
}

