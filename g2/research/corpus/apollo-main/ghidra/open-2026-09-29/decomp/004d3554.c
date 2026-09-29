
undefined4 FUN_004d3554(undefined2 *param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_004d3608;
  if (param_1 == (undefined2 *)0x0) {
    uVar2 = 6;
  }
  else {
    if (*DAT_004d3608 == 0) {
      *DAT_004d3608 = *DAT_004d360c;
    }
    *puVar1 = *puVar1 & 0x1fff;
    *param_1 = (short)*puVar1;
    *(byte *)(param_1 + 1) = (byte)*puVar1 & 1;
    *(byte *)((int)param_1 + 3) = (byte)(*puVar1 >> 1) & 1;
    *(byte *)(param_1 + 2) = (byte)(*puVar1 >> 2) & 1;
    *(byte *)((int)param_1 + 5) = (byte)(*puVar1 >> 3) & 1;
    *(byte *)(param_1 + 3) = (byte)(*puVar1 >> 4) & 1;
    *(byte *)((int)param_1 + 7) = (byte)(*puVar1 >> 5) & 1;
    *(byte *)(param_1 + 4) = (byte)(*puVar1 >> 6) & 1;
    *(byte *)((int)param_1 + 9) = (byte)(*puVar1 >> 7) & 1;
    *(byte *)(param_1 + 5) = (byte)(*puVar1 >> 8) & 1;
    *(byte *)((int)param_1 + 0xb) = (byte)(*puVar1 >> 9) & 1;
    *(byte *)(param_1 + 6) = (byte)(*puVar1 >> 10) & 1;
    *(undefined1 *)((int)param_1 + 0xd) = 0;
    *(byte *)(param_1 + 7) = (byte)(*puVar1 >> 0xc) & 1;
    if (*puVar1 == 0) {
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

