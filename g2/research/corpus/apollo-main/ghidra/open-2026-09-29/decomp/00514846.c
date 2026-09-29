
int FUN_00514846(undefined4 param_1,undefined4 param_2)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int local_38;
  int iStack_34;
  int iStack_30;
  int iStack_2c;
  
  piVar2 = DAT_00514b78;
  iVar6 = *DAT_00514b78;
  iVar3 = *(int *)(iVar6 + 4);
  if (iVar3 == 0) {
    FUN_00523e92(param_1,param_2);
    return 0;
  }
  piVar5 = (int *)(iVar3 + 0x10);
  *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) & 0xfffffff7;
  if ((int)((uint)*(byte *)(iVar3 + 0x18) << 0x1a) < 0) {
    iVar8 = *(int *)(iVar3 + 0x2c);
    iVar8 = iVar8 * (*(int *)(iVar3 + 0x14) / iVar8) + (iVar8 - *(int *)(iVar3 + 0x14));
  }
  else {
    iVar8 = *piVar5 - *(int *)(iVar3 + 0x14);
  }
  if (*(int *)(iVar3 + 0x18) << 0x1a < 0) {
    if (iVar8 / 2 < 2) {
      *(undefined1 *)(iVar6 + 0xf9) = 0;
      FUN_005147b0(*(undefined4 *)(*piVar2 + 4));
    }
  }
  else if (*(int *)(iVar3 + 0x18) << 0x1e < 0) {
    if (*piVar5 <= *(int *)(iVar3 + 0x14) + 4) {
      if ((int)((uint)*(byte *)(iVar3 + 0x18) << 0x1a) < 0) {
        iVar6 = *(int *)(iVar3 + 0x2c);
        iVar6 = iVar6 * (*(int *)(iVar3 + 0x14) / iVar6) + (iVar6 - *(int *)(iVar3 + 0x14));
      }
      else {
        iVar6 = *piVar5 - *(int *)(iVar3 + 0x14);
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
      piVar5 = *(int **)(iVar3 + 0x20);
      if (piVar5 == (int *)0x0) {
        piVar5 = (int *)FUN_0051416c(0x3c);
        if (piVar5 == (int *)0x0) {
          uVar4 = 0x10;
          goto LAB_005148ea;
        }
        FUN_00514070(&local_38,0,0x400);
        *piVar5 = local_38;
        piVar5[1] = iStack_34;
        piVar5[2] = iStack_30;
        piVar5[3] = iStack_2c;
        piVar5[4] = ((int)(local_38 + ((uint)(local_38 >> 2) >> 0x1d)) >> 3) << 1;
        piVar5[5] = 0;
        piVar5[7] = -1;
        piVar5[0xd] = -1;
        piVar5[0xe] = -1;
        piVar5[6] = 2;
        piVar5[8] = 0;
        piVar5[9] = 0;
        piVar5[10] = 0;
        piVar5[0xb] = 0;
        piVar5[0xc] = 0;
        if (piVar5[2] == 0) {
          FUN_004b127c(0x10);
          iVar3 = FUN_00514178(piVar5);
          return iVar3;
        }
        iVar8 = *piVar2;
        iVar3 = *(int *)(iVar8 + 4);
        iVar6 = *(int *)(iVar3 + 0x24);
        if (iVar6 != 0) {
          iVar3 = iVar6;
        }
        piVar5[9] = iVar3;
        piVar5[6] = *(uint *)(*(int *)(iVar8 + 4) + 0x18) & 0xfffffff3;
      }
      iVar3 = *(int *)(*piVar2 + 4);
      if (iVar3 == 0) {
        FUN_004b127c(0x2000);
      }
      else {
        *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) | 4;
      }
      iVar3 = *piVar2;
      iVar6 = *(int *)(iVar3 + 4);
      iVar8 = *(int *)(iVar6 + 0x14);
      *(undefined4 *)(*(int *)(iVar6 + 8) + iVar8 * 4) = 0xf0;
      *(int *)(*(int *)(iVar6 + 8) + (iVar8 + 1) * 4) = piVar5[3];
      *(int *)(iVar6 + 0x14) = iVar8 + 2;
      *(undefined4 *)(*(int *)(iVar6 + 8) + (iVar8 + 2) * 4) = 0xf4;
      *(int *)(*(int *)(iVar6 + 8) + (iVar8 + 3) * 4) = piVar5[4];
      *(int *)(iVar6 + 0x14) = iVar8 + 4;
      *(int **)(iVar6 + 0x20) = piVar5;
      if (piVar5 == (int *)0x0) {
        uVar4 = 0x2000;
      }
      else {
        if ((*(byte *)(piVar5 + 3) & 7) == 0) {
          if (*(int *)(iVar3 + 4) != 0) {
            FUN_005144ba();
          }
          bVar1 = *(byte *)(piVar5 + 6);
          while (((((int)((uint)bVar1 << 0x1d) < 0 &&
                   (piVar5 = (int *)piVar5[8], (int)((uint)*(byte *)(piVar5 + 6) << 0x1d) < 0)) &&
                  (piVar5 = (int *)piVar5[8], (int)((uint)*(byte *)(piVar5 + 6) << 0x1d) < 0)) &&
                 (piVar5 = (int *)piVar5[8], (int)((uint)*(byte *)(piVar5 + 6) << 0x1d) < 0))) {
            piVar5 = (int *)piVar5[8];
            bVar1 = *(byte *)(piVar5 + 6);
          }
          *(int **)(*piVar2 + 4) = piVar5;
          goto LAB_005148bc;
        }
        uVar4 = 0x4000;
      }
      FUN_004b127c(uVar4);
    }
  }
  else if (*piVar5 < *(int *)(iVar3 + 0x14) + 2) {
    uVar4 = 8;
LAB_005148ea:
    iVar3 = FUN_004b127c(uVar4);
    return iVar3;
  }
LAB_005148bc:
  iVar3 = *(int *)(*piVar2 + 4);
  iVar6 = *(int *)(iVar3 + 0x14);
  *(undefined4 *)(*(int *)(iVar3 + 8) + iVar6 * 4) = param_1;
  *(undefined4 *)(*(int *)(iVar3 + 8) + (iVar6 + 1) * 4) = param_2;
  *(int *)(iVar3 + 0x14) = iVar6 + 2;
  return iVar3;
}

