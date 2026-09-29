
void touch_state_291e_cap_record(int param_1,uint param_2,int param_3)

{
  ushort uVar1;
  ushort *puVar2;
  int *piVar3;
  
  piVar3 = (int *)(*(int *)(param_3 + 0xc) + param_1 * 0x90);
  puVar2 = (ushort *)(piVar3[1] + param_2 * 10);
  uVar1 = *(ushort *)(*piVar3 + 4);
  if ((*(char *)((int)piVar3 + 0x7a) == '\x01') && (*(byte *)((int)piVar3 + 0x3a) <= param_2)) {
    uVar1 = *(ushort *)(*piVar3 + 6);
  }
  if (uVar1 < *puVar2) {
    *puVar2 = uVar1;
  }
  return;
}

