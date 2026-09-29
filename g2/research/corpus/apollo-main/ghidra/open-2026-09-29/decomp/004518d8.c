
undefined8 FUN_004518d8(int param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  undefined4 uVar2;
  
  uVar2 = DAT_00451a54;
  if (((((((*(int *)(param_1 + 8) == 1) || (*(int *)(param_1 + 8) == 2)) ||
         (*(int *)(param_1 + 8) == 3)) ||
        ((*(int *)(param_1 + 8) == 4 || (*(int *)(param_1 + 8) == 8)))) ||
       ((*(int *)(param_1 + 8) == 9 ||
        ((*(int *)(param_1 + 8) == 10 || (*(int *)(param_1 + 8) == 0xb)))))) ||
      (*(int *)(param_1 + 8) == 0xc)) ||
     (((((*(int *)(param_1 + 8) == 0xe || (*(int *)(param_1 + 8) == 0xf)) ||
        (*(int *)(param_1 + 8) == 0x10)) ||
       (((*(int *)(param_1 + 8) == 0x11 || (*(int *)(param_1 + 8) == 0x13)) ||
        ((*(int *)(param_1 + 8) == 0x14 ||
         ((*(int *)(param_1 + 8) == 0x15 || (*(int *)(param_1 + 8) == 0x18)))))))) ||
      (*(int *)(param_1 + 8) == 0x19)))) {
    uVar1 = *(undefined4 *)(param_1 + 0x10);
    uVar2 = unaff_r7;
  }
  else {
    FUN_0044d25c(2,DAT_00451a3c,0xd0,DAT_00451a58);
    uVar1 = 0;
  }
  return CONCAT44(uVar2,uVar1);
}

