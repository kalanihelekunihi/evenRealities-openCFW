
longlong cff_slot_init(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = *(int *)(*(int *)(*(int *)(param_1 + 4) + 0x2a4) + 0xc08);
  if ((iVar3 != 0) &&
     (iVar1 = FT_Get_Module(*(undefined4 *)(*(int *)(*(int *)(param_1 + 4) + 0x60) + 4),
                            PTR_s_pshinter_005b00c4), iVar1 != 0)) {
    uVar2 = (**(code **)(iVar3 + 8))();
    *(undefined4 *)(*(int *)(param_1 + 0x9c) + 0x24) = uVar2;
  }
  return (ulonglong)param_4 << 0x20;
}

