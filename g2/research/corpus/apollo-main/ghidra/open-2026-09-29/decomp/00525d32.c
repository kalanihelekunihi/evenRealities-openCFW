
uint open_face_PS_from_sfnt_stream
               (undefined4 *param_1,int param_2,uint param_3,undefined4 param_4,undefined4 param_5,
               undefined4 param_6)

{
  int iVar1;
  undefined4 uVar2;
  undefined *puVar3;
  uint uVar4;
  undefined4 uVar5;
  uint local_30;
  char local_2c [4];
  uint local_28;
  uint local_24;
  undefined4 uStack_20;
  
  uVar5 = *param_1;
  if (0 < (int)param_3) {
    param_3 = param_3 & 0xffff;
  }
  iVar1 = *(int *)(param_2 + 8);
  uStack_20 = param_4;
  local_30 = ft_lookup_PS_in_sfnt_stream(param_2,param_3,&local_24,&local_28,local_2c);
  if (local_30 == 0) {
    if (*(uint *)(param_2 + 4) < local_24) {
      local_30 = 8;
    }
    else if (*(int *)(param_2 + 4) - local_24 < local_28) {
      local_30 = 8;
    }
    else {
      local_30 = FT_Stream_Seek(param_2,local_24 + iVar1);
      if ((local_30 == 0) && (uVar2 = ft_mem_alloc(uVar5,local_28,&local_30), local_30 == 0)) {
        local_30 = FT_Stream_Read(param_2,uVar2,local_28);
        if (local_30 == 0) {
          puVar3 = DAT_00526800;
          if (local_2c[0] != '\0') {
            puVar3 = &DAT_005260a0;
          }
          if (-1 < (int)param_3) {
            param_3 = 0;
          }
          local_30 = open_face_from_buffer(param_1,uVar2,local_28,param_3,puVar3,param_6);
        }
        else {
          ft_mem_free(uVar5,uVar2);
        }
      }
    }
  }
  if (((local_30 & 0xff) != 2) || (uVar4 = FT_Stream_Seek(param_2,iVar1), uVar4 == 0)) {
    uVar4 = local_30;
  }
  return uVar4;
}

