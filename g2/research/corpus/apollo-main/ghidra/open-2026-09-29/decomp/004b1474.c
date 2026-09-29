
uint FUN_004b1474(int param_1,undefined4 param_2)

{
  byte bVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  int iStack_38;
  int iStack_34;
  int iStack_30;
  int iStack_2c;
  
  piVar2 = DAT_00514b78;
  uVar3 = param_1 * 4 + 0x200;
  if (0x20c < uVar3) {
    return uVar3;
  }
  iVar8 = *DAT_00514b78;
  iVar4 = *(int *)(iVar8 + 4);
  if (iVar4 == 0) {
    FUN_00523e92(uVar3,param_2);
    return 0;
  }
  piVar7 = (int *)(iVar4 + 0x10);
  *(uint *)(iVar4 + 0x18) = *(uint *)(iVar4 + 0x18) & 0xfffffff7;
  if ((int)((uint)*(byte *)(iVar4 + 0x18) << 0x1a) < 0) {
    iVar9 = *(int *)(iVar4 + 0x2c);
    iVar9 = iVar9 * (*(int *)(iVar4 + 0x14) / iVar9) + (iVar9 - *(int *)(iVar4 + 0x14));
  }
  else {
    iVar9 = *piVar7 - *(int *)(iVar4 + 0x14);
  }
  if (*(int *)(iVar4 + 0x18) << 0x1a < 0) {
    if (iVar9 / 2 < 2) {
      *(undefined1 *)(iVar8 + 0xf9) = 0;
      FUN_005147b0(*(undefined4 *)(*piVar2 + 4));
    }
  }
  else if (*(int *)(iVar4 + 0x18) << 0x1e < 0) {
    if (*piVar7 <= *(int *)(iVar4 + 0x14) + 4) {
      if ((int)((uint)*(byte *)(iVar4 + 0x18) << 0x1a) < 0) {
        iVar8 = *(int *)(iVar4 + 0x2c);
        iVar8 = iVar8 * (*(int *)(iVar4 + 0x14) / iVar8) + (iVar8 - *(int *)(iVar4 + 0x14));
      }
      else {
        iVar8 = *piVar7 - *(int *)(iVar4 + 0x14);
      }
      uVar5 = iVar8 / 2 - 2;
      if (0 < (int)uVar5) {
        if ((uVar5 & 3) != 0) {
          do {
            iVar8 = *(int *)(iVar4 + 0x14);
            *(undefined4 *)(*(int *)(iVar4 + 8) + iVar8 * 4) = 0x10000;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 1) * 4) = 0;
            *(int *)(iVar4 + 0x14) = iVar8 + 2;
            loopEnd();
          } while( true );
        }
        if (uVar5 >> 2 != 0) {
          iVar8 = *(int *)(iVar4 + 0x14);
          do {
            *(undefined4 *)(*(int *)(iVar4 + 8) + iVar8 * 4) = 0x10000;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 1) * 4) = 0;
            *(int *)(iVar4 + 0x14) = iVar8 + 2;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 2) * 4) = 0x10000;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 3) * 4) = 0;
            *(int *)(iVar4 + 0x14) = iVar8 + 4;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 4) * 4) = 0x10000;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 5) * 4) = 0;
            *(int *)(iVar4 + 0x14) = iVar8 + 6;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 6) * 4) = 0x10000;
            *(undefined4 *)(*(int *)(iVar4 + 8) + (iVar8 + 7) * 4) = 0;
            iVar8 = iVar8 + 8;
            *(int *)(iVar4 + 0x14) = iVar8;
            loopEnd();
          } while( true );
        }
      }
      piVar7 = *(int **)(iVar4 + 0x20);
      if (piVar7 == (int *)0x0) {
        piVar7 = (int *)FUN_0051416c(0x3c);
        if (piVar7 == (int *)0x0) {
          uVar6 = 0x10;
          goto LAB_005148ea;
        }
        FUN_00514070(&iStack_38,0,0x400);
        *piVar7 = iStack_38;
        piVar7[1] = iStack_34;
        piVar7[2] = iStack_30;
        piVar7[3] = iStack_2c;
        piVar7[4] = ((int)(iStack_38 + ((uint)(iStack_38 >> 2) >> 0x1d)) >> 3) << 1;
        piVar7[5] = 0;
        piVar7[7] = -1;
        piVar7[0xd] = -1;
        piVar7[0xe] = -1;
        piVar7[6] = 2;
        piVar7[8] = 0;
        piVar7[9] = 0;
        piVar7[10] = 0;
        piVar7[0xb] = 0;
        piVar7[0xc] = 0;
        if (piVar7[2] == 0) {
          FUN_004b127c(0x10);
          uVar3 = FUN_00514178(piVar7);
          return uVar3;
        }
        iVar9 = *piVar2;
        iVar4 = *(int *)(iVar9 + 4);
        iVar8 = *(int *)(iVar4 + 0x24);
        if (iVar8 != 0) {
          iVar4 = iVar8;
        }
        piVar7[9] = iVar4;
        piVar7[6] = *(uint *)(*(int *)(iVar9 + 4) + 0x18) & 0xfffffff3;
      }
      iVar4 = *(int *)(*piVar2 + 4);
      if (iVar4 == 0) {
        FUN_004b127c(0x2000);
      }
      else {
        *(uint *)(iVar4 + 0x18) = *(uint *)(iVar4 + 0x18) | 4;
      }
      iVar4 = *piVar2;
      iVar8 = *(int *)(iVar4 + 4);
      iVar9 = *(int *)(iVar8 + 0x14);
      *(undefined4 *)(*(int *)(iVar8 + 8) + iVar9 * 4) = 0xf0;
      *(int *)(*(int *)(iVar8 + 8) + (iVar9 + 1) * 4) = piVar7[3];
      *(int *)(iVar8 + 0x14) = iVar9 + 2;
      *(undefined4 *)(*(int *)(iVar8 + 8) + (iVar9 + 2) * 4) = 0xf4;
      *(int *)(*(int *)(iVar8 + 8) + (iVar9 + 3) * 4) = piVar7[4];
      *(int *)(iVar8 + 0x14) = iVar9 + 4;
      *(int **)(iVar8 + 0x20) = piVar7;
      if (piVar7 == (int *)0x0) {
        uVar6 = 0x2000;
      }
      else {
        if ((*(byte *)(piVar7 + 3) & 7) == 0) {
          if (*(int *)(iVar4 + 4) != 0) {
            FUN_005144ba();
          }
          bVar1 = *(byte *)(piVar7 + 6);
          while (((((int)((uint)bVar1 << 0x1d) < 0 &&
                   (piVar7 = (int *)piVar7[8], (int)((uint)*(byte *)(piVar7 + 6) << 0x1d) < 0)) &&
                  (piVar7 = (int *)piVar7[8], (int)((uint)*(byte *)(piVar7 + 6) << 0x1d) < 0)) &&
                 (piVar7 = (int *)piVar7[8], (int)((uint)*(byte *)(piVar7 + 6) << 0x1d) < 0))) {
            piVar7 = (int *)piVar7[8];
            bVar1 = *(byte *)(piVar7 + 6);
          }
          *(int **)(*piVar2 + 4) = piVar7;
          goto LAB_005148bc;
        }
        uVar6 = 0x4000;
      }
      FUN_004b127c(uVar6);
    }
  }
  else if (*piVar7 < *(int *)(iVar4 + 0x14) + 2) {
    uVar6 = 8;
LAB_005148ea:
    uVar3 = FUN_004b127c(uVar6);
    return uVar3;
  }
LAB_005148bc:
  uVar5 = *(uint *)(*piVar2 + 4);
  iVar4 = *(int *)(uVar5 + 0x14);
  *(uint *)(*(int *)(uVar5 + 8) + iVar4 * 4) = uVar3;
  *(undefined4 *)(*(int *)(uVar5 + 8) + (iVar4 + 1) * 4) = param_2;
  *(int *)(uVar5 + 0x14) = iVar4 + 2;
  return uVar5;
}

