
undefined4 cff_blend_check_vector(char *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((((*param_1 == '\0') || (*(int *)(param_1 + 8) != param_2)) ||
      (*(int *)(param_1 + 0xc) != param_3)) ||
     ((param_3 != 0 &&
      (iVar1 = FUN_004751c8(param_4,*(undefined4 *)(param_1 + 0x10),param_3 << 2), iVar1 != 0)))) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

