
void semantic_gx8002_free_message(int param_1)

{
  if ((param_1 != 0) && (*(int *)(param_1 + 0xe) != 0)) {
    file_heap_free(*(undefined4 *)(param_1 + 0xe));
    *(undefined4 *)(param_1 + 0xe) = 0;
    *(undefined2 *)(param_1 + 0x12) = 0;
  }
  return;
}

