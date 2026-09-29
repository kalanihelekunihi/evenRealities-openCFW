
undefined4 dw_uart_isr(undefined4 param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 *puVar5;
  undefined4 *puVar6;
  int iVar7;
  undefined4 *puVar8;
  uint uVar9;
  undefined1 *puVar10;
  uint uVar11;
  
  uVar11 = *(uint *)(param_2[1] + 8);
  if ((uVar11 & 4) != 0) {
    uVar2 = *(uint *)(param_2[1] + 0x84);
    if (param_2[0x10] == 1) {
      (*(code *)(param_2[0x14] & 0xfffffffe))(*param_2,uVar2,param_2[0x15]);
    }
    else if ((param_2[0xb] == 0) && (param_2[0x10] == 2)) {
      uVar9 = param_2[0x19];
      iVar4 = (uVar2 < uVar9) * uVar2 + (uVar2 >= uVar9) * uVar9;
      puVar5 = (undefined1 *)param_2[0x18];
      for (puVar10 = puVar5; (int)puVar10 - (int)puVar5 < iVar4; puVar10 = puVar10 + 1) {
        *puVar10 = (char)*(undefined4 *)param_2[1];
      }
      param_2[0x18] = param_2[0x18] + iVar4;
      iVar7 = param_2[0x19];
      param_2[0x19] = iVar7 - iVar4;
      if (iVar7 - iVar4 == 0) {
        uVar3 = param_2[0x17];
        *(uint *)(param_2[1] + 4) = *(uint *)(param_2[1] + 4) & 0xfffffffe;
        (*(code *)(param_2[0x16] & 0xfffffffe))(*param_2,uVar3);
      }
    }
  }
  if ((uVar11 & 2) != 0) {
    puVar8 = (undefined4 *)param_2[1];
    uVar11 = ((puVar8[0x3d] & 0x7fffff) >> 0x10) * 0x10 - puVar8[0x20];
    if (param_2[0x11] == 1) {
      (*(code *)(param_2[0x12] & 0xfffffffe))(*param_2,uVar11,param_2[0x13]);
    }
    else if ((param_2[0xb] == 0) && (param_2[0x11] == 2)) {
      uVar2 = param_2[0x1e];
      iVar4 = (uVar11 < uVar2) * uVar11 + (uVar11 >= uVar2) * uVar2;
      puVar6 = (undefined4 *)param_2[0x1d];
      for (puVar1 = puVar6; (int)puVar1 - (int)puVar6 < iVar4;
          puVar1 = (undefined4 *)((int)puVar1 + 1)) {
        *puVar8 = *puVar1;
      }
      param_2[0x1d] = (int)puVar6 + iVar4;
      iVar7 = param_2[0x1e];
      param_2[0x1e] = iVar7 - iVar4;
      if (iVar7 - iVar4 == 0) {
        do {
        } while ((puVar8[5] & 0x40) == 0);
        puVar8[1] = puVar8[1] & 0xfffffffd;
        (*(code *)(param_2[0x1b] & 0xfffffffe))(*param_2,param_2[0x1c]);
      }
    }
  }
  return 0;
}

