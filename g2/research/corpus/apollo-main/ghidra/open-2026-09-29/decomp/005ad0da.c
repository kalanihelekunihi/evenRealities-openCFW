
undefined8 do_fixed(int param_1,undefined4 *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (*(char *)*param_2 == '\x1e') {
    iVar1 = cff_parse_real(*param_2,*(undefined4 *)(param_1 + 8),param_3,0);
  }
  else {
    iVar2 = cff_parse_integer(*param_2,*(undefined4 *)(param_1 + 8));
    iVar1 = DAT_005ad770;
    if (param_3 != 0) {
      iVar3 = iVar2;
      if (iVar2 < 0) {
        iVar3 = -iVar2;
      }
      if (*(int *)(DAT_005ad76c + param_3 * 4) < iVar3) {
        if (0 < iVar2) {
          iVar1 = 0x7fffffff;
        }
        goto LAB_005ad126;
      }
      iVar2 = *(int *)(DAT_005ad768 + param_3 * 4) * iVar2;
    }
    if (iVar2 < 0x8000) {
      if (DAT_005ad774 <= iVar2) {
        iVar1 = iVar2 << 0x10;
      }
    }
    else {
      iVar1 = 0x7fffffff;
    }
  }
LAB_005ad126:
  return CONCAT44(param_4,iVar1);
}

