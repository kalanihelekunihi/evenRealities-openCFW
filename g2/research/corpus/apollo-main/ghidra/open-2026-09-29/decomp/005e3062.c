
undefined8 smpScActDHKeyCalcF6Eb(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 *puVar3;
  int iStack_18;
  
  smpLogByteArray(DAT_005e3114,*(undefined4 *)(param_2 + 4),0x10);
  iVar1 = SmpScAlloc(0x41,param_1,param_2);
  iStack_18 = param_3;
  if (iVar1 != 0) {
    uVar2 = SmpScCat128(iVar1,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
    uVar2 = SmpScCat128(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
    puVar3 = (undefined1 *)SmpScCat128(uVar2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20);
    *puVar3 = *(undefined1 *)(param_1 + 0x2a);
    puVar3[1] = *(undefined1 *)(param_1 + 0x29);
    puVar3[2] = *(undefined1 *)(param_1 + 0x28);
    uVar2 = smpScCatResponderBdAddr(param_1,puVar3 + 3);
    smpScCatInitiatorBdAddr(param_1,uVar2);
    SmpScCmac(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x18),iVar1,0x41,param_1);
    iStack_18 = param_2;
  }
  FUN_00542a44(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),*(undefined4 *)(param_2 + 4));
  return CONCAT44(param_4,iStack_18);
}

