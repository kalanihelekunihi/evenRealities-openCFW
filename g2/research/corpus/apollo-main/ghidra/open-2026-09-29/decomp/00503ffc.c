
void FUN_00503ffc(int param_1,undefined4 param_2,char param_3)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  iVar1 = DAT_005040bc;
  if ((*(char *)(DAT_005040bc + 0x9c) == '\0') && (bVar2 = FUN_0050361c(param_1), bVar2 < 10)) {
    if (param_3 == '\x01') {
      iVar3 = FUN_00536a00();
      if (iVar3 == 0) {
        uVar4 = DmSecGetLocalIrk();
        DmPrivResolveAddr(param_1 + 0x15,uVar4,1);
      }
      else {
        uVar4 = DmSecGetLocalIrk();
        DmPrivResolveAddr(param_1 + 0x13,uVar4,1);
      }
      *(byte *)(iVar1 + 0x97) = bVar2;
      *(undefined4 *)(iVar1 + 0x98) = param_2;
      *(undefined1 *)(iVar1 + 0x9c) = 1;
    }
    else if (((param_3 == '\0') && (iVar3 = FUN_0047a630(0), iVar3 != 0)) &&
            (iVar5 = FUN_0047ae78(iVar3,4,0), iVar5 != 0)) {
      iVar6 = FUN_00536a00();
      if (iVar6 == 0) {
        DmPrivResolveAddr(param_1 + 7,iVar5,0);
      }
      else {
        DmPrivResolveAddr(param_1 + 0xc,iVar5,0);
      }
      *(byte *)(iVar1 + 0x97) = bVar2;
      *(int *)(iVar1 + 0x98) = iVar3;
      *(undefined1 *)(iVar1 + 0x9c) = 1;
    }
  }
  return;
}

