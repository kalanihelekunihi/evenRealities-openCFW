
undefined8 FUN_0055fae2(undefined4 *param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  
  local_18 = param_4;
  iVar2 = FUN_0055fc38(*param_1,0x807,&local_18,1);
  iVar1 = DAT_0055fc08;
  if (iVar2 == DAT_0055fc08) {
    local_18 = CONCAT31(local_18._1_3_,
                        (*param_2 == '\0') << PTR_DAT_0055fc18[*(byte *)(param_1 + 1)] &
                        PTR_DAT_0055fc10[*(byte *)(param_1 + 1)] |
                        PTR_DAT_0055fc0c[*(byte *)(param_1 + 1)] &
                        param_2[4] << (uint)(byte)PTR_DAT_0055fc14[*(byte *)(param_1 + 1)] |
                        (byte)local_18 & ~PTR_DAT_0055fc0c[*(byte *)(param_1 + 1)] &
                        ~PTR_DAT_0055fc10[*(byte *)(param_1 + 1)]);
    iVar2 = FUN_0055fc2c(*param_1,0x807,&local_18,1);
    if (iVar2 == iVar1) {
      iVar2 = iVar1;
    }
  }
  return CONCAT44(local_18,iVar2);
}

