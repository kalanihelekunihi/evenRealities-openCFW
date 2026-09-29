
undefined8 ft_var_load_mvar(int param_1,int *param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  short sVar2;
  undefined2 uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined2 *puVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  int local_30;
  int *local_2c;
  int local_28;
  undefined4 uStack_24;
  
  iVar8 = *(int *)(param_1 + 0x68);
  uVar10 = *(undefined4 *)(iVar8 + 0x1c);
  iVar9 = *(int *)(param_1 + 700);
  local_28 = param_3;
  uStack_24 = param_4;
  local_28 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2d90,iVar8,&uStack_24);
  local_30 = param_1;
  local_2c = param_2;
  if (local_28 == 0) {
    iVar4 = *(int *)(iVar8 + 8);
    sVar2 = FT_Stream_ReadUShort(iVar8,&local_28);
    if ((local_28 == 0) && (local_28 = FT_Stream_Skip(iVar8,2), local_28 == 0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if ((!bVar1) && (sVar2 == 1)) {
      uVar5 = ft_mem_alloc(uVar10,0x1c,&local_28);
      *(undefined4 *)(iVar9 + 0x38) = uVar5;
      if ((local_28 == 0) && (local_28 = FT_Stream_Skip(iVar8,4), local_28 == 0)) {
        uVar3 = FT_Stream_ReadUShort(iVar8,&local_28);
        **(undefined2 **)(iVar9 + 0x38) = uVar3;
        if ((local_28 == 0) && (uVar6 = FT_Stream_ReadUShort(iVar8,&local_28), local_28 == 0)) {
          uVar5 = *(undefined4 *)(iVar8 + 8);
          local_28 = ft_var_load_item_variation_store
                               (param_1,iVar4 + (uVar6 & 0xffff),*(int *)(iVar9 + 0x38) + 4);
          if (local_28 == 0) {
            local_2c = &local_28;
            local_30 = 0;
            uVar10 = ft_mem_realloc(uVar10,0xc,0,**(undefined2 **)(iVar9 + 0x38));
            *(undefined4 *)(*(int *)(iVar9 + 0x38) + 0x18) = uVar10;
            if (((local_28 == 0) && (local_28 = FT_Stream_Seek(iVar8,uVar5), local_28 == 0)) &&
               (iVar4 = FT_Stream_EnterFrame(iVar8,(uint)**(ushort **)(iVar9 + 0x38) << 3),
               iVar4 == 0)) {
              puVar11 = *(undefined4 **)(*(int *)(iVar9 + 0x38) + 0x18);
              puVar12 = puVar11 + (uint)**(ushort **)(iVar9 + 0x38) * 3;
              iVar4 = *(int *)(iVar9 + 0x38);
              local_28 = 0;
              for (; puVar11 < puVar12; puVar11 = puVar11 + 3) {
                uVar10 = FT_Stream_GetULong(iVar8);
                *puVar11 = uVar10;
                uVar3 = FT_Stream_GetUShort(iVar8);
                *(undefined2 *)(puVar11 + 1) = uVar3;
                uVar3 = FT_Stream_GetUShort(iVar8);
                *(undefined2 *)((int)puVar11 + 6) = uVar3;
                if ((*(uint *)(iVar4 + 4) <= (uint)*(ushort *)(puVar11 + 1)) ||
                   (*(uint *)(*(int *)(iVar4 + 8) + (uint)*(ushort *)(puVar11 + 1) * 0x10) <=
                    (uint)*(ushort *)((int)puVar11 + 6))) {
                  local_28 = 8;
                  break;
                }
              }
              FT_Stream_ExitFrame(iVar8);
              if (local_28 == 0) {
                puVar11 = *(undefined4 **)(*(int *)(iVar9 + 0x38) + 0x18);
                puVar12 = puVar11 + (uint)**(ushort **)(iVar9 + 0x38) * 3;
                for (; puVar11 < puVar12; puVar11 = puVar11 + 3) {
                  puVar7 = (undefined2 *)ft_var_get_value_pointer(param_1,*puVar11);
                  if (puVar7 != (undefined2 *)0x0) {
                    *(undefined2 *)(puVar11 + 2) = *puVar7;
                  }
                }
                *(uint *)(param_1 + 0x2c0) = *(uint *)(param_1 + 0x2c0) | 0x100;
              }
            }
          }
        }
      }
    }
  }
  return CONCAT44(local_2c,local_30);
}

