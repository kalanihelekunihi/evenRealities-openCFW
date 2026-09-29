
undefined8
cff_charset_load(uint *param_1,uint param_2,int param_3,int param_4,uint param_5,char param_6)

{
  byte bVar1;
  undefined2 uVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  int local_20;
  
  uVar7 = *(undefined4 *)(param_3 + 0x1c);
  local_20 = 0;
  uVar8 = param_2;
  if (param_5 < 3) {
    param_1[1] = param_5;
    if (param_5 == 0) {
      if (0xe5 < param_2) {
        local_20 = 3;
        goto LAB_005adfac;
      }
      uVar8 = 0;
      uVar4 = ft_mem_realloc(uVar7,2,0,param_2,0,&local_20);
      param_1[2] = uVar4;
      if (local_20 != 0) goto LAB_005adfac;
      FUN_00439be4(param_1[2],PTR_DAT_005aebe8,param_2 << 1);
    }
    else if (param_5 == 2) {
      if (0x57 < param_2) {
        local_20 = 3;
        goto LAB_005adfac;
      }
      uVar8 = 0;
      uVar4 = ft_mem_realloc(uVar7,2,0,param_2,0,&local_20);
      param_1[2] = uVar4;
      if (local_20 != 0) goto LAB_005adfac;
      FUN_00439be4(param_1[2],PTR_DAT_005aebf0,param_2 << 1);
    }
    else {
      if (1 < param_5) {
        local_20 = 3;
        goto LAB_005adfac;
      }
      if (0xa6 < param_2) {
        local_20 = 3;
        goto LAB_005adfac;
      }
      uVar8 = 0;
      uVar4 = ft_mem_realloc(uVar7,2,0,param_2,0,&local_20);
      param_1[2] = uVar4;
      if (local_20 != 0) goto LAB_005adfac;
      FUN_00439be4(param_1[2],PTR_DAT_005aebec,param_2 << 1);
    }
  }
  else {
    param_1[1] = param_5 + param_4;
    local_20 = FT_Stream_Seek(param_3,param_1[1]);
    if (local_20 != 0) goto LAB_005adfac;
    bVar1 = FT_Stream_ReadChar(param_3,&local_20);
    *param_1 = (uint)bVar1;
    if (local_20 != 0) goto LAB_005adfac;
    uVar8 = 0;
    uVar4 = ft_mem_realloc(uVar7,2,0,param_2,0,&local_20);
    param_1[2] = uVar4;
    if (local_20 != 0) goto LAB_005adfac;
    *(undefined2 *)param_1[2] = 0;
    uVar4 = *param_1;
    if (uVar4 == 0) {
      if (param_2 != 0) {
        local_20 = FT_Stream_EnterFrame(param_3,(param_2 - 1) * 2);
        if (local_20 != 0) goto LAB_005adfac;
        for (uVar4 = 1; uVar4 < param_2; uVar4 = uVar4 + 1) {
          uVar2 = FT_Stream_GetUShort(param_3);
          *(undefined2 *)(param_1[2] + uVar4 * 2) = uVar2;
        }
        FT_Stream_ExitFrame(param_3);
      }
    }
    else {
      if ((uVar4 != 2) && (1 < uVar4)) {
        local_20 = 3;
        goto LAB_005adfac;
      }
      uVar4 = 1;
      while (uVar4 < param_2) {
        uVar3 = FT_Stream_ReadUShort(param_3,&local_20);
        if (local_20 != 0) goto LAB_005adfac;
        if (*param_1 == 2) {
          uVar5 = FT_Stream_ReadUShort(param_3,&local_20);
        }
        else {
          uVar5 = FT_Stream_ReadChar(param_3,&local_20);
          uVar5 = uVar5 & 0xff;
        }
        if (local_20 != 0) goto LAB_005adfac;
        if (0xffff - uVar5 < (uint)uVar3) {
          uVar5 = 0xffff - uVar3;
        }
        for (uVar6 = 0; (uVar4 < param_2 && (uVar6 <= uVar5)); uVar6 = uVar6 + 1) {
          *(ushort *)(param_1[2] + uVar4 * 2) = uVar3;
          uVar4 = uVar4 + 1;
          uVar3 = uVar3 + 1;
        }
      }
    }
  }
  if (param_6 != '\0') {
    local_20 = cff_charset_compute_cids(param_1,param_2,uVar7);
  }
LAB_005adfac:
  if (local_20 != 0) {
    ft_mem_free(uVar7,param_1[2]);
    param_1[2] = 0;
    ft_mem_free(uVar7,param_1[3]);
    param_1[3] = 0;
    *param_1 = 0;
    param_1[1] = 0;
    param_1[2] = 0;
  }
  return CONCAT44(uVar8,local_20);
}

