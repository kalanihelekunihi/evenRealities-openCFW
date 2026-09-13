# SPDX-License-Identifier: MIT
"""Authenticate reply enqueue alias against the source-owned SDK entry."""
import json,subprocess
from probe_gx8002_reply_sdk_types import probe,ROOT,sha,Elf32


def verify():
    candidate=probe();out=ROOT/'build/gx8002-reply-sdk-types'
    owner=ROOT/'build/gx8002-source-candidate/uart-message-enqueue/callback.elf';elf=Elf32(owner.read_bytes(),'enqueue')
    report=json.loads((ROOT/'docs/research/gx8002-uart-message-enqueue-source-verification.json').read_text())
    row=next(r for r in report['functions'] if r['symbol']=='UartMessageAsyncSend')
    symbol=next(s for s in elf.symbols() if s['name']==row['symbol']);section=elf.sections[symbol['section']]
    assert section['flags']&4 and symbol['value']==0x102083bc and sha(elf.contents(section))==row['compiled_sha256']
    for name in ('app_reply','i2s_ack'):
        e=Elf32((out/(name+'.elf')).read_bytes(),name)
        alias=next(s for s in e.symbols() if s['name']=='open_cfw_gx8002_app_enqueue')
        assert alias['value']==symbol['value']
    contract=(out/'type_contract.c').read_text()+'\n_Static_assert(__builtin_types_compatible_p(__typeof__(&open_cfw_gx8002_app_enqueue), __typeof__(&UartMessageAsyncSend)), "enqueue SDK signature");\n'
    path=out/'enqueue_contract.c';path.write_text(contract)
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),'-mcpu=ck804ef','-mhard-float','-ffreestanding','-Wall','-Wextra','-Werror','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/lvp/common'),'-fsyntax-only',str(path)],check=True)
    return {'candidate':candidate,'enqueue_owner_elf_sha256':sha(owner.read_bytes()),'enqueue_symbol':symbol,'type_contract_sha256':sha(contract.encode()),'source_admitted':False,'limits':['Both staged helper aliases resolve to authenticated source-owned UartMessageAsyncSend, and their function pointer types match its SDK declaration. This verifies address/type binding, not nested runtime enqueue execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-reply-enqueue-binding.json').write_text(json.dumps(r,indent=2)+'\n');print('Reply enqueue source ownership and SDK type verified')
