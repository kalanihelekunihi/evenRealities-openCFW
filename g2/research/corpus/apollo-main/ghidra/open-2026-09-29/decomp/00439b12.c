
void FUN_00439b12(int param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = 0x20 - *(uint *)(param_1 + 0x20);
  if ((int)param_3 < (int)uVar1) {
    uVar1 = param_3;
  }
  if (uVar1 != 0) {
    *(uint *)(param_1 + 0x1c) =
         param_2 << (*(uint *)(param_1 + 0x20) & 0xff) | *(uint *)(param_1 + 0x1c);
    *(undefined4 *)(param_1 + 0x20) = 0x20;
  }
  FUN_0043992c(param_1 + 0x1c,param_1 + 0x28);
  *(uint *)(param_1 + 0x1c) = param_2 >> (uVar1 & 0xff);
  *(uint *)(param_1 + 0x20) = param_3 - uVar1;
  return;
}

