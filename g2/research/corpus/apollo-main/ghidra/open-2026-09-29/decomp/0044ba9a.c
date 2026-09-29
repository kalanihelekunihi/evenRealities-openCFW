
undefined4 FUN_0044ba9a(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined4 *puVar8;
  char cVar9;
  uint uVar10;
  
  sVar2 = FUN_0044b85c(param_3);
  iVar4 = FUN_0044b860(param_3);
  cVar9 = -1;
  if ((param_2 != 0) && (*(char *)(param_2 + 8) == '\0')) {
    cVar9 = '\0';
  }
  if (((param_2 != 0) && (iVar4 == 0)) && (iVar5 = FUN_0044ce2c(param_2,0x20), iVar5 != 0)) {
    FUN_00440656(param_1);
  }
  uVar10 = 0;
  bVar1 = false;
  while (uVar10 < (*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4) {
    sVar3 = FUN_0044b85c(*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0xffffff);
    iVar5 = FUN_0044b860(*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0xffffff);
    if ((((sVar2 == -1) || (sVar3 == sVar2)) && ((iVar4 == 0xf0000 || (iVar5 == iVar4)))) &&
       ((param_2 == 0 || (param_2 == *(int *)(*(int *)(param_1 + 0xc) + uVar10 * 8))))) {
      if (*(int *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) << 6 < 0) {
        FUN_0044ca18(param_1,iVar4,0xff,0);
      }
      uVar7 = uVar10;
      if ((*(uint *)(*(int *)(param_1 + 0xc) + uVar10 * 8 + 4) & 0x3000000) != 0) {
        if (*(int *)(*(int *)(param_1 + 0xc) + uVar10 * 8) != 0) {
          FUN_00482796(*(undefined4 *)(*(int *)(param_1 + 0xc) + uVar10 * 8));
        }
        FUN_0044f758(*(undefined4 *)(*(int *)(param_1 + 0xc) + uVar10 * 8));
        *(undefined4 *)(*(int *)(param_1 + 0xc) + uVar10 * 8) = 0;
      }
      for (; uVar7 < ((*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4) - 1; uVar7 = uVar7 + 1) {
        iVar5 = *(int *)(param_1 + 0xc) + uVar7 * 8;
        uVar6 = *(undefined4 *)(iVar5 + 0xc);
        puVar8 = (undefined4 *)(*(int *)(param_1 + 0xc) + uVar7 * 8);
        *puVar8 = *(undefined4 *)(iVar5 + 8);
        puVar8[1] = uVar6;
      }
      *(ushort *)(param_1 + 0x2a) =
           *(ushort *)(param_1 + 0x2a) & 0xfc0f |
           ((*(ushort *)(param_1 + 0x2a) >> 4) - 1 & 0x3f) << 4;
      uVar6 = FUN_0044f76a(*(undefined4 *)(param_1 + 0xc),
                           ((*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4) << 3);
      *(undefined4 *)(param_1 + 0xc) = uVar6;
      bVar1 = true;
    }
    else {
      uVar10 = uVar10 + 1;
    }
  }
  if ((bVar1) && (cVar9 != '\0')) {
    FUN_0044ce2a(param_1,iVar4);
    FUN_0044bc8c(param_1,iVar4,cVar9);
  }
  return param_4;
}

