
undefined4 FUN_100061a4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  char *pcVar2;
  char local_11c;
  char local_11b [255];
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  pcVar2 = &local_11c;
  uStack_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  uVar1 = FUN_10006fa4(&local_11c,param_1,&uStack_c);
  while (local_11c != '\0') {
    pcVar2 = pcVar2 + 1;
    FUN_10002a84();
    local_11c = *pcVar2;
  }
  return uVar1;
}

