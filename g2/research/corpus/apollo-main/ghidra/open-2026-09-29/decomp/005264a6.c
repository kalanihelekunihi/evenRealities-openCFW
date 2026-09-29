
uint FT_Open_Face(undefined4 *param_1,byte *param_2,int param_3,byte *param_4,char param_5)

{
  int iVar1;
  short *psVar2;
  int iVar3;
  undefined1 uVar4;
  undefined4 *puVar5;
  byte *pbVar6;
  byte *pbVar7;
  undefined4 *puVar8;
  byte *local_50;
  byte *local_4c;
  int *local_48;
  uint local_44;
  int local_40;
  undefined4 local_3c;
  undefined4 *local_38;
  undefined4 local_34;
  undefined4 *local_30;
  int iStack_2c;
  byte *local_28;
  
  puVar8 = (undefined4 *)0x0;
  local_34 = 0;
  local_3c = 0;
  local_40 = 0;
  iVar3 = 0;
  if (((param_4 == (byte *)0x0) && (-1 < param_3)) || (param_2 == (byte *)0x0)) {
    return 6;
  }
  if (((int)((uint)*param_2 << 0x1e) < 0) && (*(int *)(param_2 + 0x10) != 0)) {
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  local_38 = param_1;
  iStack_2c = param_3;
  local_28 = param_4;
  local_44 = FT_Stream_New(param_1,param_2,&local_3c);
  if (local_44 == 0) {
    local_34 = *local_38;
    if (((int)((uint)*param_2 << 0x1c) < 0) && (*(int *)(param_2 + 0x14) != 0)) {
      puVar8 = *(undefined4 **)(param_2 + 0x14);
      if ((int)((uint)*(byte *)*puVar8 << 0x1f) < 0) {
        local_50 = (byte *)0x0;
        local_4c = (byte *)0x0;
        if ((int)((uint)*param_2 << 0x1b) < 0) {
          local_50 = *(byte **)(param_2 + 0x18);
          local_4c = *(byte **)(param_2 + 0x1c);
        }
        local_48 = &local_40;
        local_44 = open_face(puVar8,&local_3c,uVar4,param_3);
        if (local_44 == 0) {
LAB_00526548:
          iVar3 = ft_mem_alloc(local_34,0xc,&local_44);
          if (local_44 == 0) {
            *(int *)(iVar3 + 8) = local_40;
            FT_List_Add(*(int *)(local_40 + 0x60) + 0x10,iVar3);
            if (-1 < param_3) {
              local_44 = FT_New_GlyphSlot(local_40,0);
              if ((local_44 != 0) || (local_44 = FT_New_Size(local_40,&local_50), local_44 != 0))
              goto LAB_00526594;
              *(byte **)(local_40 + 0x58) = local_50;
              local_44 = 0;
            }
            if ((int)((uint)*(byte *)(local_40 + 8) << 0x1f) < 0) {
              if (*(short *)(local_40 + 0x4a) < 0) {
                *(short *)(local_40 + 0x4a) = -*(short *)(local_40 + 0x4a);
              }
              if (-1 < (int)((uint)*(byte *)(local_40 + 8) << 0x1a)) {
                *(undefined2 *)(local_40 + 0x4e) = *(undefined2 *)(local_40 + 0x4a);
              }
            }
            if ((int)((uint)*(byte *)(local_40 + 8) << 0x1e) < 0) {
              for (iVar3 = 0; iVar3 < *(int *)(local_40 + 0x1c); iVar3 = iVar3 + 1) {
                psVar2 = (short *)(*(int *)(local_40 + 0x20) + iVar3 * 0x10);
                if (*psVar2 < 0) {
                  *psVar2 = -*psVar2;
                }
                if (*(int *)(psVar2 + 4) < 0) {
                  *(int *)(psVar2 + 4) = -*(int *)(psVar2 + 4);
                }
                if (*(int *)(psVar2 + 6) < 0) {
                  *(int *)(psVar2 + 6) = -*(int *)(psVar2 + 6);
                }
                if (((*psVar2 < 0) || (*(int *)(psVar2 + 4) < 0)) || (*(int *)(psVar2 + 6) < 0)) {
                  psVar2[1] = 0;
                  *psVar2 = 0;
                  psVar2[2] = 0;
                  psVar2[3] = 0;
                  psVar2[4] = 0;
                  psVar2[5] = 0;
                  psVar2[6] = 0;
                  psVar2[7] = 0;
                }
              }
            }
            puVar8 = *(undefined4 **)(local_40 + 0x80);
            *puVar8 = 0x10000;
            puVar8[1] = 0;
            puVar8[2] = 0;
            puVar8[3] = 0x10000;
            puVar8[4] = 0;
            puVar8[5] = 0;
            puVar8[0x10] = 1;
            *(undefined1 *)(puVar8 + 0xe) = 0xff;
            if (local_28 != (byte *)0x0) {
              *(int *)local_28 = local_40;
              return local_44;
            }
            FT_Done_Face(local_40);
            return local_44;
          }
          goto LAB_00526594;
        }
      }
      else {
        local_44 = 0x20;
      }
      FT_Stream_Free(local_3c,uVar4);
      goto LAB_00526594;
    }
    local_44 = 0xb;
    puVar5 = local_38 + 5;
    local_30 = puVar5 + local_38[4];
    for (; puVar5 < local_30; puVar5 = puVar5 + 1) {
      if ((int)((uint)**(byte **)*puVar5 << 0x1f) < 0) {
        pbVar6 = (byte *)0x0;
        pbVar7 = (byte *)0x0;
        puVar8 = (undefined4 *)*puVar5;
        if ((int)((uint)*param_2 << 0x1b) < 0) {
          pbVar6 = *(byte **)(param_2 + 0x18);
          pbVar7 = *(byte **)(param_2 + 0x1c);
        }
        local_48 = &local_40;
        local_50 = pbVar6;
        local_4c = pbVar7;
        local_44 = open_face(puVar8,&local_3c,uVar4,param_3);
        if (local_44 == 0) goto LAB_00526548;
        if (((param_5 != '\0') &&
            (iVar1 = FUN_0046cacc(*(undefined4 *)(*(int *)*puVar5 + 8),DAT_00526808), iVar1 == 0))
           && ((local_44 & 0xff) == 0x8e)) {
          local_44 = FT_Stream_Seek(local_3c,0);
          if (local_44 != 0) break;
          local_4c = local_28;
          local_50 = pbVar7;
          local_44 = open_face_PS_from_sfnt_stream(local_38,local_3c,param_3,pbVar6);
          if (local_44 == 0) {
            FT_Stream_Free(local_3c,uVar4);
            return local_44;
          }
        }
        if ((local_44 & 0xff) != 2) break;
      }
    }
  }
  if ((((local_44 & 0xff) == 0x51) || ((local_44 & 0xff) == 2)) || ((local_44 & 0xff) == 0x55)) {
    if ((param_5 != '\0') &&
       (local_50 = param_2, local_44 = load_mac_face(local_38,local_3c,param_3,local_28),
       local_44 == 0)) {
      FT_Stream_Free(local_3c,uVar4);
      return local_44;
    }
    if ((local_44 & 0xff) == 2) {
      local_44 = 2;
    }
  }
  FT_Stream_Free(local_3c,uVar4);
LAB_00526594:
  if (iVar3 == 0) {
    if (local_40 != 0) {
      destroy_face(local_34,local_40,puVar8);
    }
  }
  else {
    FT_Done_Face(local_40);
  }
  return local_44;
}

