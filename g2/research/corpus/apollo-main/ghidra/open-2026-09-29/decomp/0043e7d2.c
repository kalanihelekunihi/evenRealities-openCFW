
void FUN_0043e7d2(undefined4 param_1,int *param_2)

{
  char cVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  ushort uVar11;
  undefined1 auStack_38 [16];
  undefined1 auStack_28 [16];
  
  iVar4 = FUN_00450286(param_2);
  iVar5 = *param_2;
  if (iVar4 == 1) {
    FUN_0043e046(iVar5,0x20);
  }
  else if (iVar4 == 0xb) {
    FUN_0043e086(iVar5,0x20);
    iVar4 = FUN_00452fae(param_2[4]);
    if ((iVar4 == 0) && (iVar4 = FUN_0043e0e0(iVar5,8), iVar4 != 0)) {
      iVar4 = FUN_0043e156(iVar5);
      if (iVar4 << 0x1f < 0) {
        FUN_0043e086(iVar5,1);
      }
      else {
        FUN_0043e046(iVar5,1);
      }
      FUN_00451670(iVar5,0x23,0);
    }
  }
  else if (iVar4 == 3) {
    FUN_0043e086(iVar5,0x20);
  }
  else if (iVar4 == 0x32) {
    uVar6 = FUN_0044ddea(iVar5);
    for (uVar10 = 0; uVar10 < uVar6; uVar10 = uVar10 + 1) {
      FUN_0043f648(*(undefined4 *)(**(int **)(iVar5 + 8) + uVar10 * 4));
    }
  }
  else if (iVar4 == 0x11) {
    iVar4 = FUN_0043e0e0(iVar5,8);
    if (iVar4 == 0) {
      iVar4 = FUN_0043e0e0(iVar5,0x810);
      if ((iVar4 != 0) && (iVar4 = FUN_0044d19a(iVar5), iVar4 == 0)) {
        iVar4 = FUN_0044e586(iVar5);
        iVar7 = FUN_0044e67a(iVar5);
        iVar8 = FUN_004519a0(param_2);
        if (iVar8 == 0x12) {
          iVar4 = FUN_0044e498(iVar5);
          iVar7 = FUN_0043fdda(iVar5);
          FUN_0044ea04(iVar5,iVar7 / 4 + iVar4,0);
        }
        else if (iVar8 == 0x11) {
          iVar4 = FUN_0044e498(iVar5);
          iVar7 = FUN_0043fdda(iVar5);
          FUN_0044ea04(iVar5,iVar4 - iVar7 / 4,0);
        }
        else if (iVar8 == 0x13) {
          uVar6 = FUN_0044e442(iVar5);
          if (((uVar6 & 3) == 0) || ((iVar4 < 1 && (iVar7 < 1)))) {
            iVar4 = FUN_0044e498(iVar5);
            iVar7 = FUN_0043fdda(iVar5);
            FUN_0044ea04(iVar5,iVar7 / 4 + iVar4,0);
          }
          else {
            iVar4 = FUN_0044e486(iVar5);
            iVar7 = FUN_0043fd9e(iVar5);
            FUN_0044e9da(iVar5,iVar7 / 4 + iVar4,0);
          }
        }
        else if (iVar8 == 0x14) {
          uVar6 = FUN_0044e442(iVar5);
          if (((uVar6 & 3) == 0) || ((iVar4 < 1 && (iVar7 < 1)))) {
            iVar4 = FUN_0044e498(iVar5);
            iVar7 = FUN_0043fdda(iVar5);
            FUN_0044ea04(iVar5,iVar4 - iVar7 / 4,0);
          }
          else {
            iVar4 = FUN_0044e486(iVar5);
            iVar7 = FUN_0043fd9e(iVar5);
            FUN_0044e9da(iVar5,iVar4 - iVar7 / 4,0);
          }
        }
      }
    }
    else {
      iVar4 = FUN_004519a0(param_2);
      if ((iVar4 == 0x13) || (iVar4 == 0x11)) {
        FUN_0043e046(iVar5,1);
      }
      else if ((iVar4 == 0x14) || (iVar4 == 0x12)) {
        FUN_0043e086(iVar5,1);
      }
      if (iVar4 != 10) {
        FUN_00451670(iVar5,0x23,0);
      }
    }
  }
  else if (iVar4 == 0x13) {
    iVar4 = FUN_0043e0e0(iVar5,0x400);
    if (iVar4 != 0) {
      FUN_0044ea56(iVar5,1);
    }
    FUN_0043e1be(iVar5);
    cVar1 = FUN_0044d5a4();
    uVar11 = 2;
    iVar4 = FUN_00452ef8();
    if (iVar4 == 0) {
      FUN_004518d8(param_2);
    }
    cVar2 = FUN_00452f00();
    if ((cVar2 == '\x02') || (cVar2 == '\x04')) {
      uVar11 = 6;
    }
    if (cVar1 == '\0') {
      FUN_0043e046(iVar5,uVar11);
      FUN_0043e086(iVar5,8);
    }
    else {
      FUN_0043e046(iVar5,uVar11 | 8);
    }
  }
  else if (iVar4 == 0xc) {
    FUN_0043e046(iVar5,0x40);
  }
  else if (iVar4 == 0xe) {
    FUN_0043e086(iVar5,0x40);
    iVar4 = FUN_0044e42c(iVar5);
    if (iVar4 == 2) {
      FUN_0044eb28(iVar5,auStack_28,auStack_38);
      FUN_004405d4(iVar5,auStack_28);
      FUN_004405d4(iVar5,auStack_38);
    }
  }
  else if (iVar4 == 0x14) {
    FUN_0043e086(iVar5,0xe);
  }
  else if (iVar4 == 0x31) {
    iVar4 = FUN_0043dd66(iVar5,0);
    sVar3 = FUN_0043de76(iVar5,0);
    if ((sVar3 != 0) || (iVar4 != 0)) {
      FUN_0043f648(iVar5);
    }
    uVar6 = FUN_0044ddea(iVar5);
    for (uVar10 = 0; uVar10 < uVar6; uVar10 = uVar10 + 1) {
      FUN_0043f648(*(undefined4 *)(**(int **)(iVar5 + 8) + uVar10 * 4));
    }
  }
  else if (iVar4 == 0x2a) {
    iVar4 = FUN_0043dd52(iVar5,0);
    iVar7 = FUN_0043dd5c(iVar5,0);
    iVar8 = FUN_0043dd66(iVar5,0);
    sVar3 = FUN_0043de76(iVar5,0);
    if (((sVar3 != 0) || (iVar8 != 0)) || ((iVar4 == 0x3fffffff || (iVar7 == 0x3fffffff)))) {
      FUN_0043f648(iVar5);
    }
  }
  else if (iVar4 == 0x2c) {
    *(ushort *)(iVar5 + 0x2a) = *(ushort *)(iVar5 + 0x2a) | 2;
    FUN_0043f648(iVar5);
  }
  else if (iVar4 == 0x1b) {
    uVar9 = FUN_00452c66(iVar5,0);
    FUN_004519fa(param_2,uVar9);
  }
  else if (((iVar4 == 0x1d) || (iVar4 == 0x20)) || (iVar4 == 0x1a)) {
    FUN_0043e442(param_2);
  }
  else if (iVar4 == 0x17) {
    FUN_0043e086(iVar5,0x20);
    FUN_0043e086(iVar5,0x40);
  }
  else if (iVar4 == 0x18) {
    FUN_0043e046(iVar5,0x10);
  }
  else if (iVar4 == 0x19) {
    FUN_0043e086(iVar5,0x10);
  }
  return;
}

