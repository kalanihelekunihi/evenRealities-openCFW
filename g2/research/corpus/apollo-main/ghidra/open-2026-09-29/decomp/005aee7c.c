
int cff_font_load(undefined4 param_1,int param_2,uint param_3,undefined4 *param_4,undefined4 param_5
                 ,char param_6,char param_7)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int local_78;
  undefined4 local_74;
  undefined1 auStack_70 [12];
  uint local_64;
  undefined1 auStack_4c [12];
  undefined4 local_40;
  undefined4 *puStack_28;
  
  local_74 = *(undefined4 *)(param_2 + 0x1c);
  puStack_28 = param_4;
  FUN_0043c0e4(param_4,0xc40,0);
  FUN_0043c0e4(auStack_4c,0x24,0);
  iVar3 = *(int *)(param_2 + 8);
  *param_4 = param_1;
  param_4[1] = param_2;
  param_4[2] = local_74;
  *(char *)(param_4 + 8) = param_7;
  param_4[3] = iVar3;
  local_78 = FT_Stream_ReadFields(param_2,DAT_005af7b0,param_4);
  if (local_78 != 0) goto LAB_005af2ca;
  if (param_7 == '\0') {
    bVar1 = FT_Stream_ReadChar(param_2,&local_78);
    if (local_78 != 0) goto LAB_005af2ca;
    if (((*(char *)(param_4 + 6) != '\x01') || (*(byte *)((int)param_4 + 0x1a) < 4)) || (4 < bVar1))
    {
      local_78 = 2;
      goto LAB_005af2ca;
    }
  }
  else {
    if ((*(char *)(param_4 + 6) != '\x02') || (*(byte *)((int)param_4 + 0x1a) < 5)) {
      local_78 = 2;
      goto LAB_005af2ca;
    }
    uVar4 = FT_Stream_ReadUShort(param_2,&local_78);
    param_4[7] = uVar4;
    if (local_78 != 0) goto LAB_005af2ca;
  }
  local_78 = FT_Stream_Seek(param_2,iVar3 + (uint)*(byte *)((int)param_4 + 0x1a));
  if (local_78 != 0) {
    if (param_6 != '\0') {
      local_78 = 2;
    }
    goto LAB_005af2ca;
  }
  if (param_7 == '\0') {
    local_78 = cff_index_init(param_4 + 9,param_2,0,0);
    if (local_78 != 0) {
      if (param_6 != '\0') {
        local_78 = 2;
      }
      goto LAB_005af2ca;
    }
    if ((1 < (uint)param_4[0xc]) && ((uint)param_4[0xf] < (uint)param_4[0xc])) {
      if (param_6 == '\0') {
        local_78 = 3;
      }
      else {
        local_78 = 2;
      }
      goto LAB_005af2ca;
    }
    local_78 = cff_index_init(param_4 + 0x136,param_2,0,0);
    if ((((local_78 != 0) || (local_78 = cff_index_init(auStack_4c,param_2,1,0), local_78 != 0)) ||
        (local_78 = cff_index_init(param_4 + 0x1b,param_2,1,0), local_78 != 0)) ||
       (local_78 = cff_index_get_pointers
                             (auStack_4c,param_4 + 0x154,param_4 + 0x155,param_4 + 0x156),
       local_78 != 0)) goto LAB_005af2ca;
    if ((uint)param_4[0x139] < (uint)param_4[0xc]) {
      local_78 = 3;
      goto LAB_005af2ca;
    }
  }
  else {
    FUN_0043c0e4(param_4 + 0x136,0x24,0);
    param_4[0x13b] = *(undefined4 *)(param_2 + 8);
    param_4[0x13c] = param_4[7];
    local_78 = FT_Stream_Skip(param_2,param_4[7]);
    if ((local_78 != 0) ||
       (local_78 = cff_index_init(param_4 + 0x1b,param_2,1,param_7), local_78 != 0))
    goto LAB_005af2ca;
  }
  param_4[0x153] = local_40;
  if (param_6 == '\0') {
    uVar7 = 0;
    if (1 < (uint)param_4[0xc]) {
      local_78 = 3;
      goto LAB_005af2ca;
    }
  }
  else {
    uVar7 = param_3 & 0xffff;
    if ((0 < (int)param_3) && ((uint)param_4[0xc] <= uVar7)) {
      local_78 = 6;
      goto LAB_005af2ca;
    }
    param_4[4] = param_4[0xc];
  }
  if (-1 < (int)param_3) {
    if (param_7 == '\0') {
      uVar4 = 0x1000;
    }
    else {
      uVar4 = 0x3000;
    }
    local_78 = cff_subfont_load(param_4 + 0x157,param_4 + 0x136,uVar7,param_2,iVar3,uVar4,param_4,
                                param_5);
    if (((local_78 == 0) &&
        (local_78 = FT_Stream_Seek(param_2,param_4[0x173] + iVar3), local_78 == 0)) &&
       (local_78 = cff_index_init(param_4 + 0x12d,param_2,0,param_7), local_78 == 0)) {
      if ((param_4[0x178] == 0xffff) && (param_7 == '\0')) {
        param_4[0x1fa] = 0;
        local_78 = 0;
      }
      else {
        local_78 = cff_vstore_load(param_4 + 0x30a,param_2,iVar3,param_4[0x184]);
        if ((local_78 != 0) ||
           ((local_78 = FT_Stream_Seek(param_2,param_4[0x180] + iVar3), local_78 != 0 ||
            (local_78 = cff_index_init(auStack_70,param_2,0,param_7), local_78 != 0))))
        goto LAB_005af2ca;
        if (local_64 < 0x101) {
          param_4[0x1fa] = local_64;
          iVar5 = ft_mem_realloc(local_74,0x28c,0,local_64,0,&local_78);
          if (local_78 == 0) {
            for (uVar6 = 0; uVar6 < local_64; uVar6 = uVar6 + 1) {
              param_4[uVar6 + 0x1fb] = uVar6 * 0x28c + iVar5;
            }
            for (uVar6 = 0; uVar6 < local_64; uVar6 = uVar6 + 1) {
              if (param_7 == '\0') {
                uVar4 = 0x1000;
              }
              else {
                uVar4 = 0x4000;
              }
              local_78 = cff_subfont_load(param_4[uVar6 + 0x1fb],auStack_70,uVar6,param_2,iVar3,
                                          uVar4,param_4,param_5);
              if (local_78 != 0) goto LAB_005af210;
            }
            if ((param_7 == '\0') || (1 < local_64)) {
              local_78 = CFF_Load_FD_Select(param_4 + 0x2fb,param_4[0x130],param_2,
                                            param_4[0x181] + iVar3);
            }
          }
        }
LAB_005af210:
        cff_index_done(auStack_70);
        if (local_78 != 0) goto LAB_005af2ca;
      }
      if (param_4[0x173] == 0) {
        local_78 = 3;
      }
      else {
        param_4[5] = param_4[0x130];
        local_78 = cff_index_get_pointers(param_4 + 0x1b,param_4 + 0x152,0,0);
        if (local_78 == 0) {
          if ((param_7 == '\0') && (param_4[5] != 0)) {
            if ((param_4[0x178] == 0xffff) || (param_6 == '\0')) {
              uVar2 = 0;
            }
            else {
              uVar2 = 1;
            }
            local_78 = cff_charset_load(param_4 + 0x127,param_4[5],param_2,iVar3,param_4[0x171],
                                        uVar2);
            if ((local_78 != 0) ||
               ((param_4[0x178] == 0xffff &&
                (local_78 = cff_encoding_load(param_4 + 0x24,param_4 + 0x127,param_4[5],param_2,
                                              iVar3,param_4[0x172]), local_78 != 0))))
            goto LAB_005af2ca;
          }
          uVar4 = cff_index_get_name(param_4,uVar7);
          param_4[0x151] = uVar4;
        }
      }
    }
  }
LAB_005af2ca:
  cff_index_done(auStack_4c);
  return local_78;
}

