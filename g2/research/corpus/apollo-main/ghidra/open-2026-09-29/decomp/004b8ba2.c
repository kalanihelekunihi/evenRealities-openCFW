
void tpl_context_free_004b8ba2(int param_1)

{
  if ((param_1 != 0) && (*(char *)(param_1 + 0x30) != '\0')) {
    fw_event_loop_remove_delayed(0x4b8c6d);
    if (*(int *)(param_1 + 8) != 0) {
      file_heap_free(*(undefined4 *)(param_1 + 8));
      *(undefined4 *)(param_1 + 8) = 0;
    }
    *(undefined1 *)(param_1 + 0x30) = 0;
    FUN_0043c0e4(param_1,0x32,0);
  }
  return;
}

