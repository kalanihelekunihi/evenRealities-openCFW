
undefined8 FT_Stream_ReadAt(int *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if (param_2 < (uint)param_1[1]) {
    if (param_1[5] == 0) {
      uVar1 = param_1[1] - param_2;
      if (param_4 < param_1[1] - param_2) {
        uVar1 = param_4;
      }
      FUN_00439be4(param_3,*param_1 + param_2,uVar1);
    }
    else {
      uVar1 = (*(code *)param_1[5])(param_1,param_2,param_3,param_4);
    }
    param_1[2] = uVar1 + param_2;
    if (uVar1 < param_4) {
      uVar2 = 0x55;
    }
  }
  else {
    uVar2 = 0x55;
  }
  return CONCAT44(param_4,uVar2);
}

