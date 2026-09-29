
undefined8 cff_index_init(int *param_1,int param_2,char param_3,uint param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint local_20;
  
  uVar3 = *(undefined4 *)(param_2 + 0x1c);
  local_20 = param_4;
  FUN_0043c0e4(param_1,0x24,0);
  *param_1 = param_2;
  param_1[1] = *(int *)(param_2 + 8);
  if ((param_4 & 0xff) == 0) {
    iVar2 = FT_Stream_ReadUShort(param_2,&local_20);
    if (local_20 != 0) goto LAB_005ad8a8;
    param_1[2] = 3;
  }
  else {
    iVar2 = FT_Stream_ReadULong(param_2,&local_20);
    if (local_20 != 0) goto LAB_005ad8a8;
    param_1[2] = 5;
  }
  if ((iVar2 != 0) && (bVar1 = FT_Stream_ReadChar(param_2,&local_20), local_20 == 0)) {
    if ((bVar1 == 0) || (4 < bVar1)) {
      local_20 = 8;
    }
    else {
      param_1[3] = iVar2;
      *(byte *)(param_1 + 4) = bVar1;
      iVar2 = (uint)bVar1 * (iVar2 + 1);
      param_1[5] = iVar2 + param_1[2] + param_1[1];
      local_20 = FT_Stream_Skip(param_2,iVar2 - (uint)bVar1);
      if ((local_20 == 0) && (iVar2 = cff_index_read_offset(param_1,&local_20), local_20 == 0)) {
        if (iVar2 == 0) {
          local_20 = 8;
        }
        else {
          param_1[6] = iVar2 + -1;
          if (param_3 == '\0') {
            local_20 = FT_Stream_Skip(param_2);
          }
          else {
            local_20 = FT_Stream_ExtractFrame(param_2,iVar2 + -1,param_1 + 8);
          }
        }
      }
    }
  }
LAB_005ad8a8:
  if (local_20 != 0) {
    ft_mem_free(uVar3,param_1[7]);
    param_1[7] = 0;
  }
  return CONCAT44(local_20,local_20);
}

