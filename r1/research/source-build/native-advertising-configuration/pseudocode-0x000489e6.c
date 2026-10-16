/* ================================================================
 * entry: 0x000489e6
 * end:   0x00048a25
 * size:  64 bytes
 * name:  FUN_000489e6
 * ================================================================ */

void FUN_000489e6(int param_1)

{
  int iVar1;
  undefined4 uVar2;

  FUN_000277aa(param_1,0x2c);
  *(undefined1 *)(param_1 + 4) = 1;
  *(undefined4 *)(param_1 + 0x10) = 0xa0;
  iVar1 = FUN_0007ba24();
  if (iVar1 == 0x55) {
    uVar2 = 0;
  }
  else {
    uVar2 = 6000;
  }
  *(undefined4 *)(param_1 + 0x14) = uVar2;
  iVar1 = FUN_0007ba24();
  *(bool *)(param_1 + 5) = iVar1 != 0x55;
  *(undefined4 *)(param_1 + 0x18) = 0x640;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  return;
}



