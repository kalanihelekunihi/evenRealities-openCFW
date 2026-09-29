
undefined8 FUN_004519a0(int param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  undefined4 uVar2;
  
  uVar2 = DAT_00451a54;
  if (*(int *)(param_1 + 8) == 0x11) {
    uVar2 = unaff_r7;
    if (*(undefined4 **)(param_1 + 0x10) == (undefined4 *)0x0) {
      uVar1 = 0;
    }
    else {
      uVar1 = **(undefined4 **)(param_1 + 0x10);
    }
  }
  else {
    FUN_0044d25c(2,DAT_00451a3c,0xf8,DAT_00451a60);
    uVar1 = 0;
  }
  return CONCAT44(uVar2,uVar1);
}

