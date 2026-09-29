
undefined8 smpScActCalcF5MacKey(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  undefined1 *puVar3;
  int local_18;
  
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,*(undefined4 *)(param_2 + 4));
  smpLogByteArray(&DAT_005e30e4,*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,0x10);
  puVar1 = (undefined1 *)SmpScAlloc(0x35,param_1,param_2);
  local_18 = param_3;
  if (puVar1 != (undefined1 *)0x0) {
    *puVar1 = 0;
    uVar2 = SmpScCat(puVar1 + 1,DAT_005e3110,4);
    uVar2 = SmpScCat128(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
    uVar2 = SmpScCat128(uVar2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
    uVar2 = smpScCatInitiatorBdAddr(param_1,uVar2);
    puVar3 = (undefined1 *)smpScCatResponderBdAddr(param_1,uVar2);
    *puVar3 = 1;
    puVar3[1] = 0;
    SmpScCmac(*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,puVar1,0x35,param_1);
    local_18 = param_2;
  }
  return CONCAT44(param_4,local_18);
}

