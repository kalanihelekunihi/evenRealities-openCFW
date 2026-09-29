
undefined4 gx8002_uart_stage1_announce(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  uint *puVar4;
  int iVar5;
  
  piVar1 = piRam100006d4;
  iVar5 = *piRam100006d4;
  *(undefined4 *)(iVar5 + 0xa8) = 1;
  uVar3 = 6;
  if (iVar5 != 0) {
    uVar3 = 4;
  }
  func_0x10001bf8(param_1,iVar5,param_2,uVar3);
  puVar2 = (undefined4 *)*piVar1;
  puVar4 = puVar2 + 5;
  do {
  } while ((*puVar4 & 0x40) == 0);
  *puVar2 = 0x72;
  do {
  } while ((*puVar4 & 0x40) == 0);
  *puVar2 = 0x65;
  do {
  } while ((*puVar4 & 0x40) == 0);
  *puVar2 = 0x61;
  do {
  } while ((*puVar4 & 0x40) == 0);
  *puVar2 = 100;
  do {
  } while ((*puVar4 & 0x40) == 0);
  *puVar2 = 0x79;
  gx8002_uart_stage1_postamble();
  return 0;
}

