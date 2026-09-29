
undefined4 gx8002_uart_stage1_uart_config(int *param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = iRam10000d90;
  if (*param_1 != 0) {
    *(uint *)(iRam10000d90 + 0x3c) = *(uint *)(iRam10000d90 + 0x3c) & 0xfffffffd;
    *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) & 0xfffffffe;
    if (*param_1 != 0) {
      *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) & 0xffffffc0;
      *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) | param_1[4];
      *(uint *)(iVar1 + 0x20) = *(uint *)(iVar1 + 0x20) & 0xffffff00;
      *(uint *)(iVar1 + 0x24) = *(uint *)(iVar1 + 0x24) & 0xffffffe0;
      *(uint *)(iVar1 + 0x20) = (uint)*(byte *)(param_1 + 5) | *(uint *)(iVar1 + 0x20);
      *(uint *)(iVar1 + 0x24) = (param_1[5] & 0xfffU) >> 8 | *(uint *)(iVar1 + 0x24);
      *(uint *)(iVar1 + 0x28) = *(uint *)(iVar1 + 0x28) & 0xfffffff8;
      *(uint *)(iVar1 + 0x28) = *(uint *)(iVar1 + 0x28) | param_1[9];
      *(uint *)(iVar1 + 0x2c) = *(uint *)(iVar1 + 0x2c) & 0xffffff80;
      *(uint *)(iVar1 + 0x2c) = *(uint *)(iVar1 + 0x2c) | param_1[6];
      *(uint *)(iVar1 + 0x30) = *(uint *)(iVar1 + 0x30) & 0xfffffff8;
      *(uint *)(iVar1 + 0x30) = param_1[0xb] & 7U | *(uint *)(iVar1 + 0x30);
      *(uint *)(iVar1 + 0x30) = *(uint *)(iVar1 + 0x30) & 0xffffffcf;
      *(uint *)(iVar1 + 0x30) = param_1[8] << 4 | *(uint *)(iVar1 + 0x30);
      *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) & 0xfffffffb;
      *(uint *)(iVar1 + 0x3c) = (param_1[7] & 1U) << 2 | *(uint *)(iVar1 + 0x3c);
      *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) | 2;
      *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) | 1;
    }
    gx8002_uart_stage1_railcfg();
    iVar2 = func_0x100003bc();
    iVar1 = iRam10000d94;
    while ((*(uint *)(iVar1 + 0x18) & 8) == 0) {
      iVar3 = func_0x100003bc();
      if (param_2 < (uint)(iVar3 - iVar2)) {
        return 0xffffffff;
      }
    }
  }
  return 0;
}

