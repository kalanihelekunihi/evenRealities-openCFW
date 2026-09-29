
undefined4 * FUN_00514ebc(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = (undefined4 *)FUN_0051416c(0x88);
  puVar3[0x21] = 0;
  if (puVar3 == (undefined4 *)0x0) {
    FUN_0051565c(1);
    return (undefined4 *)0x0;
  }
  FUN_00561810(puVar3 + 0x18);
  puVar3[0x21] = 0;
  if (puVar3 != (undefined4 *)0x0) {
    puVar3[2] = 0;
    puVar3[3] = 0;
    *puVar3 = 0;
    uVar2 = DAT_00514f38;
    uVar1 = DAT_00514f34;
    puVar3[1] = 0;
    puVar3[4] = uVar1;
    puVar3[5] = uVar1;
    puVar3[6] = uVar2;
    puVar3[7] = uVar2;
    puVar3[0x14] = 0;
    puVar3[0x15] = 0;
    puVar3[9] = 0;
    puVar3[8] = 0;
    puVar3[0xb] = 0;
    puVar3[10] = 0;
    puVar3[0xd] = 0;
    puVar3[0xc] = 0;
    puVar3[0xf] = 0;
    puVar3[0xe] = 0;
    puVar3[0x16] = 0;
    puVar3[0x17] = 0;
    puVar3[0x10] = uVar1;
    puVar3[0x11] = uVar1;
    puVar3[0x12] = uVar2;
    puVar3[0x13] = uVar2;
  }
  return puVar3;
}

