
undefined4 Ins_FDEF(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  
  if (*(int *)(param_1 + 0x164) == 3) {
    *(undefined4 *)(param_1 + 0xc) = 0x9c;
  }
  else {
    puVar5 = *(undefined4 **)(param_1 + 0x198);
    puVar4 = puVar5 + *(int *)(param_1 + 400) * 6;
    uVar2 = *param_2;
    for (; (puVar5 < puVar4 && (puVar5[3] != uVar2)); puVar5 = puVar5 + 6) {
    }
    if (puVar5 == puVar4) {
      if (*(uint *)(param_1 + 0x194) <= *(uint *)(param_1 + 400)) {
        *(undefined4 *)(param_1 + 0xc) = 0x8c;
        return param_4;
      }
      *(int *)(param_1 + 400) = *(int *)(param_1 + 400) + 1;
    }
    if (uVar2 < 0x10000) {
      *puVar5 = *(undefined4 *)(param_1 + 0x164);
      puVar5[3] = uVar2 & 0xffff;
      puVar5[1] = *(int *)(param_1 + 0x16c) + 1;
      *(undefined1 *)(puVar5 + 4) = 1;
      *(undefined1 *)((int)puVar5 + 0x11) = 0;
      puVar5[5] = 0;
      if (*(uint *)(param_1 + 0x1a8) < uVar2) {
        *(uint *)(param_1 + 0x1a8) = uVar2 & 0xffff;
      }
      do {
        iVar3 = SkipCode(param_1);
        if (iVar3 != 0) {
          return param_4;
        }
        cVar1 = *(char *)(param_1 + 0x174);
        if (cVar1 == ',') break;
        if (cVar1 == '-') {
          puVar5[2] = *(undefined4 *)(param_1 + 0x16c);
          return param_4;
        }
      } while (cVar1 != -0x77);
      *(undefined4 *)(param_1 + 0xc) = 0x89;
    }
    else {
      *(undefined4 *)(param_1 + 0xc) = 0x8c;
    }
  }
  return param_4;
}

