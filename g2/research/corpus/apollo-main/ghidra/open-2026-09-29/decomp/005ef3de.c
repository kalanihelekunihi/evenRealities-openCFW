
int tt_get_metrics(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  uVar2 = *param_1;
  iVar3 = param_1[6];
  local_20 = 0;
  local_24 = 0;
  uVar1 = *(undefined4 *)(iVar3 + 8);
  uStack_1c = param_4;
  TT_Get_HMetrics(uVar2,param_2,(int)&local_20 + 2,&local_24,param_1);
  TT_Get_VMetrics(uVar2,param_2,param_1[0xc],&local_20,(int)&local_24 + 2);
  iVar3 = FT_Stream_Seek(iVar3,uVar1);
  if (iVar3 == 0) {
    param_1[0xd] = (int)local_20._2_2_;
    param_1[0xe] = local_24 & 0xffff;
    param_1[0x2b] = (int)(short)local_20;
    param_1[0x2c] = local_24 >> 0x10;
    if (*(char *)(param_1 + 0x10) == '\0') {
      *(undefined1 *)(param_1 + 0x10) = 1;
      param_1[0xf] = local_24 & 0xffff;
    }
    iVar3 = 0;
  }
  return iVar3;
}

