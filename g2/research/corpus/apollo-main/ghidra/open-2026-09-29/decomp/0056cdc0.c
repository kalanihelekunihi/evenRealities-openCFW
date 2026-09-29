
undefined4 SmpScAllocScratchBuffers(int param_1)

{
  undefined4 uVar1;
  
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x14) == 0) {
    uVar1 = WsfBufAlloc(0x60);
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14) = uVar1;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 8) == 0) {
    uVar1 = WsfBufAlloc(0x40);
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 8) = uVar1;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x18) == 0) {
    uVar1 = WsfBufAlloc(0x20);
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x18) = uVar1;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0xc) == 0) {
    uVar1 = WsfBufAlloc(0x40);
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc) = uVar1;
  }
  if (*(int *)(*(int *)(param_1 + 0x48) + 0x10) == 0) {
    uVar1 = WsfBufAlloc(0x20);
    *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x10) = uVar1;
  }
  if ((((*(int *)(*(int *)(param_1 + 0x48) + 0x14) == 0) ||
       (*(int *)(*(int *)(param_1 + 0x48) + 8) == 0)) ||
      (*(int *)(*(int *)(param_1 + 0x48) + 0x18) == 0)) ||
     ((*(int *)(*(int *)(param_1 + 0x48) + 0xc) == 0 ||
      (*(int *)(*(int *)(param_1 + 0x48) + 0x10) == 0)))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

