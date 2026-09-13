# SPDX-License-Identifier: MIT
"""Address-parameterized adaptation of the restricted queue decoder."""
import re
from compare_gx8002_queue_get import signed

def execute(code, memory, start, queue_address, record_address):
    registers = {f'r{i}': 0x98760000+i for i in range(32)}
    registers.update(r0=queue_address, r1=record_address)
    original = registers.copy()
    pc, condition = start, False
    trace = []
    for _ in range(10000):
        op, args, width = code[pc]
        parts = [p.strip() for p in args.split(',')]
        next_pc = pc + width
        if op == 'mov': registers[parts[0]] = registers[parts[1]]
        elif op == 'movi': registers[parts[0]] = int(parts[1], 0)
        elif op in ('cmpne', 'cmplt'):
            a, b = (registers[p] for p in parts)
            condition = a != b if op == 'cmpne' else signed(a) < signed(b)
        elif op in ('bt', 'bf', 'br'):
            if op == 'br' or (condition if op == 'bt' else not condition): next_pc = int(parts[0], 0)
        elif op in ('addu', 'subu', 'mult', 'divs', 'addi'):
            a = registers[parts[0] if len(parts) == 2 else parts[1]]
            b = int(parts[-1], 0) if op == 'addi' else registers[parts[-1]]
            if op in ('addu', 'addi'): result = a + b
            elif op == 'subu': result = a - b
            elif op == 'mult': result = a * b
            else:
                a, b = signed(a), signed(b)
                if not b: raise ValueError('division by zero')
                result = (abs(a) // abs(b)) * (-1 if (a < 0) != (b < 0) else 1)
            registers[parts[0]] = result & 0xffffffff
        elif op in ('ld.w', 'st.w', 'ldr.b', 'str.b', 'stbi.b', 'ldbi.b'):
            m = re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+)|(, r\d+ << 0))?\)', args)
            if not m: raise ValueError('unsupported memory operand: '+args)
            value, base, immediate, indexed = m.groups()
            offset = registers[indexed.split()[1]] if indexed else int(immediate or '0', 0)
            address = registers[base] + offset
            size = 4 if op.endswith('.w') else 1
            reading = op.startswith('ld')
            if any(address+i not in memory for i in range(size)): raise ValueError('out-of-bounds access')
            trace.append(('read' if reading else 'write', address, size))
            if reading: registers[value] = sum(memory[address+i] << (i*8) for i in range(size))
            else:
                for i in range(size): memory[address+i] = (registers[value] >> (i*8)) & 255
            if op in ('stbi.b', 'ldbi.b'): registers[base] += 1
        elif op == 'rts':
            assert all(registers[f'r{i}']==original[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return registers['r0'], trace
        else: raise ValueError('unsupported instruction: '+op)
        pc = next_pc
    raise ValueError('execution bound exceeded')

