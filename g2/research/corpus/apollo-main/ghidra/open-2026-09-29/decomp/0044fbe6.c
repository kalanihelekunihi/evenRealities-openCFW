
undefined8 FUN_0044fbe6(int param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 == 0) {
    uVar1 = 0x82;
  }
  else {
    uVar1 = *(undefined4 *)(param_1 + 0x18);
  }
  return CONCAT44(unaff_r7,uVar1);
}

