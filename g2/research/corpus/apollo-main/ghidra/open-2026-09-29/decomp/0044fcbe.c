
undefined8 FUN_0044fcbe(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  uVar1 = DAT_0044ff20;
  if (param_1 == 0) {
    FUN_0044d25c(2,DAT_0044fd34,0x25b,DAT_0044ff24);
    uVar2 = 0;
    unaff_r7 = uVar1;
  }
  else {
    uVar2 = *(undefined4 *)(param_1 + 0x2c0);
  }
  return CONCAT44(unaff_r7,uVar2);
}

