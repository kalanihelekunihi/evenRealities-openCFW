
undefined4 FUN_10004238(int param_1)

{
  if (-1 < *(int *)(param_1 + 0x68)) {
    gx8002_backup_dma_abort();
    *(undefined4 *)(param_1 + 0x68) = 0xffffffff;
  }
  return 0;
}

