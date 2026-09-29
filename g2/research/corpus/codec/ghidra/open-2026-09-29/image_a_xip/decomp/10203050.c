
undefined4 dw_uart_get_dma_burst_size(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x34);
  if (param_2 == 0) {
    iVar1 = *(int *)(param_1 + 0x38);
  }
  if (iVar1 == 0x40) {
    return 5;
  }
  if (iVar1 < 0x41) {
    if (iVar1 == 8) {
      return 2;
    }
    if (iVar1 < 9) {
      if (iVar1 == 4) {
        return 1;
      }
    }
    else {
      if (iVar1 == 0x10) {
        return 3;
      }
      if (iVar1 == 0x20) {
        return 4;
      }
    }
  }
  else {
    if (iVar1 == 0x100) {
      return 7;
    }
    if (iVar1 < 0x101) {
      if (iVar1 == 0x80) {
        return 6;
      }
    }
    else {
      if (iVar1 == 0x200) {
        return 8;
      }
      if (iVar1 == 0x400) {
        return 9;
      }
    }
  }
  return 0;
}

