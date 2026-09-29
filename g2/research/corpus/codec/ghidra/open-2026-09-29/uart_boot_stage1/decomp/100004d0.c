
void gx8002_uart_stage1_beacon(int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint *puVar6;
  uint *puVar7;
  uint *puVar8;
  
  puVar1 = puRam10000580;
  puVar8 = (uint *)*puRam10000580;
  puVar8[1] = 0;
  puVar8[4] = 3;
  if (param_2 == 0) {
    if (puVar8 == (uint *)0x0) {
      uVar2 = func_0x10000ea0(0x11);
    }
    else {
      uVar2 = func_0x10000ea0(0x12);
    }
    param_1 = param_1 << 4;
    uVar3 = gx8002_uart_stage1_udiv(uVar2,param_1);
    iVar4 = gx8002_uart_stage1_umod(uVar2,param_1);
    iVar4 = gx8002_uart_stage1_udiv(iVar4 * 100,param_1);
    uVar5 = gx8002_uart_stage1_udiv(iVar4 << 4,100);
    puVar8 = (uint *)*puVar1;
    puVar7 = puVar8 + 0x1f;
    do {
    } while ((*puVar7 & 1) != 0);
    puVar8[3] = 0x80;
    *puVar8 = uVar3 & 0xff;
    puVar6 = puVar8 + 3;
    puVar8[1] = (uVar3 & 0x7fff) >> 8;
    puVar8[0x30] = uVar5 & 0xff;
  }
  else {
    puVar7 = puVar8 + 0x1f;
    puVar6 = puVar8 + 3;
  }
  do {
  } while ((*puVar7 & 1) != 0);
  *puVar6 = 3;
  puVar8[2] = 0x4f;
  return;
}

