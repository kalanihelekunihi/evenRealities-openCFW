
void Ins_UNKNOWN(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  puVar3 = *(undefined4 **)(param_1 + 0x1a4);
  puVar2 = puVar3 + *(int *)(param_1 + 0x19c) * 6;
  while( true ) {
    if (puVar2 <= puVar3) {
      *(undefined4 *)(param_1 + 0xc) = 0x80;
      return;
    }
    if (((puVar3[3] & 0xff) == (uint)*(byte *)(param_1 + 0x174)) && (*(char *)(puVar3 + 4) != '\0'))
    break;
    puVar3 = puVar3 + 6;
  }
  if (*(int *)(param_1 + 0x1b4) <= *(int *)(param_1 + 0x1b0)) {
    *(undefined4 *)(param_1 + 0xc) = 0x82;
    return;
  }
  iVar1 = *(int *)(param_1 + 0x1b0);
  *(int *)(param_1 + 0x1b0) = iVar1 + 1;
  puVar2 = (undefined4 *)(iVar1 * 0x10 + *(int *)(param_1 + 0x1b8));
  *puVar2 = *(undefined4 *)(param_1 + 0x164);
  puVar2[1] = *(int *)(param_1 + 0x16c) + 1;
  puVar2[2] = 1;
  puVar2[3] = puVar3;
  Ins_Goto_CodeRange(param_1,*puVar3,puVar3[1]);
  *(undefined1 *)(param_1 + 0x17c) = 0;
  return;
}

