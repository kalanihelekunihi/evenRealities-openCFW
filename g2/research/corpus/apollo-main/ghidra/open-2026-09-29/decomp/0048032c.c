
undefined8 FUN_0048032c(void)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_004806fc + 0xc) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_004806fc + 0xc))();
  }
  return CONCAT44(unaff_r7,uVar1);
}

