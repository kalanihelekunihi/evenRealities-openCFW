
undefined8 FUN_005d377c(int param_1,undefined4 param_2,uint param_3,int param_4)

{
  bool bVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint local_28;
  int local_24;
  
  local_28 = param_3;
  local_24 = param_4;
  FUN_005d23ac(*(undefined4 *)(param_1 + 8));
  for (uVar7 = 0; uVar7 < *(uint *)(param_1 + 0x14); uVar7 = uVar7 + 1) {
    cVar2 = FUN_005d3654(uVar7 * 0x14 + param_1 + 0x1c);
    uVar10 = uVar7;
    if (cVar2 != '\0') {
      uVar10 = uVar7 + 1;
    }
    iVar4 = FUN_005d3696(uVar7 * 0x14 + param_1 + 0x1c);
    if (iVar4 == 0) {
      iVar4 = *(int *)(uVar7 * 0x14 + param_1 + 0x28) -
              (*(uint *)(uVar7 * 0x14 + param_1 + 0x28) & 0xffff0000);
      iVar8 = *(int *)(uVar10 * 0x14 + param_1 + 0x28) -
              (*(uint *)(uVar10 * 0x14 + param_1 + 0x28) & 0xffff0000);
      if (iVar4 == 0) {
        iVar5 = 0;
      }
      else {
        iVar5 = 0x10000 - iVar4;
      }
      if (iVar8 == 0) {
        iVar9 = 0;
      }
      else {
        iVar9 = 0x10000 - iVar8;
      }
      if (iVar5 < iVar9) {
        iVar9 = iVar5;
      }
      iVar5 = -iVar4;
      if (-iVar4 <= -iVar8) {
        iVar5 = -iVar8;
      }
      bVar1 = false;
      iVar4 = iVar5;
      if ((uVar10 < *(int *)(param_1 + 0x14) - 1U) &&
         (*(int *)(uVar10 * 0x14 + param_1 + 0x3c) <
          iVar9 + *(int *)(uVar10 * 0x14 + param_1 + 0x28) + 0x8000)) {
        if ((uVar7 == 0) ||
           (*(int *)(uVar7 * 0x14 + param_1 + 0x14) <=
            iVar5 + *(int *)(uVar7 * 0x14 + param_1 + 0x28) + -0x8000)) {
          if (iVar9 + iVar5 < 0 == SCARRY4(iVar9,iVar5)) {
            bVar1 = false;
          }
          else {
            bVar1 = true;
          }
        }
        else {
          bVar1 = true;
          iVar4 = 0;
        }
      }
      else {
        iVar4 = iVar9;
        if (((uVar7 == 0) ||
            (*(int *)(uVar7 * 0x14 + param_1 + 0x14) <=
             iVar5 + *(int *)(uVar7 * 0x14 + param_1 + 0x28) + -0x8000)) && (-iVar5 < iVar9)) {
          iVar4 = iVar5;
        }
      }
      if (((bVar1) && (uVar10 < *(int *)(param_1 + 0x14) - 1U)) &&
         (iVar8 = FUN_005d3696(uVar10 * 0x14 + param_1 + 0x30), iVar8 == 0)) {
        local_24 = iVar9 - iVar4;
        local_28 = uVar10;
        FUN_005d23da(*(undefined4 *)(param_1 + 8),&local_28);
      }
      *(int *)(uVar7 * 0x14 + param_1 + 0x28) = iVar4 + *(int *)(uVar7 * 0x14 + param_1 + 0x28);
      if (cVar2 != '\0') {
        *(int *)(uVar10 * 0x14 + param_1 + 0x28) = iVar4 + *(int *)(uVar10 * 0x14 + param_1 + 0x28);
      }
    }
    if ((uVar7 != 0) &&
       (*(int *)(uVar7 * 0x14 + param_1 + 0x24) != *(int *)(uVar7 * 0x14 + param_1 + 0x10))) {
      uVar3 = FT_DivFix(*(int *)(uVar7 * 0x14 + param_1 + 0x28) -
                        *(int *)(uVar7 * 0x14 + param_1 + 0x14),
                        *(int *)(uVar7 * 0x14 + param_1 + 0x24) -
                        *(int *)(uVar7 * 0x14 + param_1 + 0x10));
      *(undefined4 *)(uVar7 * 0x14 + param_1 + 0x18) = uVar3;
    }
    if (cVar2 != '\0') {
      if (*(int *)(uVar10 * 0x14 + param_1 + 0x24) != *(int *)(uVar10 * 0x14 + param_1 + 0x10)) {
        uVar3 = FT_DivFix(*(int *)(uVar10 * 0x14 + param_1 + 0x28) -
                          *(int *)(uVar10 * 0x14 + param_1 + 0x14),
                          *(int *)(uVar10 * 0x14 + param_1 + 0x24) -
                          *(int *)(uVar10 * 0x14 + param_1 + 0x10));
        *(undefined4 *)(param_1 + uVar10 * 0x14 + 0x18) = uVar3;
      }
      uVar7 = uVar7 + 1;
    }
  }
  for (iVar4 = FUN_005d23b2(*(undefined4 *)(param_1 + 8)); iVar4 != 0; iVar4 = iVar4 + -1) {
    piVar6 = (int *)FUN_005d23ba(*(undefined4 *)(param_1 + 8),iVar4 + -1);
    iVar8 = *piVar6;
    if (piVar6[1] + *(int *)(iVar8 * 0x14 + param_1 + 0x28) + 0x8000 <=
        *(int *)(iVar8 * 0x14 + param_1 + 0x3c)) {
      *(int *)(iVar8 * 0x14 + param_1 + 0x28) = piVar6[1] + *(int *)(iVar8 * 0x14 + param_1 + 0x28);
      iVar5 = FUN_005d3654(iVar8 * 0x14 + param_1 + 0x1c);
      if (iVar5 != 0) {
        *(int *)(param_1 + iVar8 * 0x14 + 0x14) =
             piVar6[1] + *(int *)(iVar8 * 0x14 + param_1 + 0x14);
      }
    }
  }
  return CONCAT44(local_24,local_28);
}

