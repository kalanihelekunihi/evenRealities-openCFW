
undefined8 FUN_005da518(undefined4 param_1,int param_2,int param_3,code *param_4,char param_5)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  char *pcVar4;
  char *pcVar5;
  int local_28;
  code *pcStack_24;
  
  local_28 = 0;
  pcStack_24 = param_4;
  pcVar1 = (char *)ft_mem_alloc(param_1,*(ushort *)(param_3 + 8) + 1,&local_28);
  if (local_28 == 0) {
    local_28 = FT_Stream_Seek(param_2,*(undefined4 *)(param_3 + 0xc));
    if (local_28 == 0) {
      local_28 = FT_Stream_EnterFrame(param_2,*(undefined2 *)(param_3 + 8));
      if (local_28 == 0) {
        pcVar5 = *(char **)(param_2 + 0x20);
        pcVar4 = pcVar1;
        for (uVar3 = (uint)*(ushort *)(param_3 + 8); uVar3 != 0; uVar3 = uVar3 - 1) {
          iVar2 = (*param_4)((int)*pcVar5);
          if (iVar2 == 0) {
            if (param_5 != '\0') {
              *pcVar4 = *pcVar5;
              pcVar4 = pcVar4 + 1;
            }
          }
          else {
            *pcVar4 = *pcVar5;
            pcVar4 = pcVar4 + 1;
          }
          pcVar5 = pcVar5 + 1;
        }
        *pcVar4 = '\0';
        FT_Stream_ExitFrame(param_2);
        goto LAB_005da5d2;
      }
    }
    ft_mem_free(param_1,pcVar1);
    *(undefined4 *)(param_3 + 0xc) = 0;
    *(undefined2 *)(param_3 + 8) = 0;
    ft_mem_free(param_1,*(undefined4 *)(param_3 + 0x10));
    *(undefined4 *)(param_3 + 0x10) = 0;
    pcVar1 = (char *)0x0;
  }
  else {
    pcVar1 = (char *)0x0;
  }
LAB_005da5d2:
  return CONCAT44(local_28,pcVar1);
}

