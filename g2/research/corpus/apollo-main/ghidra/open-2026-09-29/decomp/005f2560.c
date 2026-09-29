
undefined8 ft_var_apply_tuple(uint *param_1,int param_2,int param_3,int param_4,int param_5)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0x10000;
  uVar3 = 0;
  do {
    if (*param_1 <= uVar3) {
LAB_005f25ee:
      return CONCAT44(param_4,uVar1);
    }
    if (*(int *)(param_3 + uVar3 * 4) != 0) {
      if (*(int *)(param_1[2] + uVar3 * 4) == 0) {
        uVar1 = 0;
        goto LAB_005f25ee;
      }
      if (*(int *)(param_1[2] + uVar3 * 4) != *(int *)(param_3 + uVar3 * 4)) {
        if (-1 < param_2 << 0x11) {
          if (*(int *)(param_3 + uVar3 * 4) < 1) {
            iVar2 = *(int *)(param_3 + uVar3 * 4);
          }
          else {
            iVar2 = 0;
          }
          if (iVar2 <= *(int *)(param_1[2] + uVar3 * 4)) {
            if (*(int *)(param_3 + uVar3 * 4) < 0) {
              iVar2 = 0;
            }
            else {
              iVar2 = *(int *)(param_3 + uVar3 * 4);
            }
            if (*(int *)(param_1[2] + uVar3 * 4) <= iVar2) {
              uVar1 = FT_MulDiv(uVar1,*(undefined4 *)(param_1[2] + uVar3 * 4),
                                *(undefined4 *)(param_3 + uVar3 * 4));
              goto LAB_005f25be;
            }
          }
          uVar1 = 0;
          goto LAB_005f25ee;
        }
        if ((*(int *)(param_1[2] + uVar3 * 4) < *(int *)(param_4 + uVar3 * 4)) ||
           (*(int *)(param_5 + uVar3 * 4) < *(int *)(param_1[2] + uVar3 * 4))) {
          uVar1 = 0;
          goto LAB_005f25ee;
        }
        if (*(int *)(param_1[2] + uVar3 * 4) < *(int *)(param_3 + uVar3 * 4)) {
          uVar1 = FT_MulDiv(uVar1,*(int *)(param_1[2] + uVar3 * 4) - *(int *)(param_4 + uVar3 * 4),
                            *(int *)(param_3 + uVar3 * 4) - *(int *)(param_4 + uVar3 * 4));
        }
        else {
          uVar1 = FT_MulDiv(uVar1,*(int *)(param_5 + uVar3 * 4) - *(int *)(param_1[2] + uVar3 * 4),
                            *(int *)(param_5 + uVar3 * 4) - *(int *)(param_3 + uVar3 * 4));
        }
      }
    }
LAB_005f25be:
    uVar3 = uVar3 + 1;
  } while( true );
}

