
undefined4 FUN_00480312(undefined1 param_1,undefined1 param_2)

{
  undefined4 uVar1;
  
  if (*(int *)(DAT_004806fc + 4) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_004806fc + 4))(param_1,param_2);
  }
  return uVar1;
}

