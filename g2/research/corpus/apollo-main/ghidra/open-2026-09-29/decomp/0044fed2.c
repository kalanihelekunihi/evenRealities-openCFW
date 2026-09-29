
undefined8 FUN_0044fed2(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  uVar1 = DAT_0044ff90;
  if (param_1 == 0) {
    FUN_0044d25c(2,DAT_0044ff7c,0x3af,DAT_0044ff9c);
    uVar2 = 0;
    unaff_r7 = uVar1;
  }
  else {
    uVar2 = (uint)(0 < *(int *)(param_1 + 0x264));
  }
  return CONCAT44(unaff_r7,uVar2);
}

