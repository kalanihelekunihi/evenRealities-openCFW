
uint Mac_Read_POST_Resource
               (undefined4 *param_1,undefined4 param_2,int param_3,int param_4,int param_5,
               undefined4 param_6)

{
  undefined1 uVar1;
  undefined4 uVar4;
  uint uVar5;
  undefined1 *puVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint local_38;
  int local_34;
  int local_30;
  undefined4 *local_28;
  undefined1 uVar2;
  undefined1 uVar3;
  
  local_38 = 1;
  uVar4 = *param_1;
  if (param_5 == -1) {
    param_5 = 0;
  }
  if (param_5 == 0) {
    uVar12 = 0;
    local_34 = param_4;
    local_30 = param_3;
    local_28 = param_1;
    for (iVar10 = 0; iVar10 < local_34; iVar10 = iVar10 + 1) {
      local_38 = FT_Stream_Seek(param_2,*(undefined4 *)(local_30 + iVar10 * 4));
      if (local_38 != 0) {
        return local_38;
      }
      uVar5 = FT_Stream_ReadULong(param_2,&local_38);
      if (local_38 != 0) {
        return local_38;
      }
      if ((0xffffff < uVar5) || (0xffffff - uVar5 < uVar12 + 6)) {
        return 9;
      }
      uVar12 = uVar5 + uVar12 + 6;
    }
    if (uVar12 + 2 < 6) {
      local_38 = 10;
    }
    else {
      puVar6 = (undefined1 *)ft_mem_alloc(uVar4,uVar12 + 2,&local_38);
      if (local_38 == 0) {
        *puVar6 = 0x80;
        puVar6[1] = 1;
        puVar6[2] = 0;
        puVar6[3] = 0;
        puVar6[4] = 0;
        puVar6[5] = 0;
        uVar5 = 6;
        iVar15 = 2;
        iVar14 = 0;
        iVar10 = 1;
        iVar11 = 0;
        while( true ) {
          uVar1 = (undefined1)((uint)iVar14 >> 8);
          uVar2 = (undefined1)((uint)iVar14 >> 0x10);
          uVar3 = (undefined1)((uint)iVar14 >> 0x18);
          if (local_34 <= iVar11) break;
          local_38 = FT_Stream_Seek(param_2,*(undefined4 *)(local_30 + iVar11 * 4));
          if ((local_38 != 0) || (uVar7 = FT_Stream_ReadULong(param_2,&local_38), local_38 != 0))
          goto LAB_00525f30;
          if (0x7fffffff < uVar7) {
            local_38 = 9;
            goto LAB_00525f30;
          }
          iVar8 = FT_Stream_ReadUShort(param_2,&local_38);
          if (local_38 != 0) goto LAB_00525f30;
          local_38 = 10;
          iVar9 = iVar8 >> 8;
          if (iVar9 != 0) {
            if (uVar7 < 3) {
              iVar13 = 0;
            }
            else {
              iVar13 = uVar7 - 2;
            }
            if (iVar9 == iVar10) {
              iVar9 = iVar10;
              iVar14 = iVar13 + iVar14;
            }
            else {
              if (uVar12 + 2 < iVar15 + 3U) goto LAB_00525f30;
              puVar6[iVar15] = (char)iVar14;
              puVar6[iVar15 + 1] = uVar1;
              puVar6[iVar15 + 2] = uVar2;
              puVar6[iVar15 + 3] = uVar3;
              if (iVar9 == 5) break;
              if (uVar12 + 2 < uVar5 + 6) goto LAB_00525f30;
              puVar6[uVar5] = 0x80;
              puVar6[uVar5 + 1] = (char)((uint)iVar8 >> 8);
              iVar15 = uVar5 + 2;
              puVar6[iVar15] = 0;
              puVar6[uVar5 + 3] = 0;
              puVar6[uVar5 + 4] = 0;
              puVar6[uVar5 + 5] = 0;
              uVar5 = uVar5 + 6;
              iVar14 = iVar13;
            }
            if (((uVar12 < uVar5) || (uVar12 < iVar13 + uVar5)) ||
               (local_38 = FT_Stream_Read(param_2,puVar6 + uVar5,iVar13), local_38 != 0))
            goto LAB_00525f30;
            uVar5 = iVar13 + uVar5;
            local_38 = 0;
            iVar10 = iVar9;
          }
          iVar11 = iVar11 + 1;
        }
        local_38 = 10;
        if (uVar5 + 2 <= uVar12 + 2) {
          puVar6[uVar5] = 0x80;
          puVar6[uVar5 + 1] = 3;
          if (iVar15 + 3U <= uVar12 + 2) {
            puVar6[iVar15] = (char)iVar14;
            puVar6[iVar15 + 1] = uVar1;
            puVar6[iVar15 + 2] = uVar2;
            puVar6[iVar15 + 3] = uVar3;
            iVar10 = open_face_from_buffer(local_28,puVar6,uVar5 + 2,0,DAT_00526800,param_6);
            return iVar10;
          }
        }
LAB_00525f30:
        if (local_38 != 0) {
          local_38 = 1;
        }
        ft_mem_free(uVar4,puVar6);
      }
    }
  }
  else {
    local_38 = 1;
  }
  return local_38;
}

