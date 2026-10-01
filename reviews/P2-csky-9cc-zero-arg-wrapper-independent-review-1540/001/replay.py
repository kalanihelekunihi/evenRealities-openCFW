#!/usr/bin/env python3
def run(r0,r1,r2,lr,callee_state):
    saved_lr=lr & 0xffffffff
    child_args={'R0':r0 & 0xffffffff,'R1':r1 & 0xffffffff,'R2':0}
    # 9CC's complete behavior is intentionally controlled, not modeled here.
    after={k:(v & 0xffffffff) for k,v in callee_state.items()}
    after.setdefault('R0',child_args['R0'])
    return {'entry_state':{'R0':r0 & 0xffffffff,'R1':r1 & 0xffffffff,'R2':r2 & 0xffffffff,'R15':saved_lr},'stack_events':['push R15','pop R15'],'callee_entry':child_args,'callee_return_state':after,'return_pc':saved_lr,'wrapper_post_call_gpr_writes':[]}
