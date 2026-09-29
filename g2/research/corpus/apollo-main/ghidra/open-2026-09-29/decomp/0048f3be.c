
undefined4 FUN_0048f3be(int *param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  if (param_3 == 0) {
    uVar1 = 1;
  }
  else {
    uStack_10 = param_4;
    if ((param_2 == 0) && (*param_1 != DAT_0048fc78)) {
      for (; 0x10 < param_3; param_3 = param_3 - 0x10) {
        iVar2 = FUN_0048f3be(param_1,auStack_20,0x10);
        if (iVar2 == 0) {
          return 0;
        }
      }
      uVar1 = FUN_0048f3be(param_1,auStack_20,param_3);
    }
    else if ((uint)param_1[2] < param_3) {
      iVar2 = DAT_0048fc7c;
      if (param_1[3] != 0) {
        iVar2 = param_1[3];
      }
      param_1[3] = iVar2;
      uVar1 = 0;
    }
    else {
      iVar2 = (*(code *)*param_1)(param_1,param_2,param_3);
      if (iVar2 == 0) {
        iVar2 = DAT_0048fc80;
        if (param_1[3] != 0) {
          iVar2 = param_1[3];
        }
        param_1[3] = iVar2;
        uVar1 = 0;
      }
      else {
        if ((uint)param_1[2] < param_3) {
          param_1[2] = 0;
        }
        else {
          param_1[2] = param_1[2] - param_3;
        }
        uVar1 = 1;
      }
    }
  }
  return uVar1;
}

