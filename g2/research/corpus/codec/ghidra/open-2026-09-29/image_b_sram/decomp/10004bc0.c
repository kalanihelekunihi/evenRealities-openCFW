
void gx8002_backup_dma_pair(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = gx8002_irq_save();
  iVar1 = DAT_10004c00;
  *(undefined1 *)(param_1 + DAT_10004c00 + 0x370) = 0;
  if ((*(uint *)(iVar1 + 4) == 0) ||
     ((*(char *)(iVar1 + 0x370) != '\x01' &&
      ((*(uint *)(iVar1 + 4) < 2 || (*(char *)(iVar1 + 0x371) != '\x01')))))) {
    gx8002_platform_gate(0x19,0);
  }
  gx8002_irq_restore(uVar2);
  return;
}

