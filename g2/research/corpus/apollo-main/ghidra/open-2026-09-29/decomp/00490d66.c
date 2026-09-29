
undefined8 FUN_00490d66(int param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  uVar2 = *(byte *)(param_2 + 0x16) & 0xf;
  if (uVar2 < 4) {
    uVar1 = 0;
  }
  else if (uVar2 == 4) {
    uVar1 = 5;
  }
  else if (uVar2 == 5) {
    uVar1 = 1;
  }
  else {
    if ((3 < uVar2 - 6) && (uVar2 - 6 != 5)) {
      uVar1 = DAT_004910c0;
      if (*(int *)(param_1 + 0x10) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0x10);
      }
      *(undefined4 *)(param_1 + 0x10) = uVar1;
      uVar1 = 0;
      goto LAB_00490d94;
    }
    uVar1 = 2;
  }
  uVar1 = FUN_00490d4a(param_1,uVar1,*(undefined2 *)(param_2 + 0x10));
LAB_00490d94:
  return CONCAT44(unaff_r7,uVar1);
}

