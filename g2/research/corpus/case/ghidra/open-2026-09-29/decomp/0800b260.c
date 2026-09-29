
void FUN_0800b260(void)

{
  if (**(int **)(DAT_0800b280 + 0x34) != 0) {
    *(undefined4 *)(DAT_0800b280 + 0x28) =
         *(undefined4 *)(*(int *)(*(int *)(*(int *)(DAT_0800b280 + 0x34) + 0xc) + 0xc) + 4);
    return;
  }
  *(undefined4 *)(DAT_0800b280 + 0x28) = 0xffffffff;
  return;
}

