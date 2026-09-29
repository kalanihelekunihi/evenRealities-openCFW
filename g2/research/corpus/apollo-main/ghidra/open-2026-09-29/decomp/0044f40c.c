
void FUN_0044f40c(int *param_1,int param_2,int *param_3,char param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  
  iVar2 = FUN_0044dca2(param_2);
  iVar3 = FUN_0043e0e0(iVar2,0x10);
  if (iVar3 != 0) {
    iVar4 = FUN_0044e442(iVar2);
    iVar3 = 0;
    bVar1 = FUN_0044e470(iVar2);
    piVar9 = param_1;
    if (bVar1 != 0) {
      piVar9 = (int *)(param_2 + 0x14);
    }
    iVar5 = FUN_0044e30c(iVar2,0);
    iVar6 = FUN_0044e33a(iVar2,0);
    iVar10 = ((iVar5 + *(int *)(iVar2 + 0x18)) - piVar9[1]) - param_3[1];
    iVar8 = piVar9[3] + iVar6 + (param_3[1] - *(int *)(iVar2 + 0x20));
    iVar7 = FUN_0043fdda(iVar2);
    if ((iVar10 < 0) || (iVar8 < 0)) {
      if (iVar10 < 1) {
        if (0 < iVar8) {
          iVar3 = -iVar8;
          iVar8 = FUN_0044e4bc(iVar2);
          if (iVar3 + iVar8 < 0) {
            iVar3 = 0;
          }
        }
      }
      else {
        iVar8 = FUN_0044e4aa(iVar2);
        iVar3 = iVar10;
        if (iVar8 - iVar10 < 0) {
          iVar3 = 0;
        }
      }
    }
    else {
      iVar3 = 0;
    }
    if (bVar1 != 0) {
      if (bVar1 == 2) {
        iVar3 = (*(int *)(iVar2 + 0x20) - iVar6) - piVar9[3];
      }
      else if (bVar1 < 2) {
        iVar3 = (iVar5 + *(int *)(iVar2 + 0x18)) - piVar9[1];
      }
      else if (bVar1 == 3) {
        iVar3 = *(int *)(iVar2 + 0x18);
        iVar8 = FUN_004515a4(piVar9);
        iVar3 = (((iVar7 - iVar5) - iVar6) / 2 + iVar5 + iVar3) - (piVar9[1] + iVar8 / 2);
      }
    }
    iVar5 = 0;
    bVar1 = FUN_0044e45a(iVar2);
    if (bVar1 != 0) {
      param_1 = (int *)(param_2 + 0x14);
    }
    iVar6 = FUN_0044e2b0(iVar2,0);
    iVar7 = FUN_0044e2de(iVar2,0);
    iVar10 = ((iVar6 + *(int *)(iVar2 + 0x14)) - *param_1) - *param_3;
    iVar8 = param_1[2] + iVar7 + (*param_3 - *(int *)(iVar2 + 0x1c));
    if ((iVar10 < 0) || (iVar8 < 0)) {
      if (iVar10 < 1) {
        if (0 < iVar8) {
          iVar5 = -iVar8;
          iVar8 = FUN_0044e67a(iVar2);
          if (iVar5 + iVar8 < 0) {
            iVar5 = 0;
          }
        }
      }
      else {
        iVar8 = FUN_0044e586(iVar2);
        iVar5 = iVar10;
        if (iVar8 - iVar10 < 0) {
          iVar5 = 0;
        }
      }
    }
    else {
      iVar5 = 0;
    }
    iVar8 = FUN_0043fd9e(iVar2);
    if (bVar1 != 0) {
      if (bVar1 == 2) {
        iVar5 = (*(int *)(iVar2 + 0x1c) - iVar7) - param_1[2];
      }
      else if (bVar1 < 2) {
        iVar5 = (iVar6 + *(int *)(iVar2 + 0x14)) - *param_1;
      }
      else if (bVar1 == 3) {
        iVar10 = *(int *)(iVar2 + 0x14);
        iVar5 = FUN_00451598(param_1);
        iVar5 = (((iVar8 - iVar6) - iVar7) / 2 + iVar6 + iVar10) - (*param_1 + iVar5 / 2);
      }
    }
    FUN_00450500(iVar2,DAT_0044f704);
    FUN_00450500(iVar2,DAT_0044f708);
    if ((-1 < iVar4 << 0x1f) && (iVar5 < 0)) {
      iVar5 = 0;
    }
    if ((-1 < iVar4 << 0x1e) && (0 < iVar5)) {
      iVar5 = 0;
    }
    if ((-1 < iVar4 << 0x1d) && (iVar3 < 0)) {
      iVar3 = 0;
    }
    if ((-1 < iVar4 << 0x1c) && (0 < iVar3)) {
      iVar3 = 0;
    }
    iVar4 = iVar5;
    if (param_4 == '\0') {
      iVar4 = 0;
    }
    *param_3 = iVar4 + *param_3;
    iVar4 = iVar3;
    if (param_4 == '\0') {
      iVar4 = 0;
    }
    param_3[1] = iVar4 + param_3[1];
    FUN_0044e884(iVar2,iVar5,iVar3,param_4);
  }
  return;
}

