
undefined8 FUN_0044fd38(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  uVar1 = DAT_0044ff30;
  if (param_1 == 0) {
    FUN_0044d25c(2,DAT_0044ff7c,0x271,DAT_0044ff34);
    uVar2 = 0;
    unaff_r7 = uVar1;
  }
  else {
    uVar2 = *(undefined4 *)(param_1 + 0x2c8);
  }
  return CONCAT44(unaff_r7,uVar2);
}

