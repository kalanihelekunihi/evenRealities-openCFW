
int FUN_0058e360(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 local_38;
  uint local_34;
  undefined1 auStack_30 [32];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  local_34 = FUN_00473940();
  iVar2 = FUN_0058e2d8(param_1,auStack_30,0x20,&local_38);
  if ((iVar2 == 0) && (iVar3 = FUN_00530084(param_1 + 0x4c,auStack_30,local_38), iVar3 == 0)) {
    iVar2 = DAT_0058e940;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((local_34 & 1) == 1);
  }
  return iVar2;
}

