
undefined8 cff_parse_fixed_dynamic(int param_1,undefined4 *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (*(char *)*param_2 == '\x1e') {
    iVar2 = cff_parse_real(*param_2,*(undefined4 *)(param_1 + 8),0,param_3);
  }
  else {
    iVar2 = cff_parse_integer(*param_2,param_2[1]);
    iVar1 = DAT_005ad768;
    if (iVar2 < 0x8000) {
      *param_3 = 0;
      iVar2 = iVar2 << 0x10;
    }
    else {
      for (iVar3 = 5; (iVar3 < 10 && (*(int *)(DAT_005ad768 + iVar3 * 4) <= iVar2));
          iVar3 = iVar3 + 1) {
      }
      if (iVar2 / *(int *)(DAT_005ad768 + iVar3 * 4 + -0x14) < 0x8000) {
        *param_3 = iVar3 + -5;
        iVar2 = FT_DivFix(iVar2,*(undefined4 *)(iVar1 + iVar3 * 4 + -0x14));
      }
      else {
        *param_3 = iVar3 + -4;
        iVar2 = FT_DivFix(iVar2,*(undefined4 *)(iVar1 + iVar3 * 4 + -0x10));
      }
    }
  }
  return CONCAT44(param_4,iVar2);
}

