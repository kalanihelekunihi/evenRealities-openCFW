
undefined4 dw_uart_get_fifo_depth(int param_1)

{
  uint uVar1;
  
  uVar1 = (*(uint *)(*(int *)(param_1 + 4) + 0xf4) & 0x7fffff) >> 0x10;
  if (uVar1 == 8) {
    return 0x80;
  }
  if (uVar1 < 9) {
    if (uVar1 == 2) {
      return 0x20;
    }
    if (uVar1 == 4) {
      return 0x40;
    }
    if (uVar1 == 1) {
      return 0x10;
    }
  }
  else {
    if (uVar1 == 0x20) {
      return 0x200;
    }
    if (uVar1 < 0x21) {
      if (uVar1 == 0x10) {
        return 0x100;
      }
    }
    else {
      if (uVar1 == 0x40) {
        return 0x400;
      }
      if (uVar1 == 0x80) {
        return 0x800;
      }
    }
  }
  return 0;
}

