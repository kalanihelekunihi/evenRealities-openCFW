
void dmAdvConfig(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = DAT_004ba498;
  uVar2 = DmLlAddrType(*(undefined1 *)(DAT_004ba498 + 0xe));
  HciLeSetAdvParamCmd(*(undefined2 *)(DAT_004ba49c + 0x10),*(undefined2 *)(DAT_004ba49c + 0x14),
                      param_1,uVar2,param_2,param_3,*(undefined1 *)(DAT_004ba49c + 0x1a),
                      *(undefined1 *)(iVar1 + 0x11),param_4);
  *DAT_004ba6c0 = param_1;
  return;
}

