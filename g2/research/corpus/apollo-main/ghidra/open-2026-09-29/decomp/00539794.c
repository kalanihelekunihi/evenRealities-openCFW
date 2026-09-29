
undefined4 FUN_00539794(int param_1,uint param_2,int param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  undefined1 *puVar6;
  undefined1 uStack_30;
  char local_2f [11];
  undefined1 uStack_24;
  char local_23;
  char local_22;
  byte local_21;
  byte local_20;
  byte local_1f;
  
  puVar6 = &uStack_30;
  iVar1 = FUN_00539674(&uStack_24,param_2,param_3,DAT_00539d94);
  iVar2 = FUN_00539674(&uStack_30,param_2,param_3,DAT_00539d98);
  if (iVar1 != 0 || iVar2 != 0) {
    puVar6 = &uStack_30;
    if ((iVar2 != 0) && (puVar6 = (undefined1 *)0x0, iVar1 == 0)) {
      puVar6 = &uStack_24;
    }
  }
  else {
    uVar4 = (uint)(local_22 == '\0');
    if (local_23 == '\x01') {
      uVar4 = uVar4 + 2;
    }
    uVar5 = (uint)(local_2f[1] == '\0');
    if (local_2f[0] == '\x01') {
      uVar5 = uVar5 + 2;
    }
    if (*(int *)(DAT_00539da0 + uVar4 * 4) *
        (((uint)local_1f * (uint)local_20 * param_3) / DAT_00539d90) +
        (*(int *)(DAT_00539d9c + uVar4 * 4) * (param_2 / DAT_00539d90)) / (uint)local_21 <
        *(int *)(DAT_00539da0 + uVar5 * 4) *
        (((uint)(byte)local_2f[4] * (uint)(byte)local_2f[3] * param_3) / DAT_00539d90) +
        (*(int *)(DAT_00539d9c + uVar5 * 4) * (param_2 / DAT_00539d90)) / (uint)(byte)local_2f[2]) {
      puVar6 = &uStack_24;
    }
  }
  if (puVar6 == (undefined1 *)0x0) {
    uVar3 = 5;
  }
  else {
    *(undefined1 *)(param_1 + 1) = puVar6[1];
    *(undefined1 *)(param_1 + 2) = puVar6[2];
    *(undefined1 *)(param_1 + 3) = puVar6[3];
    *(undefined1 *)(param_1 + 4) = puVar6[4];
    *(undefined1 *)(param_1 + 5) = puVar6[5];
    *(undefined2 *)(param_1 + 6) = *(undefined2 *)(puVar6 + 6);
    *(undefined4 *)(param_1 + 8) = *(undefined4 *)(puVar6 + 8);
    uVar3 = 0;
  }
  return uVar3;
}

