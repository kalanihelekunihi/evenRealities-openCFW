
int FUN_005db578(undefined4 param_1,undefined4 *param_2,int param_3)

{
  bool bVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 *puVar10;
  undefined4 uVar11;
  int local_48;
  ushort local_44;
  int local_40;
  undefined4 local_3c;
  int local_38;
  undefined4 local_34;
  uint local_30;
  int local_2c;
  int local_28;
  
  uVar11 = *(undefined4 *)(param_2[0x18] + 4);
  puVar10 = (undefined4 *)param_2[0x87];
  if (puVar10 == (undefined4 *)0x0) {
    puVar10 = (undefined4 *)FT_Get_Module_Interface(uVar11,PTR_DAT_005dc120);
    if (puVar10 == (undefined4 *)0x0) {
      return 0xb;
    }
    param_2[0x87] = puVar10;
    param_2[0x81] = *puVar10;
  }
  uVar5 = ft_module_get_service(param_2[0x18],PTR_s_postscript_cmaps_005dc124,1);
  param_2[0x88] = uVar5;
  if (param_2[0x89] == 0) {
    uVar5 = FT_Get_Module(uVar11,PTR_s_truetype_005dc128);
    uVar5 = ft_module_get_service(uVar5,PTR_s_multi_masters_005dc12c,0);
    param_2[0x89] = uVar5;
  }
  if (param_2[0x8a] == 0) {
    uVar11 = FT_Get_Module(uVar11,PTR_s_truetype_005dc128);
    uVar11 = ft_module_get_service(uVar11,PTR_s_metrics_variations_005dc130,0);
    param_2[0x8a] = uVar11;
  }
  local_48 = FUN_005db3ec(param_1,param_2);
  if (local_48 == 0) {
    iVar9 = param_2[0x1a];
    uVar2 = (ushort)param_3;
    if (param_3 < 0) {
      uVar2 = -uVar2;
    }
    uVar6 = (uint)uVar2;
    if (param_3 < 0) {
      uVar6 = uVar6 - 1;
    }
    if ((int)param_2[0x23] <= (int)uVar6) {
      if (-1 < param_3) {
        return 6;
      }
      uVar6 = 0;
    }
    local_40 = param_3;
    local_48 = FT_Stream_Seek(iVar9,*(undefined4 *)(param_2[0x24] + uVar6 * 4));
    if ((local_48 == 0) && (local_48 = (*(code *)puVar10[0x16])(param_2,iVar9), local_48 == 0)) {
      local_34 = param_2[0x19];
      local_38 = 0;
      local_3c = 0;
      local_28 = local_40;
      if (local_40 < 0) {
        local_28 = -local_40;
      }
      local_28 = local_28 >> 0x10;
      iVar7 = (*(code *)param_2[0x81])(param_2,DAT_005dc134,iVar9,&local_30);
      if (((((iVar7 != 0) || (local_30 < 0x14)) ||
           (iVar7 = FT_Stream_ReadULong(iVar9,&local_48), local_48 != 0)) ||
          (((iVar8 = FT_Stream_ReadUShort(iVar9,&local_48), local_48 != 0 ||
            (local_48 = FT_Stream_Skip(iVar9,2), local_48 != 0)) ||
           ((uVar2 = FT_Stream_ReadUShort(iVar9,&local_48), local_48 != 0 ||
            ((uVar3 = FT_Stream_ReadUShort(iVar9,&local_48), local_48 != 0 ||
             (uVar4 = FT_Stream_ReadUShort(iVar9,&local_48), local_48 != 0)))))))) ||
         (local_44 = FT_Stream_ReadUShort(iVar9,&local_48), local_48 != 0)) {
        iVar7 = 0;
        iVar8 = 0;
        uVar2 = 0;
        uVar3 = 0;
        uVar4 = 0;
        local_44 = 0;
      }
      if (((((iVar7 == 0x10000) && (uVar3 == 0x14)) && (uVar2 != 0)) &&
          (((uVar2 < 0x3fff &&
            (((uint)local_44 == (uint)uVar2 * 4 + 4 || ((uint)local_44 == (uint)uVar2 * 4 + 6)))) &&
           (uVar4 < 0x7f00)))) &&
         ((uint)uVar4 * (uint)local_44 + (uint)uVar2 * 0x14 + iVar8 <= local_30)) {
        param_2[0xb0] = param_2[0xb0] | 1;
      }
      else {
        uVar4 = 0;
      }
      if ((int)((uint)*(byte *)(param_2 + 0xb0) << 0x1f) < 0) {
        local_38 = ft_mem_alloc(local_34,(uint)uVar2 << 2,&local_48);
        if ((local_48 == 0) &&
           (local_3c = ft_mem_alloc(local_34,(uint)uVar2 << 2,&local_48), local_48 == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (!bVar1) {
          iVar8 = iVar8 + *(int *)(iVar9 + 8);
          local_2c = iVar8 + -0x10;
          iVar8 = iVar8 + -8;
          iVar7 = local_38;
          for (uVar6 = 0; uVar6 < uVar2; uVar6 = uVar6 + 1) {
            local_48 = FT_Stream_ReadAt(iVar9,iVar8,iVar7,4);
            iVar8 = iVar8 + (uint)uVar3;
            iVar7 = iVar7 + 4;
          }
          iVar7 = (uint)uVar2 * (uint)uVar3 + local_2c + 4;
          for (uVar6 = 0; uVar6 < uVar4; uVar6 = uVar6 + 1) {
            local_48 = FT_Stream_ReadAt(iVar9,iVar7,local_3c,(uint)uVar2 << 2);
            iVar8 = FUN_004751c8(local_38,local_3c,(uint)uVar2 << 2);
            if (iVar8 == 0) break;
            iVar7 = iVar7 + (uint)local_44;
          }
          if (uVar6 == uVar4) {
            uVar4 = uVar4 + 1;
          }
        }
      }
      ft_mem_free(local_34,local_38);
      ft_mem_free(local_34,local_3c);
      iVar7 = (*(code *)param_2[0x81])(param_2,DAT_005dc38c,iVar9,0);
      if (((iVar7 != 0) &&
          (iVar7 = (*(code *)param_2[0x81])(param_2,DAT_005dc390,iVar9,0), iVar7 != 0)) &&
         (iVar9 = (*(code *)param_2[0x81])(param_2,DAT_005dc394,iVar9,0), iVar9 == 0)) {
        uVar4 = 0;
      }
      if ((int)(uint)uVar4 < local_28) {
        if (-1 < local_40) {
          return 6;
        }
        uVar4 = 0;
      }
      param_2[3] = (uint)uVar4 << 0x10;
      *param_2 = param_2[0x23];
      param_2[1] = local_40;
    }
  }
  return local_48;
}

