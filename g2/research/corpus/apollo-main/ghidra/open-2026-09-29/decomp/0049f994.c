
void ring_master_scan_start(int param_1)

{
  if (*(char *)(param_1 + 3) == '\0') {
    *(undefined1 *)(*DAT_004a0518 + 0x58) = 2;
    *(undefined1 *)(*DAT_004a05e8 + 0x16) = 0x80;
  }
  return;
}

