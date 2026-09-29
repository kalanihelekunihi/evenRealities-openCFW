
undefined4 FUN_00514504(int param_1)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int *piVar9;
  int local_30;
  int iStack_2c;
  int iStack_28;
  int iStack_24;
  
  piVar2 = DAT_00514b78;
  iVar3 = *(int *)(*DAT_00514b78 + 4);
  if (iVar3 == 0) {
    FUN_004b127c(0x80);
    return 0xffffffff;
  }
  if (-1 < (int)((uint)*(byte *)(iVar3 + 0x18) << 0x1e)) {
    FUN_004b127c(8);
    return 0xffffffff;
  }
  if ((int)((uint)*(byte *)(iVar3 + 0x18) << 0x1a) < 0) {
    iVar6 = *(int *)(iVar3 + 0x2c);
    iVar6 = iVar6 * (*(int *)(iVar3 + 0x14) / iVar6) + (iVar6 - *(int *)(iVar3 + 0x14));
  }
  else {
    iVar6 = *(int *)(iVar3 + 0x10) - *(int *)(iVar3 + 0x14);
  }
  uVar7 = iVar6 / 2 - 2;
  if (0 < (int)uVar7) {
    if ((uVar7 & 3) != 0) {
      do {
        iVar6 = *(int *)(iVar3 + 0x14);
        *(undefined4 *)(*(int *)(iVar3 + 8) + iVar6 * 4) = 0x10000;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 1) * 4) = 0;
        *(int *)(iVar3 + 0x14) = iVar6 + 2;
        loopEnd();
      } while( true );
    }
    if (uVar7 >> 2 != 0) {
      iVar6 = *(int *)(iVar3 + 0x14);
      do {
        *(undefined4 *)(*(int *)(iVar3 + 8) + iVar6 * 4) = 0x10000;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 1) * 4) = 0;
        *(int *)(iVar3 + 0x14) = iVar6 + 2;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 2) * 4) = 0x10000;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 3) * 4) = 0;
        *(int *)(iVar3 + 0x14) = iVar6 + 4;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 4) * 4) = 0x10000;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 5) * 4) = 0;
        *(int *)(iVar3 + 0x14) = iVar6 + 6;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 6) * 4) = 0x10000;
        *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 7) * 4) = 0;
        iVar6 = iVar6 + 8;
        *(int *)(iVar3 + 0x14) = iVar6;
        loopEnd();
      } while( true );
    }
  }
  piVar9 = *(int **)(iVar3 + 0x20);
  if (piVar9 == (int *)0x0) {
    piVar9 = (int *)FUN_0051416c(0x3c);
    if (piVar9 == (int *)0x0) {
      FUN_004b127c(0x10);
      return 0xffffffff;
    }
    if ((param_1 + 2) * 8 < 0x401) {
      FUN_00514070(&local_30,0,0x400);
      *piVar9 = local_30;
      piVar9[1] = iStack_2c;
      piVar9[2] = iStack_28;
      piVar9[3] = iStack_24;
      piVar9[4] = ((int)(local_30 + ((uint)(local_30 >> 2) >> 0x1d)) >> 3) << 1;
      piVar9[5] = 0;
      piVar9[6] = 2;
    }
    else {
      FUN_00514070(&local_30,0);
      *piVar9 = local_30;
      piVar9[1] = iStack_2c;
      piVar9[2] = iStack_28;
      piVar9[3] = iStack_24;
      piVar9[4] = ((int)(local_30 + ((uint)(local_30 >> 2) >> 0x1d)) >> 3) << 1;
      piVar9[5] = 0;
      piVar9[6] = 0;
    }
    piVar9[9] = 0;
    piVar9[7] = -1;
    piVar9[0xd] = -1;
    piVar9[0xe] = -1;
    piVar9[10] = 0;
    piVar9[0xb] = 0;
    piVar9[0xc] = 0;
    piVar9[8] = 0;
    if (piVar9[2] == 0) {
      FUN_004b127c(0x10);
      FUN_00514178(piVar9);
      return 0xffffffff;
    }
    iVar5 = *piVar2;
    iVar3 = *(int *)(iVar5 + 4);
    iVar6 = *(int *)(iVar3 + 0x24);
    if (iVar6 != 0) {
      iVar3 = iVar6;
    }
    piVar9[9] = iVar3;
    piVar9[6] = *(uint *)(*(int *)(iVar5 + 4) + 0x18) & 0xfffffff3;
  }
  iVar3 = *(int *)(*piVar2 + 4);
  if (iVar3 == 0) {
    FUN_004b127c(0x2000);
  }
  else {
    *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) | 4;
  }
  iVar6 = *piVar2;
  iVar3 = *(int *)(iVar6 + 4);
  iVar5 = *(int *)(iVar3 + 0x14);
  *(undefined4 *)(*(int *)(iVar3 + 8) + iVar5 * 4) = 0xf0;
  *(int *)(*(int *)(iVar3 + 8) + (iVar5 + 1) * 4) = piVar9[3];
  *(int *)(iVar3 + 0x14) = iVar5 + 2;
  *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar5 + 2) * 4) = 0xf4;
  *(int *)(*(int *)(iVar3 + 8) + (iVar5 + 3) * 4) = piVar9[4];
  *(int *)(iVar3 + 0x14) = iVar5 + 4;
  *(int **)(iVar3 + 0x20) = piVar9;
  if (piVar9 == (int *)0x0) {
    uVar4 = 0x2000;
  }
  else {
    if ((*(byte *)(piVar9 + 3) & 7) == 0) {
      iVar3 = *(int *)(iVar6 + 4);
      if (iVar3 != 0) {
        iVar5 = *(int *)(iVar3 + 0x14);
        if (iVar5 + 2 <= *(int *)(iVar3 + 0x10)) {
          iVar8 = *(int *)(iVar3 + 8);
          *(undefined4 *)(iVar8 + iVar5 * 4) = 0x50000;
          *(undefined4 *)(iVar8 + 4 + iVar5 * 4) = 0;
          *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) & 0xfffffff7;
        }
        *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) & 0xffffffdf;
        *(undefined4 *)(iVar6 + 4) = 0;
      }
      bVar1 = *(byte *)(piVar9 + 6);
      while (((((int)((uint)bVar1 << 0x1d) < 0 &&
               (piVar9 = (int *)piVar9[8], (int)((uint)*(byte *)(piVar9 + 6) << 0x1d) < 0)) &&
              (piVar9 = (int *)piVar9[8], (int)((uint)*(byte *)(piVar9 + 6) << 0x1d) < 0)) &&
             (piVar9 = (int *)piVar9[8], (int)((uint)*(byte *)(piVar9 + 6) << 0x1d) < 0))) {
        piVar9 = (int *)piVar9[8];
        bVar1 = *(byte *)(piVar9 + 6);
      }
      *(int **)(iVar6 + 4) = piVar9;
      return 0;
    }
    uVar4 = 0x4000;
  }
  FUN_004b127c(uVar4);
  return 0;
}

