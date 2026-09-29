
undefined4 FUN_004d3a58(int param_1)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 0x24) < 100) {
    if (*(uint *)(param_1 + 0x20) < 0x3c) {
      if (*(uint *)(param_1 + 0x1c) < 0x3c) {
        if (*(uint *)(param_1 + 0x18) < 0x18) {
          if ((*(int *)(param_1 + 0x14) == 0) || (0x1f < *(uint *)(param_1 + 0x14))) {
            uVar1 = 0;
          }
          else if ((*(int *)(param_1 + 0x10) == 0) || (0xc < *(uint *)(param_1 + 0x10))) {
            uVar1 = 0;
          }
          else if (*(uint *)(param_1 + 0xc) < 0x65) {
            if (*(uint *)(param_1 + 4) < 7) {
              uVar1 = 1;
            }
            else {
              uVar1 = 0;
            }
          }
          else {
            uVar1 = 0;
          }
        }
        else {
          uVar1 = 0;
        }
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

