
undefined8 FUN_004803c2(undefined1 param_1,undefined1 param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_004806fc + 0x24) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_004806fc + 0x24))(param_1,param_2);
  }
  return CONCAT44(unaff_r7,uVar1);
}

