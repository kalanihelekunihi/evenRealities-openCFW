
void FUN_005dc266(int param_1)

{
  if (*(char *)(param_1 + 0x32c) != '\0') {
    if (*(int *)(param_1 + 0x318) != 0) {
      FT_Stream_ReleaseFrame(*(undefined4 *)(param_1 + 0x68),(int *)(param_1 + 0x318));
    }
    *(undefined4 *)(param_1 + 0x31c) = 0;
    *(undefined4 *)(param_1 + 800) = 0;
    *(undefined4 *)(param_1 + 0x324) = 0;
  }
  return;
}

