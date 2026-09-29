
void aout_i2s_config(int param_1,int param_2)

{
  *(uint *)(param_1 + 4) =
       (*(uint *)(param_2 + 0x18) & 1) << 0x10 | *(uint *)(param_1 + 4) & 0xfffeffff;
  *(uint *)(param_1 + 4) = *(uint *)(param_1 + 4) & 0xffff7fff;
  *(uint *)(param_1 + 4) =
       (*(uint *)(param_2 + 0x20) & 1) << 0xe | *(uint *)(param_1 + 4) & 0xffffbfff;
  *(uint *)(param_1 + 4) = (*(uint *)(param_2 + 4) & 1) << 9 | *(uint *)(param_1 + 4) & 0xfffffdff;
  *(uint *)(param_1 + 4) = (*(uint *)(param_2 + 8) & 7) << 4 | *(uint *)(param_1 + 4) & 0xffffff8f;
  *(uint *)(param_1 + 4) = (*(uint *)(param_2 + 0xc) & 3) << 2 | *(uint *)(param_1 + 4) & 0xfffffff3
  ;
  *(uint *)(param_1 + 4) = *(uint *)(param_2 + 0x10) & 3 | *(uint *)(param_1 + 4) & 0xfffffffc;
  *(uint *)(param_1 + 0x10) =
       *(int *)(param_2 + 0x24) << 0x1f | *(uint *)(param_1 + 0x10) & 0x3fffffff;
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) & 0xff000000 | 0x400;
  return;
}

