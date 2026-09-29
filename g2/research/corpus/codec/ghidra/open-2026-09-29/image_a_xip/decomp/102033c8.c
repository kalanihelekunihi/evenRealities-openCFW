
undefined4 gx8002_uart_configure(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  
  if (*(int *)(param_1 + 0x1c) == 0) {
    *(undefined4 *)(param_1 + 0x1c) = 8;
  }
  if (*(int *)(param_1 + 0x20) == 0) {
    *(undefined4 *)(param_1 + 0x20) = 1;
  }
  puVar7 = *(uint **)(param_1 + 4);
  puVar7[1] = 0;
  uVar5 = 0x22;
  if (*(int *)(param_1 + 0x24) == 0) {
    uVar5 = 3;
  }
  puVar7[4] = uVar5;
  uVar9 = 0x7f;
  uVar5 = 0x6f;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar5 = 0x7f;
  }
  puVar7[2] = uVar5;
  if (*(int *)(param_1 + 0x10) != 0) {
    uVar5 = *(int *)(param_1 + 0x10) * 0x10;
    uVar8 = *(uint *)(param_1 + 0xc) / uVar5;
    *(uint *)(param_1 + 0x14) = uVar8;
    uVar1 = gx8002_floatunsidf(*(uint *)(param_1 + 0xc) - uVar8 * uVar5);
    uVar3 = param_2;
    uVar2 = gx8002_floatunsidf(uVar5);
    gx8002_divdf3_fixed(uVar1,param_2,uVar2,uVar3);
    gx8002_muldf3_fixed();
    gx8002_adddf3();
    uVar3 = gx8002_fixunsdfsi();
    *(undefined4 *)(param_1 + 0x18) = uVar3;
    puVar7[2] = 0;
    uVar5 = puVar7[3];
    puVar7[3] = uVar5 | 0x80;
    *puVar7 = uVar8 & 0xff;
    puVar7[1] = (uVar8 & 0x7fff) >> 8;
    puVar7[0x30] = (uint)*(byte *)(param_1 + 0x18);
    puVar7[3] = uVar5;
    if (*(int *)(param_1 + 0x24) == 0) {
      uVar9 = 0x6f;
    }
    puVar7[2] = uVar9;
  }
  puVar7[2] = 0;
  puVar7[3] = puVar7[3] & 0xffffffe0 | 3;
  uVar5 = 0x7f;
  if (*(int *)(param_1 + 0x24) == 0) {
    uVar5 = 0x6f;
  }
  puVar7[2] = uVar5;
  uVar5 = dw_uart_get_fifo_depth(param_1);
  *(uint *)(param_1 + 0x30) = uVar5;
  iVar4 = *(int *)(*(int *)(param_1 + 4) + 0x9c);
  iVar6 = *(int *)(*(int *)(param_1 + 4) + 0xa0);
  if (iVar4 == 1) {
    uVar9 = uVar5;
    if ((uVar5 & 0x80000000) != 0) {
      uVar9 = uVar5 + 3;
    }
    iVar4 = (int)uVar9 >> 2;
LAB_102034f4:
    *(int *)(param_1 + 0x38) = iVar4;
  }
  else {
    if (iVar4 == 0) {
      iVar4 = 1;
      goto LAB_102034f4;
    }
    if (iVar4 == 2) {
      iVar4 = (int)uVar5 / 2;
      goto LAB_102034f4;
    }
    if (iVar4 == 3) {
      iVar4 = uVar5 - 2;
      goto LAB_102034f4;
    }
  }
  if (iVar6 == 1) {
    uVar3 = 2;
  }
  else {
    uVar3 = 0;
    if (iVar6 != 0) {
      if (iVar6 == 2) {
        if ((uVar5 & 0x80000000) != 0) {
          uVar5 = uVar5 + 3;
        }
        iVar4 = (int)uVar5 >> 2;
      }
      else {
        if (iVar6 != 3) goto LAB_102034d6;
        iVar4 = (int)uVar5 / 2;
      }
      *(int *)(param_1 + 0x34) = iVar4;
      goto LAB_102034d6;
    }
  }
  *(undefined4 *)(param_1 + 0x34) = uVar3;
LAB_102034d6:
  *(undefined4 *)(param_1 + 0x2c) = 1;
  *(undefined4 *)(param_1 + 0x68) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x7c) = 0xffffffff;
  func_0x1002553c(*(undefined4 *)(param_1 + 0x3c),PTR_dw_uart_isr_1020352c,param_1);
  return 0;
}

