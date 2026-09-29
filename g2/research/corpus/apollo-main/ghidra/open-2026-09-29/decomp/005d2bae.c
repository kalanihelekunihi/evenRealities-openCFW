
void FUN_005d2bae(int param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  bool bVar10;
  undefined4 local_2c;
  undefined4 local_28;
  
  iVar6 = *(int *)(param_1 + 0xb0);
  iVar7 = *(int *)(param_1 + 0x88);
  uVar8 = *(undefined4 *)(param_1 + 0x8c);
  local_28 = 0;
  local_2c = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  iVar1 = FUN_005d3238(iVar6);
  bVar10 = *(int *)(param_1 + 0xb4) != iVar1;
  if (bVar10) {
    *(int *)(param_1 + 0xb4) = iVar1;
  }
  if (*(char *)(param_1 + 8) == '\0') {
    iVar9 = *(int *)(param_1 + 0x224);
    piVar2 = (int *)FUN_005d323e(iVar6);
    if (*piVar2 != 0) {
      uVar3 = FUN_005d3252(iVar6,&local_28,&local_2c);
      *(undefined4 *)(param_1 + 4) = uVar3;
      if (*(int *)(param_1 + 4) != 0) {
        return;
      }
      iVar4 = (**(code **)(iVar9 + 0xc))
                        (iVar1 + 0x22c,*(undefined4 *)(iVar1 + 0x224),local_28,local_2c);
      if (iVar4 != 0) {
        (**(code **)(iVar9 + 4))(*(undefined4 *)(iVar6 + 0x214),iVar1,local_28,local_2c);
      }
      bVar10 = iVar4 != 0 || bVar10;
      *(undefined4 *)(param_1 + 0x60) = *(undefined4 *)(iVar1 + 0x230);
      *(undefined1 *)(param_1 + 0x5d) = 0;
      *(undefined4 *)(param_1 + 0x78) = *(undefined4 *)(iVar1 + 0x224);
      *(undefined4 *)(param_1 + 0x7c) = local_28;
      *(undefined4 *)(param_1 + 0x80) = local_2c;
    }
  }
  iVar1 = FUN_005d3268(iVar6);
  if (*(int *)(param_1 + 0x58) != iVar1) {
    *(int *)(param_1 + 0x58) = iVar1;
    bVar10 = true;
  }
  *(byte *)(param_1 + 0xb8) = *(byte *)(param_1 + 0xc) & 1;
  iVar1 = FUN_004751c8(param_2,param_1 + 0x10,0x10);
  if (iVar1 != 0) {
    FUN_00439c04(param_1 + 0x10,param_2,0x18);
    *(undefined4 *)(param_1 + 0x24) = 0;
    *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x24);
    FUN_00439c04(param_1 + 0x28,param_2,0x18);
    *(undefined4 *)(param_1 + 0x4c) = 0x10000;
    *(undefined4 *)(param_1 + 0x40) = *(undefined4 *)(param_1 + 0x4c);
    *(undefined4 *)(param_1 + 0x48) = 0;
    *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_1 + 0x48);
    bVar10 = true;
  }
  if (*(byte *)(param_1 + 0xba) != (*(byte *)(param_1 + 0xc) & 2)) {
    *(byte *)(param_1 + 0xba) = *(byte *)(param_1 + 0xc) & 2;
    bVar10 = true;
  }
  if (bVar10) {
    iVar1 = *(int *)(param_1 + 0x84);
    if (iVar1 == 0) {
      iVar1 = 1000;
    }
    if (*(int *)(param_1 + 0x58) < 0x40000) {
      uVar3 = 0x40000;
    }
    else {
      uVar3 = *(undefined4 *)(param_1 + 0x58);
    }
    iVar9 = 0x3e80000 / iVar1;
    uVar5 = FUN_005d3272(iVar6);
    *(undefined4 *)(param_1 + 0xdc) = uVar5;
    if (*(int *)(param_1 + 0xdc) < 1) {
      uVar5 = FT_DivFix(0x4b0000,iVar9);
      *(undefined4 *)(param_1 + 0xdc) = uVar5;
    }
    if (iVar7 < 1) {
      FUN_005d2a18(iVar9,uVar3,*(undefined4 *)(param_1 + 0xdc),param_1 + 0xe4,0,
                   *(undefined1 *)(param_1 + 0xba),param_1 + 0xbc);
    }
    else {
      iVar4 = FT_DivFix(iVar1 << 0x10,uVar3);
      if (iVar7 <= iVar4) {
        iVar7 = FT_DivFix(iVar1 << 0x10,uVar3);
      }
      FUN_005d2a18(iVar9,uVar3,*(undefined4 *)(param_1 + 0xdc),param_1 + 0xe4,iVar7,0,param_1 + 0xbc
                  );
    }
    iVar1 = FUN_005d327e(iVar6);
    if ((iVar1 < 1) || (*(int *)(param_1 + 0xdc) <= iVar1 * 2)) {
      uVar5 = FT_DivFix(s_D__01_workspace_s200_ap510b_iar__006dffb4 + 0x4c,iVar9);
      *(undefined4 *)(param_1 + 0xe0) = uVar5;
    }
    else {
      uVar5 = FT_DivFix(0x4b0000,iVar9);
      *(undefined4 *)(param_1 + 0xe0) = uVar5;
    }
    FUN_005d2a18(iVar9,uVar3,*(undefined4 *)(param_1 + 0xe0),param_1 + 0xe8,uVar8,
                 *(undefined1 *)(param_1 + 0xba),param_1 + 0xbc);
    if ((*(int *)(param_1 + 0xe4) == 0) && (*(int *)(param_1 + 0xe8) == 0)) {
      *(undefined1 *)(param_1 + 0xb9) = 0;
    }
    else {
      *(undefined1 *)(param_1 + 0xb9) = 1;
    }
    *(undefined1 *)(param_1 + 0xec) = 0;
    FUN_005d2418(param_1 + 0xf0,param_1);
  }
  return;
}

