
undefined4 gx8002_dw_spi_setup(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int *piVar5;
  
  *(undefined2 *)(param_1 + 10) = 0;
  if (*(char *)(param_1 + 9) == '\0') {
    *(undefined1 *)(param_1 + 9) = 8;
  }
  piVar5 = *(int **)(param_1 + 0xc);
  if ((*(int **)(param_1 + 0xc) == (int *)0x0) && (piVar5 = DAT_102061fc, *DAT_102061fc != 0)) {
    uVar1 = 0xfffffff4;
  }
  else {
    if (*(int *)(param_1 + 4) == 0) {
      *(undefined4 *)(param_1 + 4) = DAT_10206200;
    }
    uVar2 = func_0x10025210(0xe);
    uVar4 = *(uint *)(param_1 + 4);
    uVar3 = uVar2 / uVar4 & 0xfffffffe;
    *piVar5 = param_1;
    piVar5[1] = (*(ushort *)(param_1 + 10) & 3) << 8 | (*(byte *)(param_1 + 0x10) & 3) << 0x16 |
                0x80000000;
    if (uVar2 != uVar3 * uVar4) {
      uVar3 = uVar3 + 2;
    }
    piVar5[2] = uVar3;
    piVar5[3] = 2;
    uVar1 = 0;
    *(int **)(param_1 + 0xc) = piVar5;
  }
  return uVar1;
}

