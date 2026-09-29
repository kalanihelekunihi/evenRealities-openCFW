
void SmpScFreeScratchBuffers(int param_1)

{
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x14) != 0) {
    WsfBufFree(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14) = 0;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 8) != 0) {
    WsfBufFree(*(undefined4 *)(*(int *)(param_1 + 0x48) + 8));
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 8) = 0;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x18) != 0) {
    WsfBufFree(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x18));
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x18) = 0;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0xc) != 0) {
    WsfBufFree(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc));
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc) = 0;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x10) != 0) {
    WsfBufFree(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x10));
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x10) = 0;
  }
  return;
}

