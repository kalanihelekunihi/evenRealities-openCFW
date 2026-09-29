
undefined4 FUN_004bfed6(int param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint *puVar5;
  
  iVar2 = DAT_004c0754;
  iVar4 = *(int *)(param_1 + 4);
  bVar1 = *(byte *)(param_1 + 10);
  if (bVar1 == 0) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 | 0x2000000;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 2) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 5;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 2) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 | 0x2000000;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 4) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 9;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 4) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 6;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 6) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0xd;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 < 6) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 10;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 8) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0xd;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 < 8) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0xe;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 == 10) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0x11;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = DAT_004c0f20;
  }
  else if (bVar1 < 10) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0xe;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 == 0xc) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x100;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 0xc) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 0x12;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = DAT_004c0f20;
  }
  else if (bVar1 == 0xe) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x300;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 0xe) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x100;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 0x10) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x500;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 0x10) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x300;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 0x12) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x700;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 0x12) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x500;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 0x14) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 < 0x14) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x700;
    uVar3 = DAT_004c0998;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x10f;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 0x16) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x900;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 < 0x16) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff;
    uVar3 = DAT_004c0994;
    if (*(char *)(param_1 + 9) == '\0') {
      uVar3 = 0x103;
    }
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = uVar3;
  }
  else if (bVar1 == 0x18) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 1;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0xb00;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 < 0x18) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0x900;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  else if (bVar1 == 0x19) {
    puVar5 = (uint *)(DAT_004c0754 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xffffffe0 | 2;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x84);
    *puVar5 = *puVar5 & 0xfdffffff;
    puVar5 = (uint *)(iVar2 + iVar4 * 0x1000 + 0x90);
    *puVar5 = *puVar5 & 0xfffff0ff | 0xb00;
    *(undefined4 *)(iVar2 + iVar4 * 0x1000 + 0x44) = 0x3ff;
  }
  return 0;
}

