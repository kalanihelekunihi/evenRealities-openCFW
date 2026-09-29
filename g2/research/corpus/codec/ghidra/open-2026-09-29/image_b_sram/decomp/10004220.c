
undefined4 FUN_10004220(int param_1)

{
  if (-1 < *(int *)(param_1 + 0x7c)) {
    gx8002_backup_dma_abort();
    *(undefined4 *)(param_1 + 0x7c) = 0xffffffff;
  }
  return 0;
}

