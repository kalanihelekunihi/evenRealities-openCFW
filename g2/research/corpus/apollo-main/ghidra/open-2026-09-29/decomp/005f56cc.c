
undefined4 Ins_IDEF(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 *puVar4;
  
  if (*(int *)(param_1 + 0x164) == 3) {
    *(undefined4 *)(param_1 + 0xc) = 0x9c;
  }
  else {
    puVar4 = *(undefined4 **)(param_1 + 0x1a4);
    puVar2 = puVar4 + *(int *)(param_1 + 0x19c) * 6;
    for (; (puVar4 < puVar2 && (puVar4[3] != *param_2)); puVar4 = puVar4 + 6) {
    }
    if (puVar4 == puVar2) {
      if (*(uint *)(param_1 + 0x1a0) <= *(uint *)(param_1 + 0x19c)) {
        *(undefined4 *)(param_1 + 0xc) = 0x8d;
        return param_4;
      }
      *(int *)(param_1 + 0x19c) = *(int *)(param_1 + 0x19c) + 1;
    }
    if (*param_2 < 0x100) {
      puVar4[3] = (uint)(byte)*param_2;
      puVar4[1] = *(int *)(param_1 + 0x16c) + 1;
      *puVar4 = *(undefined4 *)(param_1 + 0x164);
      *(undefined1 *)(puVar4 + 4) = 1;
      if (*(uint *)(param_1 + 0x1ac) < *param_2) {
        *(uint *)(param_1 + 0x1ac) = (uint)(byte)*param_2;
      }
      do {
        iVar3 = SkipCode(param_1);
        if (iVar3 != 0) {
          return param_4;
        }
        cVar1 = *(char *)(param_1 + 0x174);
        if (cVar1 == ',') break;
        if (cVar1 == '-') {
          puVar4[2] = *(undefined4 *)(param_1 + 0x16c);
          return param_4;
        }
      } while (cVar1 != -0x77);
      *(undefined4 *)(param_1 + 0xc) = 0x89;
    }
    else {
      *(undefined4 *)(param_1 + 0xc) = 0x8d;
    }
  }
  return param_4;
}

