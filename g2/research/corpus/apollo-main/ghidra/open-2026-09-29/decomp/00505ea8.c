
undefined4 FUN_00505ea8(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  
  for (iVar2 = 0; uVar1 = (undefined2)DAT_00505ed8, iVar2 < 3; iVar2 = iVar2 + 1) {
    *(undefined2 *)(param_1 + 0x18 + iVar2 * 2 + 6) = uVar1;
    *(undefined2 *)(param_1 + 0x18 + iVar2 * 2 + 0xc) = uVar1;
  }
  *(undefined2 *)(param_1 + 0x2a) = uVar1;
  *(undefined1 *)(param_1 + 0x2c) = 0;
  *(undefined1 *)(param_1 + 0x2d) = 0;
  *(undefined1 *)(param_1 + 0x2e) = 0;
  return 0;
}

