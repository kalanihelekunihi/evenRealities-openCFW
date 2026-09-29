
undefined8 FUN_0048aaea(int param_1,undefined4 param_2,undefined1 param_3)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0x14) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(param_1 + 0x14))(param_2,param_3);
  }
  return CONCAT44(unaff_r7,uVar1);
}

