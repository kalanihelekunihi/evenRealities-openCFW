
int ft_var_readpackedpoints(int param_1,uint param_2,uint *param_3,undefined4 param_4)

{
  short sVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  short sVar7;
  undefined4 uVar8;
  uint uVar9;
  int local_28;
  undefined4 uStack_24;
  
  uVar8 = *(undefined4 *)(param_1 + 0x1c);
  local_28 = 0;
  *param_3 = 0;
  uStack_24 = param_4;
  uVar3 = FT_Stream_GetChar(param_1);
  uVar6 = uVar3 & 0xff;
  if (uVar6 == 0) {
    iVar4 = -1;
  }
  else {
    if ((int)(uVar3 << 0x18) < 0) {
      uVar6 = FT_Stream_GetChar(param_1);
      uVar6 = uVar6 & 0xff | (uVar3 & 0x7f) << 8;
    }
    if (param_2 < uVar6) {
      iVar4 = 0;
    }
    else {
      iVar4 = ft_mem_realloc(uVar8,2,0,uVar6 + 1,0,&local_28);
      if (local_28 == 0) {
        *param_3 = uVar6;
        sVar7 = 0;
        uVar3 = 0;
LAB_005f12f2:
        if (uVar3 < uVar6) {
          uVar5 = FT_Stream_GetChar(param_1);
          if ((int)(uVar5 << 0x18) < 0) {
            sVar1 = FT_Stream_GetUShort(param_1);
            sVar7 = sVar1 + sVar7;
            *(short *)(iVar4 + uVar3 * 2) = sVar7;
            uVar3 = uVar3 + 1;
            for (uVar9 = 0; uVar9 < (uVar5 & 0x7f); uVar9 = uVar9 + 1) {
              sVar1 = FT_Stream_GetUShort(param_1);
              sVar7 = sVar1 + sVar7;
              *(short *)(iVar4 + uVar3 * 2) = sVar7;
              uVar3 = uVar3 + 1;
              if (uVar6 <= uVar3) break;
            }
          }
          else {
            uVar2 = FT_Stream_GetChar(param_1);
            sVar7 = sVar7 + (uVar2 & 0xff);
            *(short *)(iVar4 + uVar3 * 2) = sVar7;
            uVar3 = uVar3 + 1;
            for (uVar9 = 0; uVar9 < (uVar5 & 0xff); uVar9 = uVar9 + 1) {
              uVar2 = FT_Stream_GetChar(param_1);
              sVar7 = sVar7 + (uVar2 & 0xff);
              *(short *)(iVar4 + uVar3 * 2) = sVar7;
              uVar3 = uVar3 + 1;
              if (uVar6 <= uVar3) break;
            }
          }
          goto LAB_005f12f2;
        }
      }
      else {
        iVar4 = 0;
      }
    }
  }
  return iVar4;
}

