
void text_stream_destroy(int *param_1)

{
  if (param_1 != (int *)0x0) {
    text_stream_stop_and_delete_animation(param_1);
    if (param_1[8] != 0) {
      osMutexDelete(param_1[8]);
    }
    if (*param_1 != 0) {
      file_heap_free(*param_1);
    }
    if (param_1[1] != 0) {
      file_heap_free(param_1[1]);
    }
    file_heap_free(param_1);
  }
  return;
}

