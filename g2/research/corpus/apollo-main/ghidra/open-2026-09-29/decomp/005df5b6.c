
int FUN_005df5b6(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  ushort *puVar4;
  int iVar5;
  uint uVar6;
  short *psVar7;
  ushort *puVar8;
  int iVar9;
  int local_38;
  uint local_34;
  undefined4 local_30;
  int local_2c;
  undefined4 uStack_28;
  
  local_30 = *(undefined4 *)(param_2 + 0x1c);
  psVar7 = (short *)(param_1 + 0x158);
  *(int *)(param_1 + 0x170) = param_2;
  uStack_28 = param_4;
  local_38 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0078,param_2,&local_2c);
  if (local_38 == 0) {
    iVar2 = *(int *)(param_2 + 8);
    local_38 = FT_Stream_ReadFields(param_2,PTR_DAT_005e007c,psVar7);
    if (local_38 == 0) {
      uVar6 = *(int *)(param_1 + 0x15c) * 0xc + iVar2 + 6;
      local_34 = local_2c + iVar2;
      if (local_34 < uVar6) {
        local_38 = 0x91;
      }
      else {
        if (*psVar7 == 1) {
          local_38 = FT_Stream_Seek(param_2,uVar6);
          if (local_38 != 0) {
            return local_38;
          }
          uVar3 = FT_Stream_ReadUShort(param_2,&local_38);
          *(undefined4 *)(param_1 + 0x168) = uVar3;
          if (local_38 != 0) {
            return local_38;
          }
          uVar6 = uVar6 + *(int *)(param_1 + 0x168) * 4 + 2;
          uVar3 = ft_mem_realloc(local_30,0xc,0,*(undefined4 *)(param_1 + 0x168),0,&local_38);
          *(undefined4 *)(param_1 + 0x16c) = uVar3;
          if ((local_38 == 0) &&
             (local_38 = FT_Stream_EnterFrame(param_2,*(int *)(param_1 + 0x168) << 2), local_38 == 0
             )) {
            bVar1 = false;
          }
          else {
            bVar1 = true;
          }
          if (bVar1) {
            return local_38;
          }
          puVar4 = *(ushort **)(param_1 + 0x16c);
          puVar8 = puVar4 + *(int *)(param_1 + 0x168) * 6;
          for (; puVar4 < puVar8; puVar4 = puVar4 + 6) {
            local_38 = FT_Stream_ReadFields(param_2,PTR_DAT_005e0080,puVar4);
            *(int *)(puVar4 + 2) = *(int *)(param_1 + 0x160) + iVar2 + *(int *)(puVar4 + 2);
            if ((*(uint *)(puVar4 + 2) < uVar6) || (local_34 < *(int *)(puVar4 + 2) + (uint)*puVar4)
               ) {
              *puVar4 = 0;
            }
          }
          FT_Stream_ExitFrame(param_2);
          local_38 = FT_Stream_Seek(param_2,iVar2 + 6);
        }
        uVar3 = ft_mem_realloc(local_30,0x14,0,*(undefined4 *)(param_1 + 0x15c),0,&local_38);
        *(undefined4 *)(param_1 + 0x164) = uVar3;
        if ((local_38 == 0) &&
           (local_38 = FT_Stream_EnterFrame(param_2,*(int *)(param_1 + 0x15c) * 0xc), local_38 == 0)
           ) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (!bVar1) {
          iVar9 = *(int *)(param_1 + 0x164);
          for (iVar5 = *(int *)(param_1 + 0x15c); iVar5 != 0; iVar5 = iVar5 + -1) {
            local_38 = FT_Stream_ReadFields(param_2,PTR_DAT_005e0084,iVar9);
            if ((((local_38 == 0) && (*(short *)(iVar9 + 8) != 0)) &&
                (*(int *)(iVar9 + 0xc) = *(int *)(param_1 + 0x160) + iVar2 + *(int *)(iVar9 + 0xc),
                uVar6 <= *(uint *)(iVar9 + 0xc))) &&
               ((*(int *)(iVar9 + 0xc) + (uint)*(ushort *)(iVar9 + 8) <= local_34 &&
                (((*psVar7 != 1 || (*(ushort *)(iVar9 + 4) < 0x8000)) ||
                 ((*(ushort *)(iVar9 + 4) - 0x8000 < *(uint *)(param_1 + 0x168) &&
                  (*(short *)(*(int *)(param_1 + 0x16c) + (uint)*(ushort *)(iVar9 + 4) * 0xc +
                             -0x60000) != 0)))))))) {
              iVar9 = iVar9 + 0x14;
            }
          }
          iVar2 = (iVar9 - *(int *)(param_1 + 0x164)) / 0x14;
          uVar3 = ft_mem_realloc(local_30,0x14,*(undefined4 *)(param_1 + 0x15c),iVar2,
                                 *(undefined4 *)(param_1 + 0x164),&local_38);
          *(undefined4 *)(param_1 + 0x164) = uVar3;
          *(int *)(param_1 + 0x15c) = iVar2;
          FT_Stream_ExitFrame(param_2);
          *(short *)(param_1 + 0x154) = (short)*(undefined4 *)(param_1 + 0x15c);
        }
      }
    }
  }
  return local_38;
}

