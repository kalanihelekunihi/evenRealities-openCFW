
undefined4 gx8002_uart_initialize(uint param_1,undefined4 param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  
  if (1 < param_1) {
    return 0xffffffff;
  }
  func_0x10025080((param_1 != 0) + '\x11',1);
  uVar1 = func_0x10025210(0x10);
  uVar3 = uVar1 % 1000000;
  if (100 < uVar3) {
    if (100 < (int)(1000000 - uVar3)) goto LAB_10203566;
    uVar1 = uVar1 + 1000000;
  }
  uVar1 = uVar1 - uVar3;
LAB_10203566:
  iVar4 = param_1 * 0x80 + DAT_10203594;
  *(uint *)(iVar4 + 0xc) = uVar1;
  *(undefined4 *)(iVar4 + 0x10) = param_2;
  uVar2 = gx8002_uart_configure(iVar4);
  return uVar2;
}

