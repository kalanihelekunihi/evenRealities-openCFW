
void mspi_get_xip_off_min_delay(int param_1)

{
  uint uVar1;
  
  uVar1 = (uint)*(byte *)(param_1 + 0xc);
  if (uVar1 - 6 < 4) {
    *(undefined4 *)(param_1 + 0x8cc) = 8;
  }
  else if (uVar1 - 10 < 4) {
    *(undefined4 *)(param_1 + 0x8cc) = 4;
  }
  else if ((uVar1 - 0xe < 2) || (uVar1 - 0x12 < 2)) {
    *(undefined4 *)(param_1 + 0x8cc) = 2;
  }
  else if (uVar1 - 0x14 < 4) {
    *(undefined4 *)(param_1 + 0x8cc) = 1;
  }
  return;
}

