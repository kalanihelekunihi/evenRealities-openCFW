
longlong FUN_005959a2(char *param_1,undefined4 **param_2,undefined4 param_3,undefined4 *param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  char cVar4;
  char *pcVar5;
  undefined4 *local_20;
  
  pcVar5 = param_1;
  local_20 = param_4;
  if (param_2 == (undefined4 **)0x0) {
    param_2 = &local_20;
  }
  while (iVar1 = FUN_004d58ae(*pcVar5), iVar1 != 0) {
    pcVar5 = pcVar5 + 1;
  }
  cVar4 = *pcVar5;
  if (cVar4 == '-' || cVar4 == '+') {
    pcVar5 = pcVar5 + 1;
    iVar1 = FUN_004d58ae(*pcVar5);
    if (iVar1 != 0) goto LAB_005959ec;
  }
  else {
    cVar4 = '+';
  }
  uVar2 = FUN_0048d724(pcVar5,param_2,param_3,param_4);
  if (pcVar5 == (char *)*param_2) {
LAB_005959ec:
    *param_2 = (undefined4 *)param_1;
    return ZEXT48(local_20) << 0x20;
  }
  if (cVar4 == '+') {
    if (0x7fffffff < uVar2) {
LAB_00595a0e:
      FUN_00439cb2();
      if (param_4 != (undefined4 *)0x0) {
        *param_4 = 1;
      }
      if (cVar4 == '-') {
        uVar3 = 0x80000000;
      }
      else {
        uVar3 = 0x7fffffff;
      }
      return CONCAT44(local_20,uVar3);
    }
  }
  else if (cVar4 == '-') {
    if (uVar2 < 0x80000001) {
      return CONCAT44(local_20,-uVar2);
    }
    goto LAB_00595a0e;
  }
  return CONCAT44(local_20,uVar2);
}

