
void gx8002_uart_stage1_umod(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  if ((param_2 < param_1) && (-1 < (int)param_2)) {
    iVar1 = 0x20;
    uVar2 = 1;
    do {
      param_2 = param_2 * 2;
      uVar2 = uVar2 * 2;
      if (param_1 <= param_2) {
        if (uVar2 == 0) {
          return;
        }
        break;
      }
      iVar1 = iVar1 + -1;
      if (iVar1 == 0) {
        return;
      }
    } while (-1 < (int)param_2);
  }
  else {
    uVar2 = 0;
  }
  do {
    uVar2 = uVar2 >> 1;
    if (param_2 <= param_1) {
      param_1 = param_1 - param_2;
    }
    param_2 = param_2 >> 1;
  } while (uVar2 != 0);
  return;
}

