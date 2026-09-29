
void gx8002_flash_block_range(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_14 [4];
  
  iVar1 = gx8002_flash_block_bounds(param_1,param_3,auStack_14);
  if (iVar1 == 0) {
    gx8002_flash_block_bounds(param_2 + -1 + param_1,auStack_14,param_4);
  }
  return;
}

