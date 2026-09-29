
undefined8 smpScActDHKeyCalcF6Ea(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 *puVar3;
  int iStack_18;
  
  smpLogByteArray(&DAT_005e30ec,*(undefined4 *)(param_2 + 4),0x10);
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,*(undefined4 *)(param_2 + 4),0x10)
  ;
  iVar1 = SmpScAlloc(0x41,param_1,param_2);
  iStack_18 = param_3;
  if (iVar1 != 0) {
    uVar2 = SmpScCat128(iVar1,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
    uVar2 = SmpScCat128(uVar2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
    puVar3 = (undefined1 *)SmpScCat128(uVar2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30);
    *puVar3 = *(undefined1 *)(param_1 + 0x23);
    puVar3[1] = *(undefined1 *)(param_1 + 0x22);
    puVar3[2] = *(undefined1 *)(param_1 + 0x21);
    uVar2 = smpScCatInitiatorBdAddr(param_1,puVar3 + 3);
    smpScCatResponderBdAddr(param_1,uVar2);
    SmpScCmac(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x18),iVar1,0x41,param_1);
    iStack_18 = param_2;
  }
  return CONCAT44(param_4,iStack_18);
}

