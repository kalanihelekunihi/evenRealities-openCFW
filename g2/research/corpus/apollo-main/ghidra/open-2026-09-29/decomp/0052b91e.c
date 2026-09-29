
undefined4 WsfSetEvent(uint param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  WsfCsEnter();
  iVar1 = DAT_0052bac4;
  *(byte *)(DAT_0052bac4 + (param_1 & 0xf) + 0x28) =
       param_2 | *(byte *)((param_1 & 0xf) + DAT_0052bac4 + 0x28);
  *(byte *)(iVar1 + 0x3c) = *(byte *)(iVar1 + 0x3c) | 4;
  WsfCsExit();
  WsfSetOsSpecificEvent();
  return param_4;
}

