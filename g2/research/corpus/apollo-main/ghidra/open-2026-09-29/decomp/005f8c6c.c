
undefined8 tt_size_init_bytecode(int *param_1,uint param_2,undefined4 param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  short sVar5;
  undefined4 uVar6;
  int local_20;
  
  iVar3 = *param_1;
  uVar4 = *(undefined4 *)(iVar3 + 100);
  local_20 = param_4;
  ft_mem_free(uVar4,param_1[0x21],param_3,param_4,param_2,param_3);
  param_1[0x21] = 0;
  ft_mem_free(uVar4,param_1[0x24]);
  param_1[0x24] = 0;
  ft_mem_free(uVar4,param_1[0x3f]);
  param_1[0x3f] = 0;
  ft_mem_free(uVar4,param_1[0x41]);
  param_1[0x41] = 0;
  if (param_1[0x4b] != 0) {
    TT_Done_Context(param_1[0x4b]);
  }
  tt_glyphzone_done(param_1 + 0x42);
  param_1[0x4c] = -1;
  param_1[0x4d] = -1;
  iVar2 = TT_New_Context(*(undefined4 *)(iVar3 + 0x60));
  param_1[0x4b] = iVar2;
  param_1[0x20] = (uint)*(ushort *)(iVar3 + 0x118);
  param_1[0x23] = (uint)*(ushort *)(iVar3 + 0x11a);
  param_1[0x1f] = 0;
  param_1[0x22] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x3e] = *(int *)(iVar3 + 0x298);
  *(undefined2 *)(param_1 + 0x40) = *(undefined2 *)(iVar3 + 0x116);
  *(undefined1 *)((int)param_1 + 0x71) = 0;
  *(undefined1 *)((int)param_1 + 0x72) = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  uVar6 = 0;
  iVar2 = ft_mem_realloc(uVar4,0x18,0,param_1[0x20],0,&local_20);
  param_1[0x21] = iVar2;
  if (local_20 == 0) {
    uVar6 = 0;
    iVar2 = ft_mem_realloc(uVar4,0x18,0,param_1[0x23],0,&local_20);
    param_1[0x24] = iVar2;
    if (local_20 != 0) goto LAB_005f8dc4;
    uVar6 = 0;
    iVar2 = ft_mem_realloc(uVar4,4,0,param_1[0x3e],0,&local_20);
    param_1[0x3f] = iVar2;
    if (local_20 != 0) goto LAB_005f8dc4;
    uVar6 = 0;
    iVar2 = ft_mem_realloc(uVar4,4,0,(short)param_1[0x40],0,&local_20);
    param_1[0x41] = iVar2;
    if (local_20 != 0) goto LAB_005f8dc4;
    bVar1 = false;
  }
  else {
LAB_005f8dc4:
    bVar1 = true;
  }
  if (!bVar1) {
    sVar5 = *(short *)(iVar3 + 0x114) + 4;
    local_20 = tt_glyphzone_new(uVar4,sVar5,0,param_1 + 0x42);
    if (local_20 == 0) {
      *(short *)(param_1 + 0x44) = sVar5;
      FUN_00439c04(param_1 + 0x2d,DAT_005f9500,0x44);
      *(undefined4 *)(iVar3 + 0x2a0) = *(undefined4 *)(*(int *)(*(int *)(iVar3 + 0x60) + 4) + 0xa4);
      if (*(int *)(iVar3 + 0x2a0) == 0) {
        *(undefined4 *)(iVar3 + 0x2a0) = DAT_005f9504;
      }
      local_20 = tt_size_run_fpgm(param_1,param_2 & 0xff);
      goto LAB_005f8dde;
    }
  }
  if (local_20 != 0) {
    tt_size_done_bytecode(param_1);
  }
LAB_005f8dde:
  return CONCAT44(uVar6,local_20);
}

