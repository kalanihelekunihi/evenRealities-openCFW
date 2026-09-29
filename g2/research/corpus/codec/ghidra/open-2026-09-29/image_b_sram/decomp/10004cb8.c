
void gx8002_dma_callback(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = DAT_10004cc8;
  *(undefined4 *)(DAT_10004cc8 + param_1 * 4) = param_2;
  *(undefined4 *)(iVar1 + param_1 * 4 + 8) = param_3;
  return;
}

