
uint * FUN_005d7f90(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  undefined4 uVar8;
  int iVar9;
  uint *puVar10;
  uint *puVar11;
  uint uVar12;
  uint *local_68;
  uint local_64 [16];
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  uVar8 = *(undefined4 *)(param_2 * 0xcc + param_1[6] + 200);
  iVar9 = param_1[4];
  uVar6 = 0;
  puVar11 = (uint *)param_1[2];
  puVar10 = puVar11 + *param_1 * 10;
  for (puVar4 = puVar11; puVar4 < puVar10; puVar4 = puVar4 + 10) {
    if ((int)((uint)(byte)puVar4[4] << 0x1b) < 0) {
      uVar6 = uVar6 + 1;
    }
  }
  if (uVar6 != 0) {
    if (uVar6 < 0x11) {
      puVar1 = local_64;
    }
    else {
      puVar1 = (uint *)ft_mem_realloc(iVar9,4,0,uVar6,0,&local_68);
      if (local_68 != (uint *)0x0) {
        return local_68;
      }
    }
    uVar6 = 0;
    for (puVar4 = puVar11; puVar4 < puVar10; puVar4 = puVar4 + 10) {
      if ((int)((uint)(byte)puVar4[4] << 0x1b) < 0) {
        puVar5 = puVar1 + uVar6;
        while ((puVar1 < puVar5 && ((int)puVar4[7] < *(int *)(puVar5[-1] + 0x1c)))) {
          *puVar5 = puVar5[-1];
          puVar5 = puVar5 + -1;
        }
        *puVar5 = (uint)puVar4;
        uVar6 = uVar6 + 1;
      }
    }
    for (; puVar11 < puVar10; puVar11 = puVar11 + 10) {
      if (-1 < (int)((uint)(byte)puVar11[4] << 0x1b)) {
        if ((int)((uint)(byte)puVar11[3] << 0x1e) < 0) {
          if ((((char)puVar11[5] == '\x04') || ((char)puVar11[5] != *(char *)((int)puVar11 + 0x15)))
             || ((-1 < (int)((uint)(byte)puVar11[4] << 0x19) &&
                 (-1 < (int)((uint)(byte)puVar11[3] << 0x1d))))) goto LAB_005d806a;
          puVar11[3] = puVar11[3] & 0xfffffffd;
        }
        uVar2 = 0;
        while ((uVar2 < uVar6 && (*(int *)(puVar1[uVar2] + 0x1c) <= (int)puVar11[7]))) {
          uVar2 = uVar2 + 1;
        }
        if (uVar2 == 0) {
          uVar2 = *puVar1;
          iVar3 = FT_MulFix(puVar11[7] - *(int *)(uVar2 + 0x1c),uVar8);
          puVar11[9] = iVar3 + *(int *)(uVar2 + 0x24);
        }
        else {
          uVar12 = puVar1[uVar2 - 1];
          uVar2 = uVar6;
          while ((uVar2 != 0 && ((int)puVar11[7] <= *(int *)(puVar1[uVar2 - 1] + 0x1c)))) {
            uVar2 = uVar2 - 1;
          }
          if (uVar2 == uVar6) {
            uVar2 = puVar1[uVar2 - 1];
            iVar3 = FT_MulFix(puVar11[7] - *(int *)(uVar2 + 0x1c),uVar8);
            puVar11[9] = iVar3 + *(int *)(uVar2 + 0x24);
          }
          else {
            uVar7 = puVar1[uVar2];
            uVar2 = puVar11[7];
            if (uVar2 == *(uint *)(uVar12 + 0x1c)) {
              puVar11[9] = *(uint *)(uVar12 + 0x24);
            }
            else if (uVar2 == *(uint *)(uVar7 + 0x1c)) {
              puVar11[9] = *(uint *)(uVar7 + 0x24);
            }
            else {
              iVar3 = FT_MulDiv(uVar2 - *(int *)(uVar12 + 0x1c),
                                *(int *)(uVar7 + 0x24) - *(int *)(uVar12 + 0x24),
                                *(int *)(uVar7 + 0x1c) - *(int *)(uVar12 + 0x1c));
              puVar11[9] = iVar3 + *(int *)(uVar12 + 0x24);
            }
          }
        }
        puVar11[4] = puVar11[4] | 0x20;
      }
LAB_005d806a:
    }
    puVar4 = local_64;
    if (puVar1 != puVar4) {
      ft_mem_free(iVar9,puVar1);
      puVar4 = (uint *)0x0;
    }
  }
  return puVar4;
}

