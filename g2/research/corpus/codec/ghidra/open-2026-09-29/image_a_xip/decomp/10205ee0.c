
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_gpio_isr(void)

{
  uint uVar1;
  uint uVar2;
  undefined4 *puVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = _DAT_a0001030;
  uVar4 = 0;
  puVar3 = DAT_10205f20;
  do {
    uVar5 = 1 << (uVar4 & 0x3f);
    uVar2 = _DAT_a0001030;
    if (((uVar1 & uVar5) != 0) && (uVar2 = uVar5, puVar3[1] != 0)) {
      (*(code *)(puVar3[1] & 0xfffffffe))(*puVar3,puVar3[2]);
    }
    _DAT_a0001030 = uVar2;
    uVar4 = uVar4 + 1;
    puVar3 = puVar3 + 3;
  } while (uVar4 != 0x20);
  return 0;
}

