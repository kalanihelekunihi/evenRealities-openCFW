
undefined8 cff_ps_get_font_extra(int param_1,undefined2 *param_2)

{
  ushort *puVar1;
  int iVar2;
  byte *pbVar3;
  byte *pbVar4;
  int iVar5;
  int iStack_18;
  
  iVar5 = *(int *)(param_1 + 0x2a4);
  iStack_18 = 0;
  if ((iVar5 != 0) && (*(int *)(iVar5 + 0xc3c) == 0)) {
    puVar1 = (ushort *)ft_mem_alloc(*(undefined4 *)(param_1 + 100),2,&iStack_18);
    if (iStack_18 != 0) goto LAB_005ac3ca;
    *puVar1 = 0;
    iVar2 = cff_index_get_sid_string(iVar5,*(undefined4 *)(iVar5 + 0x5dc));
    if (((iVar2 != 0) && (iVar2 = FUN_0044b63a(iVar2,DAT_005ace0c), iVar2 != 0)) &&
       (pbVar3 = (byte *)FUN_0044b63a(iVar2 + 7,&DAT_005ac5e8), pbVar3 != (byte *)0x0)) {
      for (pbVar4 = (byte *)(iVar2 + 7); pbVar4 != pbVar3; pbVar4 = pbVar4 + 1) {
        if (*pbVar4 - 0x30 < 10) {
          if (0x1997 < *puVar1) {
            *puVar1 = 0;
            break;
          }
          *puVar1 = *puVar1 * 10;
          *puVar1 = (*puVar1 + (ushort)*pbVar4) - 0x30;
        }
        else if (((*pbVar4 != 0x20) && (*pbVar4 != 10)) && (*pbVar4 != 0xd)) {
          *puVar1 = 0;
          break;
        }
      }
    }
    *(ushort **)(iVar5 + 0xc3c) = puVar1;
  }
  if (iVar5 != 0) {
    *param_2 = **(undefined2 **)(iVar5 + 0xc3c);
  }
LAB_005ac3ca:
  return CONCAT44(iStack_18,iStack_18);
}

