
undefined4 gx8002_backup_dma_abort(uint param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = *DAT_10004cb4;
  iVar2 = 1 << (param_1 & 0x3f);
  *(int *)(iVar1 + 0x3a0) = 0x100 << (param_1 & 0x3f);
  *(int *)(iVar1 + 0x338) = iVar2;
  *(int *)(iVar1 + 0x340) = iVar2;
  *(int *)(iVar1 + 0x348) = iVar2;
  *(int *)(iVar1 + 0x350) = iVar2;
  *(int *)(iVar1 + 0x358) = iVar2;
  gx8002_backup_dma_pair();
  return 0;
}

