
uint * FUN_0041560c(int param_1,uint param_2,uint param_3)

{
  undefined1 uVar1;
  undefined2 uVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = (param_3 & 0xff) << 8;
  uVar4 = param_3 & 0xff | uVar5;
  uVar5 = uVar4 | (param_3 & 0xffff00ff | uVar5) << 0x10;
  puVar3 = (uint *)(param_1 + param_2);
  uVar6 = (uint)puVar3 & 3;
  uVar1 = (undefined1)param_3;
  uVar2 = (undefined2)uVar4;
  if (uVar6 != 0) {
    uVar4 = param_2 - uVar6;
    if (param_2 < uVar6) {
      if (uVar4 + uVar6 != 0) {
        puVar3 = (uint *)((int)puVar3 + -1);
        *(undefined1 *)puVar3 = uVar1;
      }
      if ((uVar4 + uVar6 & 2) != 0) {
        puVar3 = (uint *)((int)puVar3 + -1);
        *(undefined1 *)puVar3 = uVar1;
      }
      return puVar3;
    }
    uVar6 = (uint)puVar3 & 2;
    if ((int)puVar3 * -0x80000000 < 0) {
      puVar3 = (uint *)((int)puVar3 + -1);
      *(undefined1 *)puVar3 = uVar1;
    }
    param_2 = uVar4;
    if (uVar6 != 0) {
      puVar3 = (uint *)((int)puVar3 + -2);
      *(undefined2 *)puVar3 = uVar2;
    }
  }
  do {
    uVar4 = param_2;
    param_2 = uVar4 - 0x10;
    if (0xf < uVar4) {
      puVar3[-1] = uVar5;
      puVar3[-2] = uVar5;
      puVar3[-3] = uVar5;
      puVar3 = puVar3 + -4;
      *puVar3 = uVar5;
    }
  } while (0xf < uVar4 && param_2 != 0);
  if ((param_2 & 8) != 0) {
    puVar3[-1] = uVar5;
    puVar3 = puVar3 + -2;
    *puVar3 = uVar5;
  }
  if ((int)(uVar4 * 0x20000000) < 0) {
    puVar3 = puVar3 + -1;
    *puVar3 = uVar5;
  }
  if ((uVar4 * 0x20000000 & 0x40000000) != 0) {
    puVar3 = (uint *)((int)puVar3 + -2);
    *(undefined2 *)puVar3 = uVar2;
  }
  if ((int)(uVar4 * -0x80000000) < 0) {
    puVar3 = (uint *)((int)puVar3 + -1);
    *(undefined1 *)puVar3 = uVar1;
  }
  return puVar3;
}

