
void Ins_LOOPCALL(int param_1,int *param_2)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  uVar1 = param_2[1];
  if (uVar1 < *(int *)(param_1 + 0x1a8) + 1U) {
    puVar3 = (undefined4 *)(*(int *)(param_1 + 0x198) + uVar1 * 0x18);
    if ((*(int *)(param_1 + 0x1a8) + 1 != *(int *)(param_1 + 400)) || (puVar3[3] != uVar1)) {
      puVar3 = *(undefined4 **)(param_1 + 0x198);
      puVar2 = puVar3 + *(int *)(param_1 + 400) * 6;
      for (; (puVar3 < puVar2 && (puVar3[3] != uVar1)); puVar3 = puVar3 + 6) {
      }
      if (puVar3 == puVar2) goto LAB_005f5610;
    }
    if (*(char *)(puVar3 + 4) != '\0') {
      if (*(int *)(param_1 + 0x1b4) <= *(int *)(param_1 + 0x1b0)) {
        *(undefined4 *)(param_1 + 0xc) = 0x82;
        return;
      }
      if (*param_2 < 1) {
        return;
      }
      puVar2 = (undefined4 *)(*(int *)(param_1 + 0x1b8) + *(int *)(param_1 + 0x1b0) * 0x10);
      *puVar2 = *(undefined4 *)(param_1 + 0x164);
      puVar2[1] = *(int *)(param_1 + 0x16c) + 1;
      puVar2[2] = *param_2;
      puVar2[3] = puVar3;
      *(int *)(param_1 + 0x1b0) = *(int *)(param_1 + 0x1b0) + 1;
      Ins_Goto_CodeRange(param_1,*puVar3,puVar3[1]);
      *(undefined1 *)(param_1 + 0x17c) = 0;
      *(int *)(param_1 + 0x26c) = *param_2 + *(int *)(param_1 + 0x26c);
      if (*(uint *)(param_1 + 0x26c) <= *(uint *)(param_1 + 0x270)) {
        return;
      }
      *(undefined4 *)(param_1 + 0xc) = 0x8b;
      return;
    }
  }
LAB_005f5610:
  *(undefined4 *)(param_1 + 0xc) = 0x86;
  return;
}

