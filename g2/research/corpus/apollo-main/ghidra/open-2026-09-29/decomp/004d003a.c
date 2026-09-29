
uint FUN_004d003a(int param_1,int param_2,uint param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_2 + 0xc);
  iVar1 = *(int *)(param_2 + 8);
  if (iVar2 == 0) {
    FUN_004d09b4(DAT_004d085c,DAT_004d06ac,0x245);
  }
  if (iVar1 == 0) {
    FUN_004d09b4(DAT_004d094c,DAT_004d06ac,0x246);
  }
  *(int *)(iVar1 + 0xc) = iVar2;
  *(int *)(iVar2 + 8) = iVar1;
  if (((*(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74) == param_2) &&
      (*(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74) = iVar1, iVar1 == param_1)) &&
     (*(uint *)(param_1 + param_3 * 4 + 0x14) =
           *(uint *)(param_1 + param_3 * 4 + 0x14) & ~(1 << (param_4 & 0xff)),
     *(int *)(param_1 + param_3 * 4 + 0x14) == 0)) {
    *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) & ~(1 << (param_3 & 0xff));
  }
  return param_4;
}

