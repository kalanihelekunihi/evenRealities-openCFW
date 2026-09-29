
undefined4 nvdbMacDefaultInitialize(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined4 uStack_58;
  undefined1 auStack_54 [4];
  undefined1 auStack_50 [4];
  undefined1 auStack_4c [4];
  undefined1 auStack_48 [4];
  undefined1 auStack_44 [56];
  
  uStack_58 = 0;
  FUN_00480d72(1,auStack_4c);
  FUN_00439be4(auStack_54,auStack_44,4);
  FUN_00439be4(auStack_50,auStack_48,4);
  uStack_58 = FUN_004d34c4(auStack_54,8,0);
  iVar1 = DAT_005da060;
  FUN_00439be4(DAT_005da060 + 1,&uStack_58,4);
  uVar2 = FUN_0049acd4(auStack_54,8,0);
  *(char *)(iVar1 + 5) = (char)((ushort)uVar2 >> 8);
  *(char *)(iVar1 + 6) = (char)uVar2;
  *(byte *)(iVar1 + 6) = *(byte *)(iVar1 + 6) & 0xfc;
  *(byte *)(iVar1 + 6) = *(byte *)(iVar1 + 6) | 0xc0;
  uVar2 = FUN_0049acd4(iVar1,8,0);
  *(undefined2 *)(iVar1 + 8) = uVar2;
  return 0;
}

