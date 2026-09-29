
void mspi_seq_loopback(int param_1)

{
  *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x830) + 1;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined1 *)(param_1 + 0x834) = 1;
  *(undefined4 *)(DAT_004251a4 + *(int *)(param_1 + 4) * 0x1000 + 0x2b4) = 0x40;
  return;
}

