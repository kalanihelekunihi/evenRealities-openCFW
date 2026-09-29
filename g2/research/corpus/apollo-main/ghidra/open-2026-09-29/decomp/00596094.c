
void FUN_00596094(int param_1)

{
  if (*(int *)(param_1 + 4) != 0) {
    file_heap_free(*(undefined4 *)(param_1 + 4));
    *(undefined4 *)(param_1 + 4) = 0;
    *(undefined2 *)(param_1 + 0xc) = 0;
  }
  if (*(int *)(param_1 + 8) != 0) {
    file_heap_free(*(undefined4 *)(param_1 + 8));
    *(undefined4 *)(param_1 + 8) = 0;
    *(undefined2 *)(param_1 + 0xe) = 0;
  }
  return;
}

