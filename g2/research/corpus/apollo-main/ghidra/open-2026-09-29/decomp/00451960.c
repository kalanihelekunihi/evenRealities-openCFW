
undefined8 FUN_00451960(int param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  undefined4 uVar2;
  
  uVar2 = DAT_00451a54;
  if ((((*(int *)(param_1 + 8) == 0x1d) || (*(int *)(param_1 + 8) == 0x1c)) ||
      (*(int *)(param_1 + 8) == 0x1e)) ||
     (((*(int *)(param_1 + 8) == 0x20 || (*(int *)(param_1 + 8) == 0x1f)) ||
      (*(int *)(param_1 + 8) == 0x21)))) {
    uVar1 = *(undefined4 *)(param_1 + 0x10);
    uVar2 = unaff_r7;
  }
  else {
    FUN_0044d25c(2,DAT_00451a3c,0xe0,DAT_00451a5c);
    uVar1 = 0;
  }
  return CONCAT44(uVar2,uVar1);
}

