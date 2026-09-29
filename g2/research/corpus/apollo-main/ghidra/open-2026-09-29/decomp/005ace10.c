
undefined8 cff_parse_real(byte *param_1,byte *param_2,int param_3,int *param_4)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  bool bVar11;
  
  bVar2 = false;
  bVar1 = false;
  if (param_4 != (int *)0x0) {
    *param_4 = 0;
  }
  iVar6 = 0;
  iVar5 = 0;
  iVar9 = 0;
  iVar10 = 0;
  iVar7 = 0;
  iVar8 = 0;
  uVar3 = 4;
  while ((uVar3 == 0 || (param_1 = param_1 + 1, param_1 < param_2))) {
    uVar4 = (int)(uint)*param_1 >> (uVar3 & 0xff) & 0xf;
    uVar3 = 4 - uVar3;
    if (uVar4 == 0xe) {
      bVar2 = true;
    }
    else {
      if (9 < uVar4) {
        if (uVar4 == 10) goto LAB_005acea4;
        goto LAB_005ace7c;
      }
      if (iVar5 < DAT_005ad764) {
        if ((uVar4 != 0) || (iVar5 != 0)) {
          iVar7 = iVar7 + 1;
          iVar5 = iVar5 * 10 + uVar4;
        }
      }
      else {
        iVar10 = iVar10 + 1;
      }
    }
  }
LAB_005ace50:
  iVar6 = 0;
  goto LAB_005ad074;
LAB_005acea4:
  if ((uVar3 != 0) && (param_1 = param_1 + 1, param_2 <= param_1)) goto LAB_005ace50;
  uVar4 = (int)(uint)*param_1 >> (uVar3 & 0xff) & 0xf;
  uVar3 = 4 - uVar3;
  if (uVar4 < 10) {
    if ((uVar4 == 0) && (iVar5 == 0)) {
      iVar10 = iVar10 + -1;
    }
    else if ((iVar5 < DAT_005ad764) && (iVar8 < 9)) {
      iVar8 = iVar8 + 1;
      iVar5 = iVar5 * 10 + uVar4;
    }
    goto LAB_005acea4;
  }
LAB_005ace7c:
  bVar11 = uVar4 == 0xc;
  if (bVar11) {
    uVar4 = 0xb;
  }
  if (uVar4 == 0xb) {
    while( true ) {
      if ((uVar3 != 0) && (param_1 = param_1 + 1, param_2 <= param_1)) goto LAB_005ace50;
      uVar4 = (int)(uint)*param_1 >> (uVar3 & 0xff) & 0xf;
      uVar3 = 4 - uVar3;
      if (9 < uVar4) break;
      if (iVar9 < 0x3e9) {
        iVar9 = iVar9 * 10 + uVar4;
      }
      else {
        bVar1 = true;
      }
    }
    if (bVar11) {
      iVar9 = -iVar9;
    }
  }
  if (iVar5 == 0) goto LAB_005ad074;
  if (bVar1) {
    if (bVar11) {
LAB_005acf38:
      iVar6 = 0;
      goto LAB_005ad074;
    }
  }
  else {
    iVar10 = iVar10 + param_3 + iVar9;
    if (param_4 != (int *)0x0) {
      iVar8 = iVar7 + iVar8;
      iVar7 = iVar7 + iVar10;
      if (iVar8 < 6) {
        if (iVar5 < 0x8000) {
          if (iVar7 < 1) {
            iVar7 = iVar7 - iVar8;
          }
          else {
            iVar9 = iVar7;
            if (4 < iVar7) {
              iVar9 = 5;
            }
            if (iVar9 - iVar8 < 1) {
              iVar7 = iVar7 - iVar8;
            }
            else {
              iVar7 = iVar7 - iVar9;
              iVar5 = *(int *)(DAT_005ad768 + (iVar9 - iVar8) * 4) * iVar5;
              if (0x7fff < iVar5) {
                iVar5 = iVar5 / 10;
                iVar7 = iVar7 + 1;
              }
            }
          }
          iVar6 = iVar5 << 0x10;
          *param_4 = iVar7;
        }
        else {
          iVar6 = FT_DivFix(iVar5,10);
          *param_4 = (iVar7 - iVar8) + 1;
        }
      }
      else if (iVar5 / *(int *)(DAT_005ad768 + iVar8 * 4 + -0x14) < 0x8000) {
        iVar6 = FT_DivFix(iVar5,*(undefined4 *)(DAT_005ad768 + iVar8 * 4 + -0x14));
        *param_4 = iVar7 + -5;
      }
      else {
        iVar6 = FT_DivFix(iVar5,*(undefined4 *)(DAT_005ad768 + iVar8 * 4 + -0x10));
        *param_4 = iVar7 + -4;
      }
      goto LAB_005ad074;
    }
    iVar7 = iVar10 + iVar7;
    iVar8 = iVar8 - iVar10;
    if (iVar7 < 6) {
      if (iVar7 < -5) goto LAB_005acf38;
      if (iVar7 < 0) {
        iVar5 = iVar5 / *(int *)(DAT_005ad768 + iVar7 * -4);
        iVar8 = iVar7 + iVar8;
      }
      if (iVar8 == 10) {
        iVar5 = iVar5 / 10;
        iVar8 = 9;
      }
      if (0 < iVar8) {
        if (iVar5 / *(int *)(DAT_005ad768 + iVar8 * 4) < 0x8000) {
          iVar6 = FT_DivFix(iVar5,*(undefined4 *)(DAT_005ad768 + iVar8 * 4));
        }
        goto LAB_005ad074;
      }
      iVar5 = *(int *)(DAT_005ad768 + iVar8 * -4) * iVar5;
      if (iVar5 < 0x8000) {
        iVar6 = iVar5 * 0x10000;
        goto LAB_005ad074;
      }
    }
  }
  iVar6 = 0x7fffffff;
LAB_005ad074:
  if (bVar2) {
    iVar6 = -iVar6;
  }
  return CONCAT44(param_2,iVar6);
}

