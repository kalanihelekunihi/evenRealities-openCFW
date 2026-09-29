
undefined8
tt_synth_sfnt_checksum(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  
  iVar4 = 0;
  iVar2 = FT_Stream_EnterFrame(param_1,param_2);
  uVar3 = 0;
  if (iVar2 == 0) {
    for (; 3 < param_2; param_2 = param_2 - 4) {
      uVar6 = FT_Stream_GetULong(param_1,uVar3);
      uVar3 = (undefined4)((ulonglong)uVar6 >> 0x20);
      iVar4 = (int)uVar6 + iVar4;
    }
    uVar5 = 3;
    for (; param_2 != 0; param_2 = param_2 - 1) {
      bVar1 = FT_Stream_GetChar(param_1);
      iVar4 = ((uint)bVar1 << ((uVar5 & 0x1f) << 3)) + iVar4;
      uVar5 = uVar5 - 1;
    }
    FT_Stream_ExitFrame(param_1);
  }
  else {
    iVar4 = 0;
  }
  return CONCAT44(param_4,iVar4);
}

