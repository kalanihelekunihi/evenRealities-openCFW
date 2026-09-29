
undefined4 gx8002_dma_abort(uint param_1)

{
  *(int *)(*DAT_10203b60 + 0x3a0) = 0x100 << (param_1 & 0x3f);
  gx8002_dma_clear();
  gx8002_dma_deallocate(param_1);
  return 0;
}

