
undefined8 ft_var_load_avar(int param_1,int *param_2,undefined4 param_3,uint param_4)

{
  short sVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  ushort *puVar9;
  int iVar10;
  int local_30;
  int *local_2c;
  int local_28;
  uint local_24;
  
  iVar6 = *(int *)(param_1 + 0x68);
  uVar7 = *(undefined4 *)(iVar6 + 0x1c);
  iVar8 = *(int *)(param_1 + 700);
  local_28 = 0;
  *(undefined1 *)(iVar8 + 0x18) = 1;
  local_24 = param_4;
  local_28 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2094,iVar6,&local_24);
  local_30 = param_1;
  local_2c = param_2;
  if ((local_28 == 0) && (local_28 = FT_Stream_EnterFrame(iVar6,local_24), local_28 == 0)) {
    iVar3 = FT_Stream_GetULong(iVar6);
    iVar4 = FT_Stream_GetULong(iVar6);
    if ((iVar3 == 0x10000) && (iVar4 == **(int **)(iVar8 + 0xc))) {
      local_2c = &local_28;
      local_30 = 0;
      uVar5 = ft_mem_realloc(uVar7,8,0,iVar4);
      *(undefined4 *)(iVar8 + 0x1c) = uVar5;
      if (local_28 == 0) {
        puVar9 = *(ushort **)(iVar8 + 0x1c);
        iVar3 = 0;
        while( true ) {
          local_2c = &local_28;
          local_30 = 0;
          if (iVar4 <= iVar3) break;
          uVar2 = FT_Stream_GetUShort(iVar6);
          *puVar9 = uVar2;
          if (local_24 < (uint)*puVar9 << 2) {
LAB_005f151c:
            local_2c = &local_28;
            local_30 = 0;
            while (iVar3 = iVar3 + -1, -1 < iVar3) {
              ft_mem_free(uVar7,*(undefined4 *)(*(int *)(iVar8 + 0x1c) + iVar3 * 8 + 4));
              *(undefined4 *)(*(int *)(iVar8 + 0x1c) + iVar3 * 8 + 4) = 0;
            }
            ft_mem_free(uVar7,*(undefined4 *)(iVar8 + 0x1c));
            *(undefined4 *)(iVar8 + 0x1c) = 0;
            *(undefined4 *)(iVar8 + 0x1c) = 0;
            break;
          }
          uVar5 = ft_mem_realloc(uVar7,8,0,*puVar9);
          *(undefined4 *)(puVar9 + 2) = uVar5;
          if (local_28 != 0) goto LAB_005f151c;
          for (iVar10 = 0; iVar10 < (int)(uint)*puVar9; iVar10 = iVar10 + 1) {
            sVar1 = FT_Stream_GetUShort(iVar6);
            *(int *)(*(int *)(puVar9 + 2) + iVar10 * 8) = (int)sVar1 << 2;
            sVar1 = FT_Stream_GetUShort(iVar6);
            *(int *)(*(int *)(puVar9 + 2) + iVar10 * 8 + 4) = (int)sVar1 << 2;
          }
          iVar3 = iVar3 + 1;
          puVar9 = puVar9 + 4;
        }
      }
    }
    FT_Stream_ExitFrame(iVar6);
  }
  return CONCAT44(local_2c,local_30);
}

