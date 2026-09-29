
int FUN_0056f178(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if ((param_2 == 0) || (param_1 == 0)) {
    iVar1 = 0;
  }
  else {
    uVar4 = *(int *)(param_2 + 0x20) +
            *(int *)(param_2 + 0x18) * 0xe10 + *(int *)(param_2 + 0x1c) * 0x3c;
    uVar3 = *(int *)(param_1 + 0x20) +
            *(int *)(param_1 + 0x18) * 0xe10 + *(int *)(param_1 + 0x1c) * 0x3c;
    if (uVar3 < uVar4) {
      uVar3 = DAT_0056f924 + uVar3;
    }
    iVar1 = uVar3 - uVar4;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbe0,0x140,DAT_0056f928,iVar1,
                   *(undefined4 *)(param_2 + 0x18),*(undefined4 *)(param_2 + 0x1c),
                   *(undefined4 *)(param_2 + 0x20),*(undefined4 *)(param_1 + 0x18),
                   *(undefined4 *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x20),param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x9c00000,DAT_0056fd90,DAT_0056fd90,iVar1,*(undefined4 *)(param_2 + 0x18),
                          *(undefined4 *)(param_2 + 0x1c),*(undefined4 *)(param_2 + 0x20),
                          *(undefined4 *)(param_1 + 0x18),*(undefined4 *)(param_1 + 0x1c),
                          *(undefined4 *)(param_1 + 0x20));
    }
  }
  return iVar1;
}

