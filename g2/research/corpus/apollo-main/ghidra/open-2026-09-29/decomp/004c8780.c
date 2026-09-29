
undefined4 FUN_004c8780(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  int local_20;
  undefined4 uStack_1c;
  
  puVar3 = *(undefined4 **)(param_2 + 0x48);
  uVar4 = *puVar3;
  iVar5 = (*(uint *)(param_2 + 0x24) >> 0x10) * (*(uint *)(param_2 + 0x28) & 0xffff);
  if ((*(uint *)(param_2 + 0x20) >> 8 & 0xff) == 0x14) {
    iVar5 = (*(uint *)(param_2 + 0x24) >> 0x10) * ((*(uint *)(param_2 + 0x28) & 0xffff) / 2) + iVar5
    ;
  }
  uStack_1c = param_4;
  iVar2 = FUN_0048b010(DAT_004c8a20,*(uint *)(param_2 + 0x24) & 0xffff,
                       *(uint *)(param_2 + 0x24) >> 0x10,*(uint *)(param_2 + 0x20) >> 8 & 0xff,
                       *(uint *)(param_2 + 0x28) & 0xffff);
  if (iVar2 == 0) {
    FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,800,PTR_s_decode_rgb_004c8eac,
                 PTR_s_No_memory_for_rgb_file_read_004c8ea8);
    uVar4 = 0;
  }
  else {
    cVar1 = FUN_004c8d3c(uVar4,0xc,*(undefined4 *)(iVar2 + 0x10),iVar5,&local_20);
    if ((cVar1 == '\0') && (local_20 == iVar5)) {
      *(int *)(param_2 + 0x2c) = iVar2;
      puVar3[7] = iVar2;
      uVar4 = 1;
    }
    else {
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x329,PTR_s_decode_rgb_004c8eac
                   ,PTR_s_Read_rgb_file_failed___d__with_l_004c8eb0,cVar1,local_20,iVar5);
      FUN_0048b216(iVar2);
      uVar4 = 0;
    }
  }
  return uVar4;
}

