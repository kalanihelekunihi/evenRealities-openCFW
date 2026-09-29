
undefined2 * FUN_10009ab8(uint param_1)

{
  uint uVar1;
  int *piVar2;
  undefined2 *puVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  undefined2 *puVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  undefined2 *puVar11;
  
  if (param_1 != 0) {
    uVar4 = param_1 + 3 & 0xfffffffc;
    if (param_1 != uVar4) {
      FUN_10009934(PTR_s_malloc_size__d__but_align_to__d_10009c00,param_1,uVar4);
    }
    piVar2 = DAT_10009c04;
    uVar10 = DAT_10009c04[3];
    if (uVar4 <= uVar10) {
      uVar6 = (uint)(uVar4 < 0xc) * 0xc + (uVar4 >= 0xc) * uVar4;
      puVar11 = (undefined2 *)DAT_10009c04[2];
      iVar5 = *DAT_10009c04;
      uVar4 = (int)puVar11 - iVar5;
      do {
        while( true ) {
          uVar1 = uVar4;
          if (uVar10 - uVar6 <= uVar1) {
            return (undefined2 *)0x0;
          }
          puVar3 = (undefined2 *)(iVar5 + uVar1);
          if (puVar3[1] == 0) break;
          uVar4 = *(uint *)(puVar3 + 2);
        }
        uVar4 = *(uint *)(puVar3 + 2);
        uVar9 = (uVar4 - uVar1) - 0xc;
      } while (uVar9 < uVar6);
      if (uVar9 < uVar6 + 0x18) {
        puVar3[1] = 1;
        uVar4 = (uVar4 - uVar1) + piVar2[4];
        piVar2[4] = uVar4;
        if ((uint)piVar2[5] < uVar4) {
          piVar2[5] = uVar4;
        }
      }
      else {
        iVar8 = uVar6 + 0xc + uVar1;
        puVar7 = (undefined2 *)(iVar5 + iVar8);
        *(uint *)(puVar7 + 2) = uVar4;
        *(uint *)(puVar7 + 4) = uVar1;
        *puVar7 = 0x1ea0;
        puVar7[1] = 0;
        *(int *)(puVar3 + 2) = iVar8;
        puVar3[1] = 1;
        if (*(int *)(puVar7 + 2) != uVar10 + 0xc) {
          *(int *)(iVar5 + *(int *)(puVar7 + 2) + 8) = iVar8;
        }
        uVar6 = uVar6 + piVar2[4] + 0xc;
        piVar2[4] = uVar6;
        if ((uint)piVar2[5] < uVar6) {
          piVar2[5] = uVar6;
        }
      }
      *puVar3 = 0x1ea0;
      if (((puVar11 == puVar3) && (puVar3[1] != 0)) &&
         (puVar11 = (undefined2 *)piVar2[1], puVar3 != puVar11)) {
        puVar7 = puVar3;
        do {
          puVar7 = (undefined2 *)(*(int *)(puVar7 + 2) + *piVar2);
          if (puVar7[1] == 0) {
            piVar2[2] = (int)puVar7;
            goto LAB_10009bc2;
          }
        } while (puVar7 != puVar11);
        piVar2[2] = (int)puVar11;
      }
LAB_10009bc2:
      return puVar3 + 6;
    }
    FUN_10009934(PTR_s_no_memory_10009c08);
  }
  return (undefined2 *)0x0;
}

