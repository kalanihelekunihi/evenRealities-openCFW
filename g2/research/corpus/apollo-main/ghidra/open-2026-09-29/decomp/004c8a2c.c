
undefined1 FUN_004c8a2c(undefined4 param_1,int param_2)

{
  char cVar1;
  undefined1 uVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int iVar7;
  int local_28;
  int local_24;
  
  puVar3 = (undefined4 *)FUN_004c81a2(param_2);
  iVar4 = 0;
  puVar5 = puVar3 + 3;
  FUN_004c7940(puVar5,0x10);
  if (*(char *)(param_2 + 0x10) == '\x01') {
    uVar6 = *puVar3;
    iVar4 = FUN_004c6fba(uVar6,0,2);
    if ((iVar4 != 0) || (iVar4 = FUN_004c7018(uVar6,&local_28), iVar4 != 0)) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3a5,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Failed_to_get_compressed_file_le_004c8ec0)
      ;
      return 0;
    }
    local_28 = local_28 + -0x18;
    cVar1 = FUN_004c8d3c(uVar6,0xc,puVar5,0xc,&local_24);
    if ((cVar1 != '\0') || (local_24 != 0xc)) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3b0,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Read_compressed_header_failed____004c8ec8,
                   cVar1,local_24,0xc);
      return 0;
    }
    if (puVar3[4] != local_28) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3b5,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Compressed_size_mismatch___u______004c8ecc
                   ,puVar3[4],local_28);
      return 0;
    }
    iVar4 = FUN_0044f718(local_28);
    if (iVar4 == 0) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3bb,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_No_memory_for_compressed_file_004c8ed0);
      return 0;
    }
    cVar1 = FUN_004c6f46(uVar6,iVar4,local_28,&local_24);
    if ((cVar1 != '\0') || (local_24 != local_28)) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3c4,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Read_compressed_file_failed___d__004c8ed4,
                   cVar1,local_24,local_28);
      FUN_0044f758(iVar4);
      return 0;
    }
    puVar3[6] = iVar4;
  }
  else {
    if (*(char *)(param_2 + 0x10) != '\0') {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3db,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Compressed_image_only_support_fi_004c8edc)
      ;
      return 0;
    }
    iVar7 = *(int *)(param_2 + 0xc);
    local_28 = *(int *)(iVar7 + 0xc) + -0xc;
    FUN_00454738(puVar5,*(undefined4 *)(iVar7 + 0x10),0xc);
    puVar3[6] = *(int *)(iVar7 + 0x10) + 0xc;
    if (puVar3[4] != local_28) {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3d6,
                   PTR_s_decode_compressed_004c8ec4,PTR_s_Compressed_size_mismatch___u______004c8ecc
                   ,puVar3[4],local_28);
      return 0;
    }
  }
  cVar1 = FUN_004c8d8c(param_2,puVar5);
  puVar3[6] = 0;
  FUN_0044f758(iVar4);
  if (cVar1 == '\x01') {
    if ((*(char *)(param_2 + 0x10) == '\0') && (*(int *)(*(int *)(param_2 + 0xc) + 0x10) == 0)) {
      uVar2 = 0;
    }
    else if ((*(uint *)(param_2 + 0x20) >> 8 & 0xff) - 7 < 4) {
      if (*(char *)(param_2 + 7) == '\0') {
        uVar2 = FUN_004c8256(param_1,param_2);
      }
      else {
        uVar2 = FUN_004c8570(param_1,param_2);
      }
    }
    else if ((*(uint *)(param_2 + 0x20) >> 8 & 0xff) - 0xb < 4) {
      uVar2 = FUN_004c887c(param_1,param_2);
    }
    else {
      *(undefined4 *)(param_2 + 0x2c) = puVar3[8];
      puVar3[7] = puVar3[8];
      puVar3[8] = 0;
      uVar2 = 1;
    }
  }
  else {
    FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x3e3,
                 PTR_s_decode_compressed_004c8ec4,PTR_s_Decompress_failed_004c8ed8);
    uVar2 = 0;
  }
  return uVar2;
}

