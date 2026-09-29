
undefined4 gx8002_power_initialize(void)

{
  uint *puVar1;
  uint uVar2;
  undefined4 uVar3;
  uint *puVar4;
  
  uVar2 = func_0x10024940();
  puVar1 = puRam102076b8;
  if (uVar2 < 2) {
    gx8002_memset(uRam102076bc,0,0x90);
    uVar3 = 1;
  }
  else {
    puVar4 = puRam102076b8;
    for (uVar2 = 0; uVar2 < puVar1[-0x11]; uVar2 = uVar2 + 1) {
      (*(code *)(*puVar4 & 0xfffffffe))(puVar4[1]);
      puVar4 = puVar4 + 2;
    }
    uVar3 = 0;
  }
  return uVar3;
}

