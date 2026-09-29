
undefined8 FUN_00490616(int *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_3 != 0) && (*param_1 != 0)) {
    if (((uint)(param_3 + param_1[3]) < (uint)param_1[3]) ||
       ((uint)param_1[2] < (uint)(param_3 + param_1[3]))) {
      iVar2 = DAT_004910ac;
      if (param_1[4] != 0) {
        iVar2 = param_1[4];
      }
      param_1[4] = iVar2;
      uVar1 = 0;
      goto LAB_00490676;
    }
    iVar2 = (*(code *)*param_1)(param_1,param_2,param_3);
    if (iVar2 == 0) {
      iVar2 = DAT_004910b0;
      if (param_1[4] != 0) {
        iVar2 = param_1[4];
      }
      param_1[4] = iVar2;
      uVar1 = 0;
      goto LAB_00490676;
    }
  }
  param_1[3] = param_3 + param_1[3];
  uVar1 = 1;
LAB_00490676:
  return CONCAT44(param_4,uVar1);
}

