
void FUN_004c7752(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char cVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  undefined1 auStack_2c [16];
  undefined4 uStack_1c;
  
  piVar5 = *(int **)(param_1 + 0x48);
  iVar6 = *piVar5;
  uStack_1c = param_4;
  FUN_004c73c4(auStack_2c,param_1 + 0x38);
  FUN_00450bb2(auStack_2c,-piVar5[1],-piVar5[2]);
  FUN_004c73c4(&local_3c,param_1 + 8);
  if (*(char *)(param_1 + 4) == '\x06') {
    iVar7 = *(int *)(param_1 + 0x54);
    if ((((*(int *)(iVar7 + 0x30) == 0) && (*(int *)(iVar7 + 0x34) == 0x100)) &&
        (*(int *)(iVar7 + 0x38) == 0x100)) &&
       ((*(int *)(iVar7 + 0x40) == 0 && (*(int *)(iVar7 + 0x3c) == 0)))) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if (bVar1) {
      uVar3 = FUN_00451598(&local_3c);
      uVar4 = FUN_004515a4(&local_3c);
      FUN_00488cda(&local_3c,uVar3,uVar4,*(undefined4 *)(iVar7 + 0x30),*(undefined4 *)(iVar7 + 0x34)
                   ,*(undefined4 *)(iVar7 + 0x38),iVar7 + 0x44);
      local_3c = *(int *)(param_1 + 8) + local_3c;
      local_38 = *(int *)(param_1 + 0xc) + local_38;
      local_34 = *(int *)(param_1 + 8) + local_34;
      local_30 = *(int *)(param_1 + 0xc) + local_30;
    }
  }
  FUN_00450bb2(&local_3c,-piVar5[1],-piVar5[2]);
  iVar7 = FUN_00450bcc(&local_3c,&local_3c,auStack_2c);
  if (iVar7 != 0) {
    FUN_0048abb8(iVar6,&local_3c);
    cVar2 = FUN_004b092a(iVar6,auStack_2c,0);
    if (cVar2 == '\x01') {
      cVar2 = *(char *)(param_1 + 4);
      if (cVar2 == '\x01') {
        FUN_0053dc38(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
      }
      else if (cVar2 == '\x02') {
        FUN_0053df00(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
      }
      else if (cVar2 == '\x03') {
        FUN_00540036(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
      }
      else if (cVar2 != '\x04') {
        if (cVar2 == '\x05') {
          FUN_004b0bea(*(uint *)(iVar6 + 4) & 0xffff,*(uint *)(iVar6 + 4) >> 0x10);
          FUN_0053faa6(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
        }
        else if (cVar2 == '\x06') {
          FUN_0053f42a(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
        }
        else if (cVar2 == '\a') {
          FUN_0053f400(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
        }
        else if (cVar2 == '\b') {
          FUN_0053ecfc(param_1,*(undefined4 *)(param_1 + 0x54));
        }
        else if (cVar2 == '\t') {
          FUN_0053f09c(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
        }
        else if (cVar2 == '\n') {
          FUN_0053e728(param_1,*(undefined4 *)(param_1 + 0x54));
        }
        else if (cVar2 == '\v') {
          FUN_005409f0(param_1,*(undefined4 *)(param_1 + 0x54),param_1 + 8);
        }
      }
      FUN_004b0c8a(1);
      FUN_0048ab30(iVar6,&local_3c);
    }
  }
  return;
}

