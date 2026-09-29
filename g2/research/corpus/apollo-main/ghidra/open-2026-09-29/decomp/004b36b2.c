
undefined8 FUN_004b36b2(int *param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint local_10;
  undefined4 uStack_c;
  
  iVar1 = 0;
  local_10 = param_3;
  uStack_c = param_4;
  if (*param_1 != 0) {
    iVar1 = FUN_0047ae78(*param_1,1,&local_10);
  }
  if (iVar1 == 0) {
    *(undefined1 *)((int)param_1 + 6) = 0;
    DmSecLtkRsp((char)param_1[1],0,0,0);
  }
  else {
    *(bool *)((int)param_1 + 6) = *(char *)((int)param_1 + 5) == '\0';
    DmSecLtkRsp((char)param_1[1],1,local_10 & 0xff);
  }
  return CONCAT44(uStack_c,local_10);
}

