
int ft_var_readpackeddeltas(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  byte bVar1;
  undefined2 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  int local_28;
  undefined4 uStack_24;
  
  uVar5 = *(undefined4 *)(param_1 + 0x1c);
  local_28 = 0;
  if ((param_3 <= param_2) &&
     (uStack_24 = param_4, iVar3 = ft_mem_realloc(uVar5,2,0,param_3,0,&local_28), local_28 == 0)) {
    uVar6 = 0;
    do {
      if (param_3 <= uVar6) {
        return iVar3;
      }
      bVar1 = FT_Stream_GetChar(param_1);
      uVar4 = (uint)bVar1;
      uVar7 = uVar4 & 0x3f;
      if ((int)(uVar4 << 0x18) < 0) {
        uVar4 = 0;
        for (; (uVar4 <= uVar7 && (uVar6 < param_3)); uVar6 = uVar6 + 1) {
          *(undefined2 *)(iVar3 + uVar6 * 2) = 0;
          uVar4 = uVar4 + 1;
        }
      }
      else if ((int)(uVar4 << 0x19) < 0) {
        uVar4 = 0;
        for (; (uVar4 <= uVar7 && (uVar6 < param_3)); uVar6 = uVar6 + 1) {
          uVar2 = FT_Stream_GetUShort(param_1);
          *(undefined2 *)(iVar3 + uVar6 * 2) = uVar2;
          uVar4 = uVar4 + 1;
        }
      }
      else {
        uVar4 = 0;
        for (; (uVar4 <= uVar7 && (uVar6 < param_3)); uVar6 = uVar6 + 1) {
          uVar2 = FT_Stream_GetChar(param_1);
          *(undefined2 *)(iVar3 + uVar6 * 2) = uVar2;
          uVar4 = uVar4 + 1;
        }
      }
    } while (uVar7 < uVar4);
    ft_mem_free(uVar5,iVar3);
  }
  return 0;
}

