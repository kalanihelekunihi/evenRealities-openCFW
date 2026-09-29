
int IsMacBinary(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char local_94;
  byte local_93;
  char acStack_92 [61];
  char local_55;
  char local_4a;
  char local_42;
  byte local_41;
  byte local_40;
  byte local_3f;
  byte local_3e;
  
  if (param_2 == 0) {
    iVar1 = 0x55;
  }
  else {
    iVar1 = FT_Stream_Seek(param_2,0);
    if ((iVar1 == 0) && (iVar1 = FT_Stream_Read(param_2,&local_94,0x80), iVar1 == 0)) {
      if ((((local_94 == '\0') && (((local_4a == '\0' && (local_42 == '\0')) && (local_93 != 0))))
          && (((local_93 < 0x22 && (local_55 == '\0')) && (acStack_92[local_93] == '\0')))) &&
         (local_41 < 0x80)) {
        iVar1 = IsMacResource(param_1,param_2,
                              (((uint)local_3e |
                               (uint)local_40 << 0x10 | (uint)local_41 << 0x18 | (uint)local_3f << 8
                               ) + 0x7f & 0xffffff80) + 0x80,param_3,param_4);
      }
      else {
        iVar1 = 2;
      }
    }
  }
  return iVar1;
}

