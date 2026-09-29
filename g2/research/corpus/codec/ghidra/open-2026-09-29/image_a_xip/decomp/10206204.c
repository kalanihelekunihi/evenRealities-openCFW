
undefined4 gx8002_dw_spi_quick_transfer(int *param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  undefined4 *puVar5;
  uint *puVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  int *piVar13;
  uint uVar14;
  uint uVar15;
  
  uVar8 = 0;
  iVar7 = *(int *)(*param_1 + 0x18);
  *(undefined4 *)(param_2 + 0x18) = 0;
  iVar9 = *(int *)(iVar7 + 0x10);
  *(int **)(param_2 + 8) = param_1;
  if (iVar9 == 0) {
    *(int *)(iVar7 + 0x10) = param_2;
    func_0x10025080(0xe,1);
    piVar13 = (int *)**(int **)(iVar7 + 0x10);
    while (piVar13 != (int *)*(int *)(iVar7 + 0x10)) {
      puVar6 = (uint *)(piVar13 + -6);
      iVar9 = *(int *)(*(int *)(iVar7 + 0x10) + 8);
      *(uint **)(iVar7 + 0x14) = puVar6;
      iVar9 = *(int *)(iVar9 + 0xc);
      puVar5 = (undefined4 *)*puVar6;
      if (puVar5 == (undefined4 *)0x0) {
        puVar5 = (undefined4 *)piVar13[-5];
      }
      uVar8 = piVar13[-4];
      *(undefined4 **)(iVar7 + 0x18) = puVar5;
      *(undefined4 *)(iVar7 + 0x1c) = uVar8;
      if (*(byte *)((int)piVar13 + -0xb) == 0) {
        *(undefined1 *)((int)piVar13 + -0xb) = 8;
        *(undefined1 *)(iVar7 + 0x28) = 1;
      }
      else {
        uVar4 = *(byte *)((int)piVar13 + -0xb) + 7 & 0xf8;
        if (uVar4 == 0x18) {
          uVar4 = 0x20;
        }
        *(char *)(iVar7 + 0x28) = (char)(uVar4 >> 3);
      }
      bVar1 = *(byte *)((int)piVar13 + -0xb);
      uVar14 = *puVar6;
      uVar2 = *(uint *)(iVar9 + 4);
      *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 0;
      uVar4 = 0x800;
      if (uVar14 != 0) {
        uVar4 = 0x400;
      }
      *(undefined4 *)(*(int *)(iVar7 + 4) + 0xf0) = *(undefined4 *)(iVar9 + 0xc);
      **(uint **)(iVar7 + 4) = bVar1 - 1 | uVar2 | uVar4;
      if ((*(uint *)(iVar9 + 8) & 0xffff) < 2) {
        uVar4 = 2;
      }
      else {
        uVar4 = *(uint *)(iVar9 + 8) & 0x7fff;
      }
      *(uint *)(*(int *)(iVar7 + 4) + 0x14) = uVar4;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 4) = 0;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 0x4c) = 0;
      uVar4 = (uint)*(byte *)(iVar7 + 0x28);
      uVar2 = *(uint *)(iVar7 + 0x1c) / uVar4;
      uVar15 = *(int *)(iVar7 + 0xc) * 2 - 1;
      if ((*(uint *)(iVar7 + 0x1c) != uVar2 * uVar4) ||
         (puVar5 != (undefined4 *)(uVar4 * ((uint)puVar5 / uVar4)))) {
        uVar8 = 0xffffffea;
        goto LAB_1020625a;
      }
      *(undefined4 *)(iVar7 + 0x20) = 0;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 0;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 0x10) = 1;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 0x4c) = 0;
      puVar11 = puVar5;
      puVar12 = puVar5;
      if (uVar14 == 0) {
        for (; uVar2 != 0; uVar2 = uVar2 - iVar3) {
          *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 0;
          uVar14 = *(uint *)(iVar7 + 0xc);
          iVar3 = (uVar2 < uVar14) * uVar14 + (uVar2 >= uVar14) * uVar14;
          *(int *)(*(int *)(iVar7 + 4) + 4) = iVar3 + -1;
          *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 1;
          *(undefined4 *)(*(int *)(iVar7 + 4) + 0x60) = 0;
          for (iVar9 = iVar3; iVar9 != 0; iVar9 = iVar9 - uVar14) {
            uVar14 = uVar15 & *(uint *)(*(int *)(iVar7 + 4) + 0x24);
            for (iVar10 = 0; iVar10 < (int)uVar14; iVar10 = iVar10 + 1) {
              if (uVar4 == 1) {
                *(char *)puVar11 = (char)*(undefined4 *)(*(int *)(iVar7 + 4) + 0x60);
                puVar11 = (undefined4 *)((int)puVar11 + 1);
              }
              else if (uVar4 == 2) {
                *(short *)puVar12 = (short)*(undefined4 *)(*(int *)(iVar7 + 4) + 0x60);
                puVar12 = (undefined4 *)((int)puVar12 + 2);
              }
              else if (uVar4 == 4) {
                *puVar5 = *(undefined4 *)(*(int *)(iVar7 + 4) + 0x60);
                puVar5 = puVar5 + 1;
              }
            }
          }
        }
      }
      else {
        *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 1;
        for (; uVar2 != 0; uVar2 = uVar2 - iVar9) {
          iVar9 = *(int *)(iVar7 + 8) - (uVar15 & *(uint *)(*(int *)(iVar7 + 4) + 0x20));
          iVar9 = (uint)(iVar9 < (int)uVar2) * iVar9 + (iVar9 >= (int)uVar2) * uVar2;
          *(int *)(*(int *)(iVar7 + 4) + 4) = iVar9 + -1;
          for (iVar3 = 0; iVar9 != iVar3; iVar3 = iVar3 + 1) {
            if (uVar4 == 1) {
              iVar10 = *(int *)(iVar7 + 4);
              uVar14 = (uint)*(byte *)((int)puVar11 + iVar3);
LAB_102063e0:
              *(uint *)(iVar10 + 0x60) = uVar14;
            }
            else if (uVar4 == 2) {
              *(uint *)(*(int *)(iVar7 + 4) + 0x60) = (uint)*(ushort *)((int)puVar12 + iVar3 * 2);
            }
            else if (uVar4 == 4) {
              iVar10 = *(int *)(iVar7 + 4);
              uVar14 = puVar5[iVar3];
              goto LAB_102063e0;
            }
          }
          if (uVar4 == 1) {
            puVar11 = (undefined4 *)((int)puVar11 + iVar9);
          }
          else if (uVar4 == 2) {
            puVar12 = (undefined4 *)((int)puVar12 + iVar9 * 2);
          }
          else if (uVar4 == 4) {
            puVar5 = puVar5 + iVar9;
          }
        }
        puVar6 = (uint *)(*(int *)(iVar7 + 4) + 0x28);
        do {
        } while ((*puVar6 & 4) == 0);
        do {
        } while ((*puVar6 & 1) != 0);
      }
      piVar13 = (int *)*piVar13;
      *(undefined4 *)(*(int *)(iVar7 + 4) + 8) = 0;
    }
    uVar8 = 0;
LAB_1020625a:
    uRam0000008c = 3;
    func_0x10025080(0xe,0);
  }
  *(undefined4 *)(iVar7 + 0x10) = 0;
  *(undefined4 *)(iVar7 + 0x14) = 0;
  return uVar8;
}

