
undefined4 FUN_004406c4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_38 [16];
  undefined1 auStack_28 [16];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar1 = FUN_0043e0e0(param_1,1);
  if (iVar1 == 0) {
    iVar1 = FUN_0044dbc4(param_1);
    uVar2 = FUN_0044dc0a(iVar1);
    iVar3 = FUN_0044fc62(uVar2);
    if ((((iVar1 == iVar3) || (iVar3 = FUN_0044fc90(uVar2), iVar1 == iVar3)) ||
        (iVar3 = FUN_0044fd38(uVar2), iVar1 == iVar3)) ||
       ((iVar3 = FUN_0044fcbe(uVar2), iVar1 == iVar3 ||
        (iVar3 = FUN_0044fcfc(uVar2), iVar1 == iVar3)))) {
      uVar2 = FUN_00452dc8(param_1);
      FUN_0043ee94(auStack_28,param_1 + 0x14);
      FUN_00450b98(auStack_28,uVar2,uVar2);
      iVar1 = FUN_00450bcc(param_2,param_2,auStack_28);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        iVar1 = thunk_FUN_00440a1c(param_1);
        if (iVar1 != 0) {
          FUN_00440494(param_1,param_2,1);
        }
        for (iVar1 = FUN_0044dca2(param_1); iVar1 != 0; iVar1 = FUN_0044dca2(iVar1)) {
          iVar3 = FUN_0043e0e0(iVar1,1);
          if (iVar3 != 0) {
            return 0;
          }
          FUN_00439c04(auStack_38,iVar1 + 0x14,0x10);
          iVar3 = FUN_0043e0e0(iVar1,0x100000);
          if (iVar3 != 0) {
            uVar2 = FUN_00452dc8(iVar1);
            FUN_00450b98(auStack_38,uVar2);
          }
          iVar3 = thunk_FUN_00440a1c(iVar1);
          if (iVar3 != 0) {
            FUN_00440494(iVar1,auStack_38,1);
          }
          iVar3 = FUN_00450bcc(param_2,param_2,auStack_38);
          if (iVar3 == 0) {
            return 0;
          }
        }
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

