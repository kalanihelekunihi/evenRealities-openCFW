
int FUN_00423350(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 local_38;
  uint local_34;
  undefined1 auStack_30 [32];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  local_34 = critical_save();
  iVar2 = FUN_004232c8(param_1,auStack_30,0x20,&local_38);
  if ((iVar2 == 0) &&
     (iVar3 = queue_item_add_427602(param_1 + 0x4c,auStack_30,local_38), iVar3 == 0)) {
    iVar2 = DAT_0042385c;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((local_34 & 1) == 1);
  }
  return iVar2;
}

