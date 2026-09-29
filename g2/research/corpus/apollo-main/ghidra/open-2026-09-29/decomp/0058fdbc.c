
undefined4 FUN_0058fdbc(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint *puVar5;
  uint uVar6;
  
  iVar1 = DAT_00590814;
  uVar4 = (param_2 & 0xffff) >> 8;
  if ((param_2 & 0xffffff) >> 0x10 == 1) {
    puVar5 = (uint *)(DAT_00590814 + param_1 * 0x1000 + 0x54);
    *puVar5 = *puVar5 | 1;
    uVar4 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xffffefff;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xfff8ffff | (param_2 & 7) << 0x10;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xffffefff | uVar4 & 0x1000;
    uVar4 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xfffffffe;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xfffffe0f | 0x170;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = uVar4 & 1 | *puVar5 & 0xfffffffe;
  }
  else {
    puVar5 = (uint *)(DAT_00590814 + param_1 * 0x1000 + 0x54);
    *puVar5 = *puVar5 & 0xfffffffe;
    uVar2 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xffffefff;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xfff8ffff | 0x40000;
    puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
    *puVar5 = *puVar5 & 0xffffefff | uVar2 & 0x1000;
    uVar2 = (*(uint *)(iVar1 + param_1 * 0x1000 + 0x100) & 0x1ff) >> 4;
    if (param_1 == 0) {
      uVar3 = *DAT_0059089c << 0x19;
    }
    else {
      uVar3 = *DAT_0059089c << 0x17;
    }
    uVar3 = uVar3 >> 0x1e;
    if (uVar4 == uVar3) {
      if ((uVar4 == 2) && (uVar2 != (param_2 & 0xff))) {
        uVar4 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffffe;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffe0f | (param_2 & 0x1f) << 4;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = uVar4 & 1 | *puVar5 & 0xfffffffe;
      }
    }
    else {
      uVar6 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
      puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
      *puVar5 = *puVar5 | 1;
      if (uVar2 == 0x17) {
        uVar2 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffffe;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffe0f | 0xa0;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = uVar2 & 1 | *puVar5 & 0xfffffffe;
      }
      if (uVar3 == 2) {
        FUN_0058fd7e(param_1);
        uVar4 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffffe;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = *puVar5 & 0xfffffe0f | 0x170;
        puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
        *puVar5 = uVar4 & 1 | *puVar5 & 0xfffffffe;
      }
      else if ((uVar3 == 1) || (uVar3 == 0)) {
        if (uVar4 == 2) {
          FUN_0058fd7e(param_1,2);
          uVar4 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x100);
          puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
          *puVar5 = *puVar5 & 0xfffffffe;
          puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
          *puVar5 = *puVar5 & 0xfffffe0f | (param_2 & 0x1f) << 4;
          puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
          *puVar5 = uVar4 & 1 | *puVar5 & 0xfffffffe;
        }
        else {
          FUN_0058fd7e(param_1);
        }
      }
      puVar5 = (uint *)(iVar1 + param_1 * 0x1000 + 0x100);
      *puVar5 = uVar6 & 1 | *puVar5 & 0xfffffffe;
    }
  }
  return param_4;
}

