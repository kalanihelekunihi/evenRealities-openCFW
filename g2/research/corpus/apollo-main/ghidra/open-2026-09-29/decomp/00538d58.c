
undefined4 FUN_00538d58(byte param_1,uint *param_2,int *param_3)

{
  undefined4 uVar1;
  uint uVar2;
  uint *puVar3;
  
  if (param_1 < 0xc) {
    if ((((param_2 == (uint *)0x0) || (param_2[1] == 0)) || (param_3 == (int *)0x0)) ||
       (*param_2 < 2)) {
      uVar1 = 6;
    }
    else if (*(int *)(DAT_00539244 + (uint)param_1 * 0x2c) << 7 < 0) {
      uVar1 = 7;
    }
    else {
      puVar3 = (uint *)((uint)param_1 * 0x2c + DAT_00539244);
      puVar3[6] = *param_2 << 3;
      uVar2 = param_2[1];
      puVar3[1] = uVar2;
      puVar3[3] = uVar2;
      puVar3[5] = uVar2;
      puVar3[4] = uVar2;
      puVar3[2] = param_2[1] + *param_2 * 8;
      *puVar3 = *puVar3 | 0x1000000;
      *puVar3 = *puVar3 & 0xfdffffff;
      *puVar3 = *puVar3 & 0xff000000 | 0xcdcdcd;
      puVar3[9] = DAT_00539248 + (uint)param_1 * 0x28;
      puVar3[7] = 0;
      puVar3[8] = 0;
      **(undefined4 **)(puVar3[9] + 8) = 0;
      **(undefined4 **)(puVar3[9] + 0xc) = 0;
      **(uint **)(puVar3[9] + 0x10) = **(uint **)(puVar3[9] + 0x10) | *(uint *)(puVar3[9] + 0x14);
      **(uint **)(puVar3[9] + 4) = param_2[1];
      **(int **)puVar3[9] = ((byte)param_2[2] & 1) << 1;
      *param_3 = (int)puVar3;
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 5;
  }
  return uVar1;
}

