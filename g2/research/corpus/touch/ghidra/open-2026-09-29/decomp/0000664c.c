
void touch_sub_334c(int param_1,uint param_2,int *param_3)

{
  uint uVar1;
  code *pcVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  
  puVar5 = (uint *)**(undefined4 **)(*param_3 + 8);
  uVar6 = param_2;
  if (0x15 < param_2) {
    uVar6 = 0x15;
  }
  *(short *)(param_3[2] + 0x46) = (short)uVar6;
  if (param_2 != 0) {
    puVar4 = (uint *)(param_3[10] + param_1 * 0x1c);
    puVar3 = puVar5 + 0x800;
    *puVar5 = *puVar5 & 0x7fffffff;
    if ((int)(puVar5[0x60] << 7) < 0) {
      puVar5[0x51] = 0x10000;
    }
    else {
      puVar5[0x51] = 1;
      touch_sub_3308(0x1b9,2,param_3);
    }
    for (uVar1 = 0; uVar1 < uVar6; uVar1 = uVar1 + 1) {
      *puVar3 = *(byte *)((int)puVar4 + 0x1b) & 0xf;
      puVar3[1] = 0;
      puVar3[2] = 0;
      puVar3[3] = puVar4[6] & 0xffffff;
      puVar3[4] = 0;
      puVar3[5] = *puVar4;
      puVar3[6] = puVar4[1];
      puVar3[7] = puVar4[2];
      puVar3[8] = puVar4[3];
      puVar3[9] = puVar4[4];
      puVar3[10] = puVar4[5];
      puVar4 = puVar4 + 7;
      puVar3 = puVar3 + 0xb;
    }
    puVar3[-1] = puVar3[-1] | 4;
    uVar1 = DAT_00006774;
    puVar5[3] = puVar5[3] & DAT_00006774;
    *puVar5 = *puVar5 & DAT_00006778;
    puVar5[2] = (0x100 - uVar6) * 0x10000 & DAT_0000677c | uVar1 & puVar5[2];
    pcVar2 = *(code **)param_3[2];
    if ((pcVar2 != (code *)0x0) && (*(char *)((int)param_3[2] + 0x61) == '\x01')) {
      (*pcVar2)(param_3[7]);
    }
    if ((*(char *)(param_3[2] + 0x61) == '\x01') && ((int)(puVar5[0x60] << 7) < 0)) {
      puVar5[0x51] = 0x100;
    }
    *puVar5 = *puVar5 | 0x80000000;
    puVar5[0x50] = 1;
  }
  return;
}

