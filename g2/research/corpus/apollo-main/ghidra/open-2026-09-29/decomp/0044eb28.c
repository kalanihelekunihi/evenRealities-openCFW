
void FUN_0044eb28(int param_1,int *param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  bool bVar19;
  uint uVar20;
  int local_48;
  
  FUN_00450b5c(param_2,0,0,0xffffffff,0xffffffff);
  FUN_00450b5c(param_3,0,0,0xffffffff,0xffffffff);
  iVar2 = FUN_0043e0e0(param_1,0x10);
  if ((iVar2 != 0) && (cVar1 = FUN_0044e42c(param_1), cVar1 != '\0')) {
    iVar2 = FUN_00452edc(0);
    if (cVar1 == '\x02') {
      while ((iVar2 != 0 && (iVar3 = FUN_00452fae(iVar2), iVar3 != param_1))) {
        iVar2 = FUN_00452edc(iVar2);
      }
      if (iVar2 == 0) {
        return;
      }
    }
    iVar3 = FUN_0044e4aa(param_1);
    iVar4 = FUN_0044e4bc(param_1);
    iVar5 = FUN_0044e586(param_1);
    iVar6 = FUN_0044e67a(param_1);
    uVar7 = FUN_0044e442(param_1);
    uVar20 = 0;
    if (((uVar7 & 0xc) != 0) &&
       (((cVar1 == '\x01' || ((cVar1 == '\x03' && ((0 < iVar3 || (0 < iVar4)))))) ||
        ((cVar1 == '\x02' && (iVar8 = FUN_00452f8c(iVar2), iVar8 == 0xc)))))) {
      uVar20 = 0x100;
    }
    uVar20 = uVar20 & 0xffffff00;
    if (((uVar7 & 3) != 0) &&
       (((cVar1 == '\x01' || ((cVar1 == '\x03' && ((0 < iVar5 || (0 < iVar6)))))) ||
        ((cVar1 == '\x02' && (iVar2 = FUN_00452f8c(iVar2), iVar2 == 3)))))) {
      uVar20 = CONCAT31((int3)(uVar20 >> 8),1);
    }
    if ((char)uVar20 != '\0' || (char)(uVar20 >> 8) != '\0') {
      iVar2 = FUN_0044e2a4(param_1,0x10000);
      bVar19 = iVar2 != 1;
      iVar8 = FUN_0044e230(param_1,0x10000);
      iVar9 = FUN_0044e23a(param_1,0x10000);
      iVar10 = FUN_0044e244(param_1,0x10000);
      iVar11 = FUN_0044e24e(param_1,0x10000);
      iVar12 = FUN_0044e21c(param_1,0x10000);
      iVar13 = FUN_0044e226(param_1,0x10000);
      iVar14 = FUN_0043fdda(param_1);
      iVar15 = FUN_0043fd9e(param_1);
      iVar2 = iVar12;
      if ((char)(uVar20 >> 8) == '\0') {
        iVar2 = 0;
      }
      local_48 = iVar12;
      if ((char)uVar20 == '\0') {
        local_48 = 0;
      }
      iVar16 = FUN_0044e276(param_1,0x10000);
      if ((1 < iVar16) || (iVar16 = FUN_0044e282(param_1,0x10000), 1 < iVar16)) {
        iVar3 = iVar4 + iVar3 + iVar14;
        if (((char)(uVar20 >> 8) != '\0') && (iVar3 != 0)) {
          param_3[1] = *(int *)(param_1 + 0x18);
          param_3[3] = *(int *)(param_1 + 0x20);
          if (bVar19) {
            param_3[2] = *(int *)(param_1 + 0x1c) - iVar11;
            *param_3 = (param_3[2] - iVar12) + 1;
          }
          else {
            *param_3 = iVar10 + *(int *)(param_1 + 0x14);
            param_3[2] = iVar12 + *param_3 + -1;
          }
          iVar16 = (iVar14 * (((iVar14 - iVar8) - iVar9) - local_48)) / iVar3;
          iVar17 = FUN_0044fbe6(0);
          if ((iVar17 * 10 + 0x50) / 0xa0 < 2) {
            iVar17 = 1;
          }
          else {
            iVar17 = FUN_0044fbe6(0);
            iVar17 = (iVar17 * 10 + 0x50) / 0xa0;
          }
          iVar18 = iVar16;
          if (0 < iVar13) {
            iVar18 = iVar13;
          }
          if (iVar17 < iVar18) {
            if (0 < iVar13) {
              iVar16 = iVar13;
            }
          }
          else {
            iVar16 = FUN_0044fbe6(0);
            if ((iVar16 * 10 + 0x50) / 0xa0 < 2) {
              iVar16 = 1;
            }
            else {
              iVar16 = FUN_0044fbe6(0);
              iVar16 = (iVar16 * 10 + 0x50) / 0xa0;
            }
          }
          if (iVar14 <= iVar16) {
            iVar16 = iVar14;
          }
          iVar17 = (((iVar14 - iVar8) - iVar9) - local_48) - iVar16;
          if (iVar3 - iVar14 < 1) {
            param_3[1] = iVar8 + *(int *)(param_1 + 0x18);
            param_3[3] = ((*(int *)(param_1 + 0x20) - iVar9) - local_48) + -1;
          }
          else {
            param_3[1] = iVar8 + (iVar17 - (iVar4 * iVar17) / (iVar3 - iVar14)) +
                                 *(int *)(param_1 + 0x18);
            param_3[3] = iVar16 + param_3[1] + -1;
            if (param_3[1] < iVar8 + *(int *)(param_1 + 0x18)) {
              param_3[1] = iVar8 + *(int *)(param_1 + 0x18);
              iVar3 = FUN_0044fbe6(0);
              if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                iVar3 = 1;
              }
              else {
                iVar3 = FUN_0044fbe6(0);
                iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
              }
              if (param_3[3] < iVar3 + param_3[1]) {
                iVar3 = FUN_0044fbe6(0);
                if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                  iVar3 = 1;
                }
                else {
                  iVar3 = FUN_0044fbe6(0);
                  iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
                }
                param_3[3] = iVar3 + param_3[1];
              }
            }
            if ((*(int *)(param_1 + 0x20) - local_48) - iVar9 < param_3[3]) {
              param_3[3] = (*(int *)(param_1 + 0x20) - local_48) - iVar9;
              iVar3 = FUN_0044fbe6(0);
              if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                iVar3 = 1;
              }
              else {
                iVar3 = FUN_0044fbe6(0);
                iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
              }
              if (param_3[3] - iVar3 < param_3[1]) {
                iVar3 = FUN_0044fbe6(0);
                if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                  iVar3 = 1;
                }
                else {
                  iVar3 = FUN_0044fbe6(0);
                  iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
                }
                param_3[1] = param_3[3] - iVar3;
              }
            }
          }
        }
        iVar3 = iVar6 + iVar5 + iVar15;
        if (((char)uVar20 != '\0') && (iVar3 != 0)) {
          param_2[3] = *(int *)(param_1 + 0x20) - iVar9;
          param_2[1] = (param_2[3] - iVar12) + 1;
          *param_2 = *(int *)(param_1 + 0x14);
          param_2[2] = *(int *)(param_1 + 0x1c);
          iVar4 = (iVar15 * (((iVar15 - iVar10) - iVar11) - iVar2)) / iVar3;
          iVar5 = FUN_0044fbe6(0);
          if ((iVar5 * 10 + 0x50) / 0xa0 < 2) {
            iVar5 = 1;
          }
          else {
            iVar5 = FUN_0044fbe6(0);
            iVar5 = (iVar5 * 10 + 0x50) / 0xa0;
          }
          iVar8 = iVar4;
          if (0 < iVar13) {
            iVar8 = iVar13;
          }
          if (iVar5 < iVar8) {
            if (0 < iVar13) {
              iVar4 = iVar13;
            }
          }
          else {
            iVar4 = FUN_0044fbe6(0);
            if ((iVar4 * 10 + 0x50) / 0xa0 < 2) {
              iVar4 = 1;
            }
            else {
              iVar4 = FUN_0044fbe6(0);
              iVar4 = (iVar4 * 10 + 0x50) / 0xa0;
            }
          }
          if (iVar15 <= iVar4) {
            iVar4 = iVar15;
          }
          iVar5 = (((iVar15 - iVar10) - iVar11) - iVar2) - iVar4;
          if (iVar3 - iVar15 < 1) {
            if (bVar19) {
              *param_2 = iVar10 + *(int *)(param_1 + 0x14);
              param_2[2] = ((*(int *)(param_1 + 0x1c) - iVar11) - iVar2) + -1;
            }
            else {
              *param_2 = iVar2 + iVar10 + *(int *)(param_1 + 0x14) + -1;
              param_2[2] = *(int *)(param_1 + 0x1c) - iVar11;
            }
          }
          else {
            iVar5 = iVar5 - (iVar6 * iVar5) / (iVar3 - iVar15);
            if (bVar19) {
              *param_2 = iVar10 + iVar5 + *(int *)(param_1 + 0x14);
              param_2[2] = iVar4 + *param_2 + -1;
              if (*param_2 < iVar10 + *(int *)(param_1 + 0x14)) {
                *param_2 = iVar10 + *(int *)(param_1 + 0x14);
                iVar3 = FUN_0044fbe6(0);
                if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                  iVar3 = 1;
                }
                else {
                  iVar3 = FUN_0044fbe6(0);
                  iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
                }
                if (param_2[2] < iVar3 + *param_2) {
                  iVar3 = FUN_0044fbe6(0);
                  if ((iVar3 * 10 + 0x50) / 0xa0 < 2) {
                    iVar3 = 1;
                  }
                  else {
                    iVar3 = FUN_0044fbe6(0);
                    iVar3 = (iVar3 * 10 + 0x50) / 0xa0;
                  }
                  param_2[2] = iVar3 + *param_2;
                }
              }
              if ((*(int *)(param_1 + 0x1c) - iVar2) - iVar11 < param_2[2]) {
                param_2[2] = (*(int *)(param_1 + 0x1c) - iVar2) - iVar11;
                iVar2 = FUN_0044fbe6(0);
                if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                  iVar2 = 1;
                }
                else {
                  iVar2 = FUN_0044fbe6(0);
                  iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                }
                if (param_2[2] - iVar2 < *param_2) {
                  iVar2 = FUN_0044fbe6(0);
                  if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                    iVar2 = 1;
                  }
                  else {
                    iVar2 = FUN_0044fbe6(0);
                    iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                  }
                  *param_2 = param_2[2] - iVar2;
                }
              }
            }
            else {
              *param_2 = iVar2 + iVar10 + iVar5 + *(int *)(param_1 + 0x14);
              param_2[2] = iVar4 + *param_2 + -1;
              if (*param_2 < iVar2 + iVar10 + *(int *)(param_1 + 0x14)) {
                *param_2 = iVar2 + iVar10 + *(int *)(param_1 + 0x14);
                iVar2 = FUN_0044fbe6(0);
                if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                  iVar2 = 1;
                }
                else {
                  iVar2 = FUN_0044fbe6(0);
                  iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                }
                if (param_2[2] < iVar2 + *param_2) {
                  iVar2 = FUN_0044fbe6(0);
                  if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                    iVar2 = 1;
                  }
                  else {
                    iVar2 = FUN_0044fbe6(0);
                    iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                  }
                  param_2[2] = iVar2 + *param_2;
                }
              }
              if (*(int *)(param_1 + 0x1c) - iVar11 < param_2[2]) {
                param_2[2] = *(int *)(param_1 + 0x1c) - iVar11;
                iVar2 = FUN_0044fbe6(0);
                if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                  iVar2 = 1;
                }
                else {
                  iVar2 = FUN_0044fbe6(0);
                  iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                }
                if (param_2[2] - iVar2 < *param_2) {
                  iVar2 = FUN_0044fbe6(0);
                  if ((iVar2 * 10 + 0x50) / 0xa0 < 2) {
                    iVar2 = 1;
                  }
                  else {
                    iVar2 = FUN_0044fbe6(0);
                    iVar2 = (iVar2 * 10 + 0x50) / 0xa0;
                  }
                  *param_2 = param_2[2] - iVar2;
                }
              }
            }
          }
        }
      }
    }
  }
  return;
}

