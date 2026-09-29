
void FUN_0049a16e(undefined4 param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  int *piVar9;
  byte bVar10;
  
  cVar1 = FUN_004516f8(PTR_PTR_0049ab9c,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    iVar3 = *param_2;
    if ((iVar2 == 0x32) || (iVar2 == 0x31)) {
      FUN_0049a602(iVar3);
    }
    else if (iVar2 == 0x1b) {
      iVar2 = FUN_004993c0(iVar3,0);
      FUN_004519fa(param_2,*(int *)(iVar2 + 0xc) / 4);
    }
    else if (iVar2 == 0x34) {
      if (*(char *)(iVar3 + 0x5c) < '\0') {
        uVar4 = FUN_004993c0(iVar3,0);
        uVar5 = FUN_004993ca(iVar3,0);
        uVar6 = FUN_004993d4(iVar3,0);
        bVar10 = 0;
        if ((*(byte *)(iVar3 + 0x5c) & 0x3f) >> 5 != 0) {
          bVar10 = 8;
        }
        if ((*(byte *)(iVar3 + 0x5c) & 0x7f) >> 6 != 0) {
          bVar10 = bVar10 | 1;
        }
        iVar2 = FUN_00499360(iVar3,0);
        if ((iVar2 == 0x3fffffff) && ((*(ushort *)(iVar3 + 0x2a) & 0xfff) >> 0xb == 0)) {
          iVar2 = 0x1fffffff;
        }
        else {
          iVar2 = FUN_0043fe16(iVar3);
        }
        iVar7 = FUN_0049936a(iVar3,0);
        if (iVar7 <= iVar2) {
          iVar2 = FUN_0049936a(iVar3,0);
        }
        uVar8 = *(undefined4 *)(iVar3 + 0x34);
        FUN_0049aacc(iVar3);
        FUN_00489546(iVar3 + 0x4c,*(undefined4 *)(iVar3 + 0x2c),uVar4,uVar5,uVar6,iVar2,bVar10);
        FUN_0049ab06(iVar3,uVar8);
        iVar2 = FUN_00499374(iVar3,0);
        if (*(int *)(iVar3 + 0x50) < iVar2) {
          uVar4 = *(undefined4 *)(iVar3 + 0x50);
        }
        else {
          uVar4 = FUN_00499374(iVar3,0);
        }
        *(undefined4 *)(iVar3 + 0x50) = uVar4;
        *(byte *)(iVar3 + 0x5c) = *(byte *)(iVar3 + 0x5c) & 0x7f;
      }
      piVar9 = (int *)param_2[4];
      if (*(int *)(iVar3 + 0x4c) < *piVar9) {
        iVar2 = *piVar9;
      }
      else {
        iVar2 = *(int *)(iVar3 + 0x4c);
      }
      *piVar9 = iVar2;
      if (*(int *)(iVar3 + 0x50) < piVar9[1]) {
        iVar2 = piVar9[1];
      }
      else {
        iVar2 = *(int *)(iVar3 + 0x50);
      }
      piVar9[1] = iVar2;
    }
    else if (iVar2 == 0x1d) {
      FUN_0049a31c(param_2);
    }
  }
  return;
}

