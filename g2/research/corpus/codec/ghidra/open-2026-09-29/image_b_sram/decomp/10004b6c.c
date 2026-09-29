
int gx8002_backup_dma_select(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = gx8002_irq_save();
  if ((*(uint *)(DAT_10004bbc + 4) != 0) &&
     ((iVar2 = 0, *(char *)(DAT_10004bbc + 0x370) == '\0' ||
      ((iVar2 = 1, 1 < *(uint *)(DAT_10004bbc + 4) && (*(char *)(DAT_10004bbc + 0x371) == '\0'))))))
  {
    *(undefined1 *)(DAT_10004bbc + iVar2 + 0x370) = 1;
    gx8002_platform_gate(0x19,1);
    gx8002_irq_restore(uVar1);
    return iVar2;
  }
  gx8002_irq_restore(uVar1);
  return -1;
}

