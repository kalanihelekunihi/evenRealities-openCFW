
undefined8 FUN_0053901a(uint *param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if (param_2 == (uint *)0x0) {
    uVar1 = 6;
  }
  else {
    FUN_00538d18(param_1);
    *param_2 = param_1[7];
    param_2[2] = param_1[8];
    param_2[1] = param_1[8] - (uint)(param_1[5] != param_1[4]);
    uVar2 = **(uint **)(param_1[9] + 0x18);
    *(bool *)(param_2 + 3) = (uVar2 & *(uint *)(param_1[9] + 0x1c)) != 0;
    *(bool *)((int)param_2 + 0xd) = (uVar2 & *(uint *)(param_1[9] + 0x24)) != 0;
    *(bool *)((int)param_2 + 0xe) = (uVar2 & *(uint *)(param_1[9] + 0x20)) != 0;
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

