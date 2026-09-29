
longlong FUN_00597e1c(void)

{
  char *pcVar1;
  uint in_r3;
  uint uVar2;
  
  pcVar1 = DAT_00597e84;
  if (*DAT_00597e84 == '\0') {
    for (uVar2 = 0; uVar2 < *DAT_00597e8c; uVar2 = uVar2 + 1) {
      if (*(int *)(*(int *)(DAT_00597e88 + uVar2 * 4) + 0x24) != 0) {
        (**(code **)(*(int *)(DAT_00597e88 + uVar2 * 4) + 0x24))();
      }
    }
    *pcVar1 = '\x01';
  }
  return (ulonglong)in_r3 << 0x20;
}

