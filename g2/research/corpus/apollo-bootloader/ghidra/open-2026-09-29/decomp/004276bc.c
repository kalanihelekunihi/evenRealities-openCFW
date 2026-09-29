
void memmove_4276bc(undefined4 *param_1,undefined4 *param_2,uint param_3,undefined4 *param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined2 *puVar3;
  undefined1 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  bool bVar13;
  bool bVar14;
  
  if (param_2 < param_1) {
    param_4 = (undefined4 *)(param_3 + (int)param_2);
  }
  if (param_2 < param_1 && param_1 < param_4) {
    param_1 = (undefined4 *)((int)param_1 + param_3);
    do {
      if (((uint)param_4 & 3) == 0) {
        if (((uint)param_1 & 3) == 0) {
          while (0xf < param_3) {
            puVar5 = param_4 + -1;
            uVar11 = param_4[-2];
            uVar10 = param_4[-3];
            param_4 = param_4 + -4;
            uVar9 = *param_4;
            param_1[-1] = *puVar5;
            param_1[-2] = uVar11;
            param_1[-3] = uVar10;
            param_1 = param_1 + -4;
            *param_1 = uVar9;
            param_3 = param_3 - 0x10;
          }
          do {
            bVar13 = 3 < param_3;
            param_3 = param_3 - 4;
            if (bVar13) {
              param_4 = param_4 + -1;
              param_1 = param_1 + -1;
              *param_1 = *param_4;
            }
          } while (bVar13 && param_3 != 0);
        }
        else {
          bVar14 = 3 < param_3;
          param_3 = param_3 - 4;
          bVar13 = false;
          if (bVar14) {
            puVar5 = param_1;
            if (((uint)param_1 & 1) == 0) {
              do {
                param_4 = param_4 + -1;
                uVar9 = *param_4;
                bVar13 = 3 < param_3;
                param_3 = param_3 - 4;
                param_1 = puVar5 + -1;
                *(short *)param_1 = (short)uVar9;
                *(short *)((int)puVar5 + -2) = (short)((uint)uVar9 >> 0x10);
                puVar5 = param_1;
              } while (bVar13);
              bVar13 = false;
            }
            else {
              do {
                param_4 = param_4 + -1;
                uVar9 = *param_4;
                bVar13 = 3 < param_3;
                param_3 = param_3 - 4;
                param_1 = puVar5 + -1;
                *(char *)param_1 = (char)uVar9;
                *(short *)((int)puVar5 + -3) = (short)((uint)uVar9 >> 8);
                *(char *)((int)puVar5 + -1) = (char)((uint)uVar9 >> 0x18);
                puVar5 = param_1;
              } while (bVar13);
              bVar13 = false;
            }
          }
        }
        if (!bVar13) {
          param_3 = param_3 + 4;
        }
        do {
          bVar13 = param_3 != 0;
          param_3 = param_3 - 1;
          if (bVar13) {
            param_4 = (undefined4 *)((int)param_4 + -1);
            param_1 = (undefined4 *)((int)param_1 + -1);
            *(undefined1 *)param_1 = *(undefined1 *)param_4;
          }
        } while (bVar13 && param_3 != 0);
        return;
      }
      bVar13 = param_3 != 0;
      param_3 = param_3 - 1;
      if (bVar13) {
        param_4 = (undefined4 *)((int)param_4 + -1);
        param_1 = (undefined4 *)((int)param_1 + -1);
        *(undefined1 *)param_1 = *(undefined1 *)param_4;
      }
    } while (bVar13 && param_3 != 0);
    return;
  }
  while( true ) {
    if (param_3 == 0) {
      return;
    }
    if (((uint)param_2 & 3) == 0) break;
    param_3 = param_3 - 1;
    *(undefined1 *)param_1 = *(undefined1 *)param_2;
    param_1 = (undefined4 *)((int)param_1 + 1);
    param_2 = (undefined4 *)((int)param_2 + 1);
  }
  if (((uint)param_1 & 3) == 0) {
    while (uVar7 = param_3 - 0x10, 0xf < param_3) {
      uVar9 = *param_2;
      uVar10 = param_2[1];
      uVar11 = param_2[2];
      uVar12 = param_2[3];
      param_2 = param_2 + 4;
      *param_1 = uVar9;
      param_1[1] = uVar10;
      param_1[2] = uVar11;
      param_1[3] = uVar12;
      param_1 = param_1 + 4;
      param_3 = uVar7;
    }
    if ((uVar7 & 8) != 0) {
      uVar9 = *param_2;
      uVar10 = param_2[1];
      param_2 = param_2 + 2;
      *param_1 = uVar9;
      param_1[1] = uVar10;
      param_1 = param_1 + 2;
    }
    puVar1 = param_1;
    puVar5 = param_2;
    if ((int)(param_3 << 0x1d) < 0) {
      puVar5 = param_2 + 1;
      puVar1 = param_1 + 1;
      *param_1 = *param_2;
    }
    puVar2 = puVar1;
    puVar6 = puVar5;
    if ((uVar7 & 2) != 0) {
      puVar6 = (undefined4 *)((int)puVar5 + 2);
      puVar2 = (undefined4 *)((int)puVar1 + 2);
      *(undefined2 *)puVar1 = *(undefined2 *)puVar5;
    }
    if ((int)(param_3 << 0x1f) < 0) {
      *(undefined1 *)puVar2 = *(undefined1 *)puVar6;
    }
    return;
  }
  uVar7 = param_3 - 4;
  if (3 < param_3) {
    puVar5 = param_2;
    if (((uint)param_1 & 1) == 0) {
      do {
        param_2 = puVar5 + 1;
        uVar9 = *puVar5;
        puVar3 = (undefined2 *)((int)param_1 + 2);
        *(short *)param_1 = (short)uVar9;
        bVar13 = 3 < uVar7;
        uVar7 = uVar7 - 4;
        param_1 = param_1 + 1;
        *puVar3 = (short)((uint)uVar9 >> 0x10);
        puVar5 = param_2;
      } while (bVar13);
    }
    else {
      do {
        param_2 = puVar5 + 1;
        uVar9 = *puVar5;
        *(char *)param_1 = (char)uVar9;
        puVar4 = (undefined1 *)((int)param_1 + 3);
        *(short *)((int)param_1 + 1) = (short)((uint)uVar9 >> 8);
        bVar13 = 3 < uVar7;
        uVar7 = uVar7 - 4;
        param_1 = param_1 + 1;
        *puVar4 = (char)((uint)uVar9 >> 0x18);
        puVar5 = param_2;
      } while (bVar13);
    }
  }
  iVar8 = uVar7 + 4;
  do {
    bVar13 = iVar8 != 0;
    iVar8 = iVar8 + -1;
    puVar5 = param_1;
    if (bVar13) {
      puVar5 = (undefined4 *)((int)param_1 + 1);
      *(undefined1 *)param_1 = *(undefined1 *)param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
    }
    param_1 = puVar5;
  } while (bVar13 && iVar8 != 0);
  return;
}

