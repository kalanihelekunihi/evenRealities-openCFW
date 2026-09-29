
int ft_var_load_delta_set_index_mapping(int param_1,undefined4 param_2,uint *param_3,uint *param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  int local_30;
  uint local_2c;
  uint *puStack_28;
  
  iVar4 = *(int *)(param_1 + 0x68);
  uVar6 = *(undefined4 *)(iVar4 + 0x1c);
  puStack_28 = param_4;
  local_30 = FT_Stream_Seek(iVar4);
  if ((local_30 == 0) && (uVar1 = FT_Stream_ReadUShort(iVar4,&local_30), local_30 == 0)) {
    uVar2 = FT_Stream_ReadUShort(iVar4,&local_30);
    *param_3 = uVar2;
    if (local_30 == 0) {
      if ((uVar1 & 0xffc0) == 0) {
        local_2c = (uVar1 & 0xf) + 1;
        iVar5 = 1 << local_2c;
        uVar2 = ft_mem_realloc(uVar6,4,0,*param_3,0,&local_30);
        param_3[2] = uVar2;
        if (local_30 == 0) {
          uVar2 = ft_mem_realloc(uVar6,4,0,*param_3,0,&local_30);
          param_3[1] = uVar2;
          if (local_30 == 0) {
            for (uVar2 = 0; uVar2 < *param_3; uVar2 = uVar2 + 1) {
              uVar8 = 0;
              for (uVar7 = 0; uVar7 < ((uVar1 & 0x3f) >> 4) + 1; uVar7 = uVar7 + 1) {
                uVar3 = FT_Stream_ReadChar(iVar4,&local_30);
                if (local_30 != 0) {
                  return local_30;
                }
                uVar8 = uVar3 & 0xff | uVar8 << 8;
              }
              uVar7 = uVar8 >> (local_2c & 0xff);
              if (*param_4 <= uVar7) {
                return 8;
              }
              *(uint *)(param_3[1] + uVar2 * 4) = uVar7;
              uVar8 = iVar5 - 1U & uVar8;
              if (*(uint *)(param_4[1] + uVar7 * 0x10) <= uVar8) {
                return 8;
              }
              *(uint *)(param_3[2] + uVar2 * 4) = uVar8;
            }
          }
        }
      }
      else {
        local_30 = 8;
      }
    }
  }
  return local_30;
}

