
char FUN_004c8570(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int local_28;
  int local_24;
  undefined4 uStack_20;
  
  puVar5 = *(undefined4 **)(param_2 + 0x48);
  if ((int)((*(uint *)(param_2 + 0x20) >> 0x10) << 0x1c) < 0) {
    *(undefined4 *)(param_2 + 0x2c) = puVar5[8];
    puVar5[7] = puVar5[8];
    puVar5[8] = 0;
    cVar1 = '\x01';
  }
  else {
    uStack_20 = param_4;
    if (*(char *)(param_2 + 0x10) == '\0') {
      puVar4 = *(uint **)(param_2 + 0xc);
      if (-1 < (int)((*puVar4 >> 0x10) << 0x1b)) {
        puVar4 = puVar5 + 9;
        cVar1 = FUN_0048b762(puVar4);
        if (cVar1 != '\x01') {
          return cVar1;
        }
      }
      *(uint **)(param_2 + 0x2c) = puVar4;
      if ((puVar4[2] & 0xffff) == 0) {
        puVar4[2] = *(uint *)(param_2 + 0x28) & 0xffff | puVar4[2] & 0xffff0000;
      }
      cVar1 = '\x01';
    }
    else if (*(char *)(param_2 + 0x10) == '\x01') {
      uVar8 = *(uint *)(param_2 + 0x20);
      uVar6 = *puVar5;
      iVar2 = FUN_0048b010(DAT_004c8a20,*(uint *)(param_2 + 0x24) & 0xffff,
                           *(uint *)(param_2 + 0x24) >> 0x10,uVar8 >> 8 & 0xff,
                           *(uint *)(param_2 + 0x28) & 0xffff);
      if (iVar2 == 0) {
        FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x2e6,
                     PTR_s_load_indexed_004c8e9c,PTR_s_Draw_buffer_alloc_failed_004c8e8c);
        cVar1 = '\0';
      }
      else {
        iVar7 = *(int *)(iVar2 + 0x10);
        if ((uVar8 >> 8 & 0xff) == 7) {
          iVar9 = 2;
        }
        else if ((uVar8 >> 8 & 0xff) == 8) {
          iVar9 = 4;
        }
        else if ((uVar8 >> 8 & 0xff) == 9) {
          iVar9 = 0x10;
        }
        else if ((uVar8 >> 8 & 0xff) == 10) {
          iVar9 = 0x100;
        }
        else {
          iVar9 = 0;
        }
        iVar9 = iVar9 * 4;
        cVar1 = FUN_004c8d3c(uVar6,0xc,iVar7,iVar9,&local_24);
        if ((cVar1 == '\0') && (local_24 == iVar9)) {
          local_28 = 0;
          iVar3 = FUN_004c6fba(uVar6,0,2);
          if ((iVar3 == 0) && (iVar3 = FUN_004c7018(uVar6,&local_28), iVar3 == 0)) {
            local_28 = local_28 - (iVar9 + 0xc);
            cVar1 = FUN_004c8d3c(uVar6,iVar9 + 0xc,iVar7 + iVar9,local_28,&local_24);
            if ((cVar1 == '\0') && (local_24 == local_28)) {
              puVar5[7] = iVar2;
              *(int *)(param_2 + 0x2c) = iVar2;
              cVar1 = '\x01';
            }
            else {
              FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x300,
                           PTR_s_load_indexed_004c8e9c,
                           PTR_s_Read_indexed_image_failed___d__w_004c8e94,cVar1,local_24,local_28);
              FUN_0048b216(iVar2);
              cVar1 = '\0';
            }
          }
          else {
            FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x2f6,
                         PTR_s_load_indexed_004c8e9c,PTR_s_Failed_to_get_file_to_size_004c8e90);
            FUN_0048b216(iVar2);
            cVar1 = '\0';
          }
        }
        else {
          FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x2ee,
                       PTR_s_load_indexed_004c8e9c,PTR_s_Read_palette_failed___d__with_le_004c8e88,
                       cVar1,local_24,iVar9);
          FUN_0048b216(iVar2);
          cVar1 = '\0';
        }
      }
    }
    else {
      FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x30a,
                   PTR_s_load_indexed_004c8e9c,PTR_s_Unknown_src_type___d_004c8ea4,
                   *(undefined1 *)(param_2 + 0x10));
      cVar1 = '\0';
    }
  }
  return cVar1;
}

