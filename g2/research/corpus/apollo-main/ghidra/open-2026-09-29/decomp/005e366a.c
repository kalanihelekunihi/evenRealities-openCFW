
undefined4 smpiScActPkCheck(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int3 iVar1;
  int iVar2;
  int3 iStack_10;
  undefined1 uStack_d;
  
  _iStack_10 = param_4;
  smpLogByteArray(&PTR_DAT_005e38a8,*(undefined4 *)(param_2 + 4),0x10);
  iVar2 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x40,*(undefined4 *)(param_2 + 4)
                       ,0x10);
  if (iVar2 == 0) {
    *(char *)(*(int *)(param_1 + 0x48) + 3) = *(char *)(*(int *)(param_1 + 0x48) + 3) + '\x01';
    if (*(byte *)(*(int *)(param_1 + 0x48) + 3) < 0x14) {
      *(undefined1 *)(param_1 + 0x3f) = 3;
      iVar1 = 0x1a;
    }
    else {
      iVar1 = 0x1b;
    }
    _iStack_10 = CONCAT13(uStack_d,iVar1 << 0x10);
    _iStack_10 = CONCAT22(stack0xfffffff2,(ushort)*(byte *)(param_1 + 0x3d));
    smpSmExecute(param_1,&iStack_10);
  }
  else {
    smpScFailWithReattempt(param_1);
  }
  return _iStack_10;
}

