
void FUN_005d9b28(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  bool bVar1;
  undefined4 uVar2;
  
  if (*DAT_005d9b58 != 'S') {
    FUN_005d9950();
  }
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getBasePriority();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0x20);
  }
  FUN_005d9abc(param_1,param_2,param_3);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(uVar2);
  }
  return;
}

