
undefined4 FUN_0048fc26(int param_1,int param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_40 [4];
  int local_3c;
  ushort local_30;
  uint uStack_18;
  
  uStack_18 = param_4;
  iVar1 = FUN_004d93a4(auStack_40,param_2);
  if (iVar1 == 0) {
    uVar2 = DAT_004905b4;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  else if ((local_30 == param_3) && (local_3c != 0)) {
    *(undefined1 *)(param_2 + 0xc) = 1;
    uVar2 = FUN_0048fbe4(param_1,param_4 & 0xff,auStack_40);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

