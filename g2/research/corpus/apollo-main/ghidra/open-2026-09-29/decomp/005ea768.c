
undefined4 FUN_005ea768(uint param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  
  iVar1 = DAT_005eb28c;
  if ((param_1 < 0xc) && (iVar3 = *(int *)(DAT_005eb28c + param_1 * 4 + 0xc), iVar3 != 0)) {
    iVar2 = td_session_record_at(param_2);
    if (iVar2 == 0) {
      FUN_0043ded4(iVar3,1);
    }
    else {
      uVar4 = *(ushort *)(iVar1 + (uint)param_2 * 2 + 0x3c);
      if (uVar4 < 0x1c) {
        uVar4 = 0x1c;
      }
      FUN_0043f09a(iVar3,0,*(undefined4 *)(iVar1 + (uint)param_2 * 4 + 0xbc));
      FUN_0043f4c0(iVar3,0x240,uVar4);
      FUN_005ea564(iVar3,iVar2,param_2);
      FUN_0043dfa4(iVar3,1);
    }
  }
  return param_4;
}

