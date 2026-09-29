
int FUN_005dff5a(int param_1,int param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int local_20;
  undefined4 uStack_1c;
  
  uVar6 = *(undefined4 *)(param_2 + 0x1c);
  local_20 = param_3;
  uStack_1c = param_4;
  iVar2 = FT_Stream_ReadUShort(param_2,&local_20,param_3,param_4,param_1,param_2);
  if (local_20 == 0) {
    if (((int)(uint)*(ushort *)(param_1 + 0x108) < iVar2) || (0x101 < iVar2 - 1U)) {
      local_20 = 3;
    }
    else {
      iVar3 = ft_mem_realloc(uVar6,1,0,iVar2,0,&local_20);
      if ((local_20 == 0) && (local_20 = FT_Stream_Read(param_2,iVar3,iVar2), local_20 == 0)) {
        bVar1 = false;
      }
      else {
        bVar1 = true;
      }
      if (bVar1) {
LAB_005dffc8:
        ft_mem_free(uVar6,iVar3);
      }
      else {
        for (iVar4 = 0; iVar4 < iVar2; iVar4 = iVar4 + 1) {
          iVar5 = iVar4 + *(char *)(iVar3 + iVar4);
          if ((iVar5 < 0) || (iVar2 < iVar5)) {
            local_20 = 3;
            goto LAB_005dffc8;
          }
        }
        *(short *)(param_1 + 0x27c) = (short)iVar2;
        *(int *)(param_1 + 0x280) = iVar3;
        local_20 = 0;
      }
    }
  }
  return local_20;
}

