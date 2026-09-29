
undefined4 FUN_004c08a8(uint *param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;
  
  iVar1 = DAT_004c0990;
  uVar3 = param_1[1];
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c0f68)) {
    uVar2 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar2 = 7;
  }
  else {
    puVar4 = (uint *)(DAT_004c0990 + uVar3 * 0x1000 + 0x90);
    *puVar4 = *puVar4 & 0xfffffffe;
    *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x9c) = 0;
    *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x80) = 0;
    iVar1 = DAT_004c0f64;
    *(undefined4 *)(uVar3 * 0x8d0 + DAT_004c0f64 + 0x18) = param_2[1];
    *(undefined4 *)(uVar3 * 0x8d0 + iVar1 + 0x14) = *param_2;
    if (param_1[6] != 0) {
      *(bool *)(param_1 + 0x232) = param_1[6] + param_1[5] * 4 < DAT_004c0f6c;
      *(uint *)(uVar3 * 0x8d0 + iVar1 + 0x858) = ((param_1[5] - 8) * 4) / 0x48;
      if (0x100 < *(uint *)(uVar3 * 0x8d0 + iVar1 + 0x858)) {
        *(undefined4 *)(uVar3 * 0x8d0 + iVar1 + 0x858) = 0x100;
      }
    }
    *(undefined1 *)(uVar3 * 0x8d0 + iVar1 + 9) = *(undefined1 *)(param_2 + 2);
    *(undefined1 *)(uVar3 * 0x8d0 + iVar1 + 8) = 1;
    *(undefined1 *)(iVar1 + uVar3 * 0x8d0 + 10) = 0x1a;
    uVar2 = 0;
  }
  return uVar2;
}

