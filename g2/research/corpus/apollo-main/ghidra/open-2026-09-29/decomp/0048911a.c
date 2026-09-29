
int FUN_0048911a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_004d4eea(*(undefined4 *)(DAT_00489420 + 0x134),param_2,0);
  if (iVar1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_004d5396(iVar1);
    *(undefined4 *)(iVar2 + 0xc) = param_3;
    if (*(char *)(iVar2 + 8) == '\x01') {
      uVar3 = FUN_004547c6(*(undefined4 *)(iVar2 + 4));
      *(undefined4 *)(iVar2 + 4) = uVar3;
    }
    *(undefined4 *)(iVar2 + 0x14) = param_4;
    *(undefined4 *)(iVar2 + 0x10) = param_1;
  }
  return iVar1;
}

