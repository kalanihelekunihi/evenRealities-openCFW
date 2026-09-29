
undefined8 FUN_004c7018(undefined4 *param_1,undefined4 *param_2)

{
  byte bVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  if (param_1[1] == 0) {
    *param_2 = 0;
    uVar2 = 0xb;
  }
  else if ((*(int *)(param_1[1] + 4) == 0) && (*(int *)(param_1[1] + 0x20) == 0)) {
    *param_2 = 0;
    uVar2 = 9;
  }
  else {
    if (*(int *)(param_1[1] + 4) == 0) {
      bVar1 = (**(code **)(param_1[1] + 0x20))(param_1[1],*param_1);
    }
    else {
      *param_2 = *(undefined4 *)(param_1[2] + 8);
      bVar1 = 0;
    }
    uVar2 = (uint)bVar1;
  }
  return CONCAT44(unaff_r7,uVar2);
}

