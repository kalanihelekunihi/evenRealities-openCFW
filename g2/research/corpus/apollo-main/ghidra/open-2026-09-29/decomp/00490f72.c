
undefined8 FUN_00490f72(int param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(short *)(param_2 + 0x12) == 4) {
    uVar1 = FUN_00490d36(param_1,*(undefined4 *)(param_2 + 0x1c));
  }
  else if (*(short *)(param_2 + 0x12) == 8) {
    uVar1 = FUN_00490d40(param_1,*(undefined4 *)(param_2 + 0x1c));
  }
  else {
    uVar1 = DAT_004910d4;
    if (*(int *)(param_1 + 0x10) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0x10);
    }
    *(undefined4 *)(param_1 + 0x10) = uVar1;
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

