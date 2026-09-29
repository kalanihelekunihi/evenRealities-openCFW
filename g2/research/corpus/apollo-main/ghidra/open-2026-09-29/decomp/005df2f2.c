
int FUN_005df2f2(int param_1,int param_2)

{
  bool bVar1;
  ushort uVar2;
  ushort uVar3;
  undefined4 uVar4;
  ushort local_38 [2];
  int local_34;
  int local_30;
  undefined4 local_2c;
  uint local_28;
  uint local_24;
  int local_20;
  ushort local_1c;
  int local_14;
  
  uVar4 = *(undefined4 *)(param_2 + 0x1c);
  local_38[0] = 0;
  local_14 = *(int *)(param_2 + 8);
  local_20 = FT_Stream_ReadULong(param_2,&local_34);
  if ((local_34 == 0) &&
     (local_34 = FT_Stream_ReadFields(param_2,DAT_005dfb94,&local_20), local_34 == 0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (!bVar1) {
    if (local_20 == DAT_005dfb98) {
      local_38[0] = local_1c;
    }
    else {
      local_34 = FUN_005df1ae(&local_20,param_2,local_38);
      if (local_34 != 0) {
        return local_34;
      }
    }
    *(ushort *)(param_1 + 0x98) = local_38[0];
    *(int *)(param_1 + 0x94) = local_20;
    uVar4 = ft_mem_realloc(uVar4,0x10,0,*(undefined2 *)(param_1 + 0x98),0,&local_34);
    *(undefined4 *)(param_1 + 0x9c) = uVar4;
    if (((local_34 == 0) && (local_34 = FT_Stream_Seek(param_2,local_14 + 0xc), local_34 == 0)) &&
       (local_34 = FT_Stream_EnterFrame(param_2,(uint)local_1c << 4), local_34 == 0)) {
      local_38[0] = 0;
      for (uVar3 = 0; uVar3 < local_1c; uVar3 = uVar3 + 1) {
        local_30 = FT_Stream_GetULong(param_2);
        local_2c = FT_Stream_GetULong(param_2);
        local_28 = FT_Stream_GetULong(param_2);
        local_24 = FT_Stream_GetULong(param_2);
        if (local_28 <= *(uint *)(param_2 + 4)) {
          if (*(int *)(param_2 + 4) - local_28 < local_24) {
            if ((local_30 != DAT_005dfb80) && (local_30 != DAT_005dfb84)) goto LAB_005df406;
            local_24 = *(int *)(param_2 + 4) - local_28 & 0xfffffffc;
          }
          bVar1 = false;
          for (uVar2 = 0; uVar2 < local_38[0]; uVar2 = uVar2 + 1) {
            if (*(int *)(*(int *)(param_1 + 0x9c) + (uint)uVar2 * 0x10) == local_30) {
              bVar1 = true;
              break;
            }
          }
          if (!bVar1) {
            FUN_00439c04(*(int *)(param_1 + 0x9c) + (uint)local_38[0] * 0x10,&local_30,0x10);
            local_38[0] = local_38[0] + 1;
          }
        }
LAB_005df406:
      }
      *(ushort *)(param_1 + 0x98) = local_38[0];
      FT_Stream_ExitFrame(param_2);
    }
  }
  return local_34;
}

