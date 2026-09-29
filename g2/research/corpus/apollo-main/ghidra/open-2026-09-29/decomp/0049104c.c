
undefined8 FUN_0049104c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  
  if (*(int *)(param_2 + 0x24) == 0) {
    uVar1 = DAT_004910e4;
    if (*(int *)(param_1 + 0x10) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0x10);
    }
    *(undefined4 *)(param_1 + 0x10) = uVar1;
    uVar1 = 0;
  }
  else {
    if (((*(byte *)(param_2 + 0x16) & 0xf) == 9) && (*(int *)(param_2 + 0x20) != 0)) {
      piVar3 = (int *)(*(int *)(param_2 + 0x20) + -8);
      if ((*piVar3 != 0) &&
         (iVar2 = (*(code *)*piVar3)(param_1,param_2,*(int *)(param_2 + 0x20) + -4), iVar2 == 0)) {
        uVar1 = 0;
        goto LAB_004910a2;
      }
    }
    uVar1 = FUN_00490ddc(param_1,*(undefined4 *)(param_2 + 0x24),*(undefined4 *)(param_2 + 0x1c));
  }
LAB_004910a2:
  return CONCAT44(param_4,uVar1);
}

