
undefined4 hw_event_apply_42c0b2(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  
  iVar1 = DAT_0042c6e8;
  iVar4 = *(int *)(param_1 + 0x864);
  iVar5 = *(int *)(param_1 + 4);
  uVar6 = *(undefined4 *)(DAT_0042c6e8 + iVar5 * 0x1000 + 0x200);
  *(undefined4 *)(DAT_0042c6e8 + iVar5 * 0x1000 + 0x200) = 0;
  uVar7 = DAT_0042c6f4;
  if ((int)(param_2 << 0x14) < 0) {
    if (*(int *)(iVar1 + iVar5 * 0x1000 + 0x218) << 0x1e < 0) {
      uVar2 = *(uint *)(iVar1 + iVar5 * 0x1000 + 0x21c);
      while (uVar2 != 0) {
        if (3 < (*(uint *)(iVar1 + iVar5 * 0x1000 + 0x100) & 0xffff) >> 8) {
          *(undefined4 *)(iVar1 + iVar5 * 0x1000 + 0x10c) = uVar7;
          if (uVar2 < 5) break;
          uVar2 = uVar2 - 4;
        }
      }
      do {
      } while ((*(uint *)(iVar1 + iVar5 * 0x1000 + 0x248) & 6) != 4);
    }
    else {
      while (*(int *)(iVar1 + iVar5 * 0x1000 + 0x248) << 0x1e < 0) {
        do {
        } while (3 < (*(uint *)(iVar1 + iVar5 * 0x1000 + 0x100) & 0xffffff) >> 0x10);
      }
      do {
      } while ((*(uint *)(iVar1 + iVar5 * 0x1000 + 0x248) & 6) != 4);
      while ((*(uint *)(iVar1 + iVar5 * 0x1000 + 0x100) & 0xffffff) >> 0x10 != 0) {
        do {
        } while (3 < (*(uint *)(iVar1 + iVar5 * 0x1000 + 0x100) & 0xffffff) >> 0x10);
      }
    }
  }
  if ((param_2 & 0x210) != 0) {
    uVar7 = *(undefined4 *)(iVar1 + iVar5 * 0x1000 + 0x388);
    do {
    } while ((*(uint *)(iVar1 + iVar5 * 0x1000 + 0x248) & 6) != 4);
    puVar3 = (uint *)(iVar1 + iVar5 * 0x1000 + 0x11c);
    *puVar3 = *puVar3 & 0xffffffef;
    puVar3 = (uint *)(iVar1 + iVar5 * 0x1000 + 0x110);
    *puVar3 = *puVar3 & 0xfffffffd;
    *(uint *)(iVar1 + iVar5 * 0x1000 + 0x388) = *(uint *)(iVar1 + iVar5 * 0x1000 + 0x388) | 2;
    delay_us(iVar4 * 6);
    *(undefined4 *)(iVar1 + iVar5 * 0x1000 + 0x388) = uVar7;
    puVar3 = (uint *)(iVar1 + iVar5 * 0x1000 + 0x110);
    *puVar3 = *puVar3 | 2;
    puVar3 = (uint *)(iVar1 + iVar5 * 0x1000 + 0x11c);
    *puVar3 = *puVar3 | 0x10;
  }
  *(undefined4 *)(iVar1 + iVar5 * 0x1000 + 0x208) = 0xffffffff;
  *(undefined4 *)(iVar1 + iVar5 * 0x1000 + 0x200) = uVar6;
  return param_4;
}

