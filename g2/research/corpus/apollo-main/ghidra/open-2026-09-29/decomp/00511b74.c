
void FUN_00511b74(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 << 0x1e < 0) {
    uVar1 = 5;
  }
  else if (param_1 << 0x1d < 0) {
    uVar1 = 1;
  }
  else if (param_1 << 0x1c < 0) {
    uVar1 = 2;
  }
  else if (param_1 << 0x1b < 0) {
    uVar1 = 4;
  }
  else {
    uVar1 = 0;
  }
  *DAT_00512608 = uVar1;
  FUN_0055f74c(2,&stack0xfffffff8);
  return;
}

