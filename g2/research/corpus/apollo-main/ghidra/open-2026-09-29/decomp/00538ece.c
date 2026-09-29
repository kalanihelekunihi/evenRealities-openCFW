
undefined8 FUN_00538ece(uint *param_1,int param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 *puVar3;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if ((param_3 == (uint *)0x0) || (param_4 == (uint *)0x0)) {
    uVar1 = 6;
  }
  else if (param_1[4] == param_1[5]) {
    FUN_00538d18(param_1);
    if ((int)((param_1[7] + 0xfe) - param_1[8]) < 0) {
      uVar1 = 5;
    }
    else {
      if (param_1[4] < param_1[3]) {
        if (param_1[3] <= param_1[4] + (param_2 + 1) * 8) {
          uVar1 = 5;
          goto LAB_00538f48;
        }
        uVar2 = param_1[4];
      }
      else if (param_1[2] < param_1[4] + (param_2 + 2) * 8) {
        if (param_1[3] <= param_1[1] + (param_2 + 1) * 8) {
          uVar1 = 5;
          goto LAB_00538f48;
        }
        puVar3 = (undefined4 *)param_1[4];
        *puVar3 = *(undefined4 *)(param_1[9] + 4);
        puVar3[1] = param_1[1];
        uVar2 = param_1[1];
      }
      else {
        uVar2 = param_1[4];
      }
      *param_3 = uVar2;
      param_1[8] = param_1[8] + 1;
      *param_4 = param_1[8];
      param_1[5] = uVar2 + param_2 * 8;
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 7;
  }
LAB_00538f48:
  return CONCAT44(param_4,uVar1);
}

