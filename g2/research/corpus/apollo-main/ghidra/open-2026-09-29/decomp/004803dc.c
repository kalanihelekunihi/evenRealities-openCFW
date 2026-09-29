
undefined8 FUN_004803dc(void)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_004806fc + 0x28) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_004806fc + 0x28))();
  }
  return CONCAT44(unaff_r7,uVar1);
}

