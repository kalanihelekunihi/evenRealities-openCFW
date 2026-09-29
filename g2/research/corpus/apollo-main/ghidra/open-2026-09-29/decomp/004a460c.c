
undefined4 semantic_set_orientation_matrix(undefined4 param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  for (iVar1 = 0; iVar1 < 9; iVar1 = iVar1 + 1) {
    *(undefined4 *)(DAT_004a50d4 + iVar1 * 4) = *(undefined4 *)(param_3 + iVar1 * 4);
    uVar2 = VectorFloatToSignedFixed(*(undefined4 *)(param_3 + iVar1 * 4),0x20,0xe);
    *(short *)(DAT_004a4990 + iVar1 * 2) = (short)uVar2;
    if (((iVar1 == 2) || (iVar1 == 5)) || (iVar1 == 8)) {
      uVar2 = VectorFloatToSignedFixed(*(undefined4 *)(param_3 + iVar1 * 4),0x20,0x1e);
      *(undefined4 *)(DAT_004a4994 + (iVar1 / 3) * 0xc + (iVar1 % 3) * 4) = uVar2;
    }
    else {
      uVar2 = VectorFloatToSignedFixed(*(float *)(param_3 + iVar1 * 4) * -1.0,0x20,0x1e);
      *(undefined4 *)(DAT_004a4994 + (iVar1 / 3) * 0xc + (iVar1 % 3) * 4) = uVar2;
    }
  }
  return 0;
}

