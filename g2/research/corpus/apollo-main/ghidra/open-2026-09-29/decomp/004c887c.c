
undefined4 FUN_004c887c(undefined4 param_1,int param_2)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined1 *puVar9;
  int iVar10;
  byte *pbVar11;
  int iVar12;
  byte bVar13;
  int local_28;
  
  puVar4 = *(undefined4 **)(param_2 + 0x48);
  bVar1 = FUN_00440f44(*(uint *)(param_2 + 0x20) >> 8 & 0xff);
  if (bVar1 == 0) {
    FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x34e,DAT_004c8eb8,DAT_004c8eb4,
                 (*(uint *)(param_2 + 0x20) & 0xffff) >> 8);
    uVar5 = 0;
  }
  else {
    uVar6 = ((*(uint *)(param_2 + 0x28) & 0xffff) << 3) / (uint)bVar1;
    uVar7 = (*(uint *)(param_2 + 0x24) >> 0x10) * uVar6;
    iVar10 = (*(uint *)(param_2 + 0x24) >> 0x10) * (*(uint *)(param_2 + 0x28) & 0xffff);
    iVar8 = FUN_0048b010(DAT_004c8a20,*(uint *)(param_2 + 0x24) & 0xffff,
                         *(uint *)(param_2 + 0x24) >> 0x10,0xe,uVar6 * 8 + 7 >> 3);
    if (iVar8 == 0) {
      FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x35b,DAT_004c8eb8,
                   PTR_s_Out_of_memory_004c8e78);
      uVar5 = 0;
    }
    else {
      iVar12 = *(int *)(iVar8 + 0x10);
      if ((int)((*(uint *)(param_2 + 0x20) >> 0x10) << 0x1c) < 0) {
        FUN_00454738(iVar12,*(undefined4 *)(puVar4[8] + 0x10),iVar10);
      }
      else if (*(char *)(param_2 + 0x10) == '\x01') {
        cVar2 = FUN_004c8d3c(*puVar4,0xc,iVar12,iVar10,&local_28);
        if ((cVar2 != '\0') || (local_28 != iVar10)) {
          FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x368,DAT_004c8eb8,
                       PTR_s_Read_header_failed___d__with_len_004c8ebc,cVar2,local_28,iVar10);
          FUN_0048b216(iVar8);
          return 0;
        }
      }
      else if (*(char *)(param_2 + 0x10) == '\0') {
        FUN_00454738(iVar12,*(undefined4 *)(*(int *)(param_2 + 0xc) + 0x10),iVar10);
      }
      if ((*(uint *)(param_2 + 0x20) & 0xffff) >> 8 != 0xe) {
        pbVar11 = (byte *)(iVar12 + iVar10 + -1);
        puVar9 = (undefined1 *)(uVar7 + iVar12);
        bVar13 = 0;
        for (uVar6 = 0; puVar9 = puVar9 + -1, uVar6 < uVar7; uVar6 = uVar6 + 1) {
          uVar3 = FUN_004c884a((1 << (uint)bVar1) - 1U & (int)(uint)*pbVar11 >> (uint)bVar13 & 0xff,
                               bVar1);
          *puVar9 = uVar3;
          bVar13 = bVar1 + bVar13;
          if (7 < bVar13) {
            bVar13 = 0;
            pbVar11 = pbVar11 + -1;
          }
        }
      }
      puVar4[7] = iVar8;
      *(int *)(param_2 + 0x2c) = iVar8;
      uVar5 = 1;
    }
  }
  return uVar5;
}

