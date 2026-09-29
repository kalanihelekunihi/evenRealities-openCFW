
undefined8 FUN_0041cda2(void)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_0041d11c + 0x1c) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_0041d11c + 0x1c))();
  }
  return CONCAT44(unaff_r7,uVar1);
}

