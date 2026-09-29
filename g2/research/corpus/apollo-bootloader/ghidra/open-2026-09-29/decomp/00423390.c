
undefined8 FUN_00423390(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uStack_20;
  uint local_1c;
  undefined4 uStack_18;
  
  iVar4 = *(int *)(param_1 + 0x28);
  iVar3 = 0;
  uStack_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  local_1c = critical_save();
  do {
    if ((*(int *)(DAT_00423764 + iVar4 * 0x1000 + 0x18) << 0x1a < 0) ||
       (iVar2 = queue_item_get_427660(param_1 + 0x34,&uStack_20,1), iVar2 == 0)) break;
    iVar3 = FUN_0042330e(param_1,&uStack_20,1,&uStack_18);
  } while (iVar3 == 0);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((local_1c & 1) == 1);
  }
  return CONCAT44(uStack_20,iVar3);
}

