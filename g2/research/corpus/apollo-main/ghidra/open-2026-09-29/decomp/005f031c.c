
int load_truetype_glyph(int *param_1,int param_2,uint param_3,char param_4)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  int local_f0;
  int local_ec;
  char local_e8;
  short local_e6;
  int local_e4;
  int local_e0;
  uint local_dc;
  short local_d8;
  short local_d6;
  int local_d4;
  int local_d0;
  int local_cc;
  undefined4 local_c4;
  int local_c0;
  uint local_bc;
  int local_b8;
  int local_b4;
  undefined2 local_b0;
  undefined2 local_ae;
  int *local_ac;
  int *local_a8;
  undefined4 *local_a4;
  undefined4 local_9c;
  undefined4 uStack_98;
  int local_94;
  int iStack_90;
  int local_8c;
  int iStack_88;
  int local_84;
  int iStack_80;
  int local_7c;
  int iStack_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  int local_64;
  int local_60;
  int local_5c;
  int local_58;
  undefined1 auStack_54 [40];
  int iStack_2c;
  uint local_28;
  
  local_f0 = 0;
  iVar8 = *param_1;
  local_ec = param_1[3];
  bVar2 = false;
  local_e8 = '\0';
  if (*(ushort *)(iVar8 + 0x122) < param_3) {
    *(short *)(iVar8 + 0x122) = (short)param_3;
  }
  param_1[5] = param_2;
  if ((int)((uint)*(byte *)(param_1 + 4) << 0x1f) < 0) {
    uVar11 = 0x10000;
    local_e4 = 0x10000;
  }
  else {
    local_e4 = *(int *)(*(int *)(param_1[1] + 0x2c) + 4);
    uVar11 = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 8);
  }
  iStack_2c = param_2;
  local_28 = param_3;
  if (*(int *)(*(int *)(iVar8 + 0x80) + 0x34) == 0) {
    iVar9 = tt_face_get_location(iVar8,param_2,param_1 + 7);
  }
  else {
    local_f0 = (**(code **)**(undefined4 **)(*(int *)(iVar8 + 0x80) + 0x34))
                         (*(undefined4 *)(*(int *)(*(int *)(iVar8 + 0x80) + 0x34) + 4),param_2,
                          &local_c4);
    if (local_f0 != 0) goto LAB_005f0aee;
    local_e8 = '\x01';
    iVar9 = 0;
    param_1[7] = local_c0;
    FUN_0043c0e4(auStack_54,0x28,0);
    FT_Stream_OpenMemory(auStack_54,local_c4,local_c0);
    param_1[6] = (int)auStack_54;
  }
  bVar1 = false;
  if (0 < param_1[7]) {
    if ((*(int *)(iVar8 + 0x2b4) == 0) && (*(int *)(*(int *)(iVar8 + 0x80) + 0x34) == 0)) {
      local_f0 = 8;
      goto LAB_005f0aee;
    }
    local_f0 = (**(code **)(iVar8 + 0x208))
                         (param_1,param_2,iVar9 + *(int *)(iVar8 + 0x2b4),param_1[7]);
    if (local_f0 != 0) goto LAB_005f0aee;
    bVar2 = true;
    local_f0 = (**(code **)(iVar8 + 0x210))(param_1);
    if (((local_f0 != 0) || (local_f0 = tt_get_metrics(param_1,param_2), local_f0 != 0)) ||
       (bVar1 = true, param_4 != '\0')) goto LAB_005f0aee;
  }
  bVar2 = bVar1;
  if ((param_1[7] == 0) || ((short)param_1[8] == 0)) {
    param_1[9] = 0;
    param_1[0xb] = 0;
    param_1[10] = 0;
    param_1[0xc] = 0;
    local_f0 = tt_get_metrics(param_1,param_2);
    if ((local_f0 == 0) && (param_4 == '\0')) {
      tt_loader_set_pp(param_1);
      tt_get_metrics_incr_overrides(param_1,param_2);
      if (((*(uint *)(iVar8 + 4) & DAT_005f0b24) != 0) || (*(int *)(iVar8 + 8) << 0x10 < 0)) {
        local_ec = *DAT_005f0fac;
        local_9c = *DAT_005f0fb0;
        uStack_98 = DAT_005f0fb0[1];
        local_74 = param_1[0x11];
        local_70 = param_1[0x12];
        local_6c = param_1[0x13];
        local_68 = param_1[0x14];
        local_64 = param_1[0x2d];
        local_60 = param_1[0x2e];
        local_5c = param_1[0x2f];
        local_58 = param_1[0x30];
        local_ae = 4;
        local_b0 = 4;
        local_ac = &local_74;
        local_a8 = &local_ec;
        local_a4 = &local_9c;
        local_f0 = TT_Vary_Apply_Glyph_Deltas(*param_1,param_2,&local_b0,4);
        if (local_f0 != 0) goto LAB_005f0aee;
        param_1[0x11] = local_74;
        param_1[0x12] = local_70;
        param_1[0x13] = local_6c;
        param_1[0x14] = local_68;
        param_1[0x2d] = local_64;
        param_1[0x2e] = local_60;
        param_1[0x2f] = local_5c;
        param_1[0x30] = local_58;
        if (-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1e)) {
          param_1[0xf] = param_1[0x13] - param_1[0x11];
        }
        local_f0 = 0;
        if (-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1b)) {
          param_1[0x2c] = param_1[0x2f] - param_1[0x2d];
        }
      }
      if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
        iVar9 = FT_MulFix(param_1[0x11],local_e4);
        param_1[0x11] = iVar9;
        iVar9 = FT_MulFix(param_1[0x13],local_e4);
        param_1[0x13] = iVar9;
        iVar9 = FT_MulFix(param_1[0x2d],local_e4);
        param_1[0x2d] = iVar9;
        iVar9 = FT_MulFix(param_1[0x2e],uVar11);
        param_1[0x2e] = iVar9;
        iVar9 = FT_MulFix(param_1[0x2f],local_e4);
        param_1[0x2f] = iVar9;
        iVar9 = FT_MulFix(param_1[0x30],uVar11);
        param_1[0x30] = iVar9;
      }
      local_f0 = 0;
    }
  }
  else {
    tt_loader_set_pp(param_1);
    tt_get_metrics_incr_overrides(param_1,param_2);
    if ((short)param_1[8] < 1) {
      if ((short)param_1[8] < 0) {
        local_e0 = *(int *)(iVar8 + 100);
        *(undefined2 *)(param_1 + 8) = 0xffff;
        iVar3 = ft_list_get_node_at(param_1 + 0x33,local_28);
        for (iVar9 = iVar3; iVar9 != 0; iVar9 = *(int *)(iVar9 + 4)) {
          *(undefined4 *)(iVar9 + 8) = 0xffffffff;
        }
        iVar9 = FT_List_Find(param_1 + 0x33,param_2);
        if (iVar9 == 0) {
          if (iVar3 == 0) {
            iVar9 = ft_mem_alloc(local_e0,0xc,&local_f0);
            if (local_f0 != 0) goto LAB_005f0aee;
            *(int *)(iVar9 + 8) = param_2;
            FT_List_Add(param_1 + 0x33,iVar9);
          }
          else {
            *(int *)(iVar3 + 8) = param_2;
          }
          local_dc = (uint)*(short *)(local_ec + 0x16);
          local_b4 = (int)*(short *)(local_ec + 0x14);
          local_f0 = (**(code **)(iVar8 + 0x218))(param_1);
          if (local_f0 == 0) {
            local_b8 = param_1[0x29];
            (**(code **)(iVar8 + 0x20c))(param_1);
            bVar2 = false;
            if (((*(uint *)(iVar8 + 4) & DAT_005f0b24) != 0) || (*(int *)(iVar8 + 8) << 0x10 < 0)) {
              iVar3 = 0;
              iVar13 = 0;
              local_e6 = (short)*(undefined4 *)(local_ec + 0x54);
              local_d8 = (short)*(undefined4 *)(local_ec + 0x54) + 4;
              local_d4 = 0;
              local_d0 = 0;
              local_cc = 0;
              local_d6 = local_d8;
              iVar9 = ft_mem_realloc(local_e0,8,0,(int)local_d8,0,&local_f0);
              if ((local_f0 == 0) &&
                 ((iVar3 = ft_mem_realloc(local_e0,1,0,(int)local_d6,0,&local_f0), local_f0 == 0 &&
                  (iVar13 = ft_mem_realloc(local_e0,2,0,(int)local_d6,0,&local_f0), local_f0 == 0)))
                 ) {
                bVar1 = false;
              }
              else {
                bVar1 = true;
              }
              if (!bVar1) {
                iVar4 = *(int *)(local_ec + 0x58);
                for (sVar5 = 0; sVar5 < local_e6; sVar5 = sVar5 + 1) {
                  *(undefined4 *)(iVar9 + sVar5 * 8) = *(undefined4 *)(iVar4 + 8);
                  *(undefined4 *)(iVar9 + sVar5 * 8 + 4) = *(undefined4 *)(iVar4 + 0xc);
                  *(undefined1 *)(iVar3 + sVar5) = 1;
                  *(short *)(iVar13 + sVar5 * 2) = sVar5;
                  iVar4 = iVar4 + 0x20;
                }
                *(int *)(iVar9 + sVar5 * 8) = param_1[0x11];
                *(int *)(iVar9 + sVar5 * 8 + 4) = param_1[0x12];
                *(undefined1 *)(iVar3 + sVar5) = 1;
                *(short *)(iVar13 + sVar5 * 2) = sVar5;
                sVar6 = sVar5 + 1;
                *(int *)(iVar9 + sVar6 * 8) = param_1[0x13];
                *(int *)(iVar9 + sVar6 * 8 + 4) = param_1[0x14];
                *(undefined1 *)(iVar3 + sVar6) = 1;
                *(short *)(iVar13 + sVar6 * 2) = sVar6;
                sVar6 = sVar5 + 2;
                *(int *)(iVar9 + sVar6 * 8) = param_1[0x2d];
                *(int *)(iVar9 + sVar6 * 8 + 4) = param_1[0x2e];
                *(undefined1 *)(iVar3 + sVar6) = 1;
                *(short *)(iVar13 + sVar6 * 2) = sVar6;
                sVar5 = sVar5 + 3;
                *(int *)(iVar9 + sVar5 * 8) = param_1[0x2f];
                *(int *)(iVar9 + sVar5 * 8 + 4) = param_1[0x30];
                *(undefined1 *)(iVar3 + sVar5) = 1;
                *(short *)(iVar13 + sVar5 * 2) = sVar5;
                local_d4 = iVar9;
                local_d0 = iVar3;
                local_cc = iVar13;
                local_f0 = TT_Vary_Apply_Glyph_Deltas(iVar8,param_2,&local_d8,(int)local_d6);
                if (local_f0 == 0) {
                  iVar3 = *(int *)(local_ec + 0x58);
                  for (sVar5 = 0; sVar5 < local_e6; sVar5 = sVar5 + 1) {
                    if ((int)((uint)*(byte *)(iVar3 + 4) << 0x1e) < 0) {
                      *(int *)(iVar3 + 8) = (int)*(short *)(iVar9 + sVar5 * 8);
                      *(int *)(iVar3 + 0xc) = (int)*(short *)(iVar9 + sVar5 * 8 + 4);
                    }
                    iVar3 = iVar3 + 0x20;
                  }
                  param_1[0x11] = *(int *)(iVar9 + sVar5 * 8);
                  param_1[0x12] = *(int *)(iVar9 + sVar5 * 8 + 4);
                  param_1[0x13] = *(int *)(iVar9 + sVar5 * 8 + 8);
                  param_1[0x14] = *(int *)(iVar9 + sVar5 * 8 + 0xc);
                  param_1[0x2d] = *(int *)(iVar9 + sVar5 * 8 + 0x10);
                  param_1[0x2e] = *(int *)(iVar9 + sVar5 * 8 + 0x14);
                  param_1[0x2f] = *(int *)(iVar9 + sVar5 * 8 + 0x18);
                  param_1[0x30] = *(int *)(iVar9 + sVar5 * 8 + 0x1c);
                  if (-1 < (int)((uint)*(byte *)(iVar8 + 0x2c0) << 0x1e)) {
                    param_1[0xf] = param_1[0x13] - param_1[0x11];
                  }
                  if (-1 < (int)((uint)*(byte *)(iVar8 + 0x2c0) << 0x1b)) {
                    param_1[0x2c] = param_1[0x2f] - param_1[0x2d];
                  }
                }
              }
              ft_mem_free(local_e0,local_d4);
              local_d4 = 0;
              ft_mem_free(local_e0,local_d0);
              local_d0 = 0;
              ft_mem_free(local_e0,local_cc);
              local_cc = 0;
              if (local_f0 != 0) goto LAB_005f0aee;
            }
            if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
              iVar9 = FT_MulFix(param_1[0x11],local_e4);
              param_1[0x11] = iVar9;
              iVar9 = FT_MulFix(param_1[0x13],local_e4);
              param_1[0x13] = iVar9;
              iVar9 = FT_MulFix(param_1[0x2d],local_e4);
              param_1[0x2d] = iVar9;
              iVar9 = FT_MulFix(param_1[0x2e],uVar11);
              param_1[0x2e] = iVar9;
              iVar9 = FT_MulFix(param_1[0x2f],local_e4);
              param_1[0x2f] = iVar9;
              iVar9 = FT_MulFix(param_1[0x30],uVar11);
              param_1[0x30] = iVar9;
            }
            uVar10 = local_dc;
            if (param_1[4] << 0x15 < 0) {
              FT_GlyphLoader_Add(local_ec);
              *(undefined4 *)(param_1[2] + 0x48) = DAT_005f1558;
            }
            else {
              iVar3 = 0;
              local_bc = *(uint *)(local_ec + 0x54);
              iVar9 = *(int *)(local_ec + 0x30);
              local_e0 = param_1[6];
              local_e4 = param_1[7];
              FT_GlyphLoader_Add(local_ec);
              for (uVar12 = 0; uVar12 < local_bc; uVar12 = uVar12 + 1) {
                local_94 = param_1[0x11];
                iStack_90 = param_1[0x12];
                local_8c = param_1[0x13];
                iStack_88 = param_1[0x14];
                local_84 = param_1[0x2d];
                iStack_80 = param_1[0x2e];
                local_7c = param_1[0x2f];
                iStack_78 = param_1[0x30];
                iVar4 = param_1[0xf];
                iVar13 = param_1[0x2c];
                uVar7 = (uint)*(short *)(local_ec + 0x16);
                local_f0 = load_truetype_glyph(param_1,*(undefined4 *)
                                                        (*(int *)(local_ec + 0x34) + iVar9 * 0x20 +
                                                        uVar12 * 0x20),local_28 + 1,0);
                if (local_f0 != 0) goto LAB_005f0aee;
                iVar3 = *(int *)(local_ec + 0x34) + iVar9 * 0x20 + uVar12 * 0x20;
                if (-1 < (int)((uint)*(ushort *)(iVar3 + 4) << 0x16)) {
                  param_1[0x11] = local_94;
                  param_1[0x12] = iStack_90;
                  param_1[0x13] = local_8c;
                  param_1[0x14] = iStack_88;
                  param_1[0x2d] = local_84;
                  param_1[0x2e] = iStack_80;
                  param_1[0x2f] = local_7c;
                  param_1[0x30] = iStack_78;
                  param_1[0xf] = iVar4;
                  param_1[0x2c] = iVar13;
                }
                uVar10 = (uint)*(short *)(local_ec + 0x16);
                if ((uVar10 != uVar7) &&
                   (local_f0 = TT_Process_Composite_Component(param_1,iVar3,local_dc,uVar7),
                   local_f0 != 0)) goto LAB_005f0aee;
              }
              param_1[6] = local_e0;
              param_1[7] = local_e4;
              param_1[0x29] = local_b8;
              if (((-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1e)) &&
                  ((int)((uint)*(ushort *)(iVar3 + 4) << 0x17) < 0)) && (local_dc < uVar10)) {
                local_f0 = TT_Process_Composite_Glyph(param_1,local_dc,local_b4);
              }
            }
          }
        }
        else {
          local_f0 = 0x15;
        }
      }
    }
    else {
      local_f0 = (**(code **)(iVar8 + 0x214))(param_1);
      if (local_f0 == 0) {
        (**(code **)(iVar8 + 0x20c))(param_1);
        bVar2 = false;
        local_f0 = TT_Process_Simple_Glyph(param_1);
        if (local_f0 == 0) {
          FT_GlyphLoader_Add(local_ec);
        }
      }
    }
  }
LAB_005f0aee:
  if (bVar2) {
    (**(code **)(iVar8 + 0x20c))(param_1);
  }
  if (local_e8 != '\0') {
    (**(code **)(**(int **)(*(int *)(iVar8 + 0x80) + 0x34) + 4))
              (*(undefined4 *)(*(int *)(*(int *)(iVar8 + 0x80) + 0x34) + 4),&local_c4);
  }
  return local_f0;
}

