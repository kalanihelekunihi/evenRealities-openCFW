# SPDX-License-Identifier: MIT
"""Prove entry-reachable decoded fill instructions remain within their bodies."""
import json
import subprocess
from build_gx8002_backup_memset import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def walk(code, start, end):
    ordinary = {'zextb', 'mov', 'andi', 'st.b', 'st.w', 'stbi.w',
                'subi', 'addi', 'lsli', 'or', 'addu', 'cmplti', 'cmpnei'}
    conditional = {'bez', 'bnez', 'bt', 'bf'}
    pending = [start]
    seen = set()
    returns = set()
    edges = []
    while pending:
        pc = pending.pop()
        if pc in seen:
            continue
        assert start <= pc < end and pc in code, 'edge outside decoded body'
        op, args, width = code[pc]
        assert width in (2, 4) and pc + width <= end
        seen.add(pc)
        if op == 'rts':
            returns.add(pc)
            continue
        if op == 'br' or op in conditional:
            successors = [int(args.split(',')[-1].strip(), 0)]
            if op in conditional:
                successors.append(pc + width)
        else:
            assert op in ordinary, ('unmodeled control effect', op)
            successors = [pc + width]
        for target in successors:
            edges.append([pc, target])
            pending.append(target)
    assert returns
    return {'reachable_instructions': len(seen), 'return_addresses': sorted(returns),
            'edges': sorted(edges)}


def verify():
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    stock_path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    candidate_path = ROOT / 'build/gx8002-backup-memset/memset-candidate.elf'
    stock_elf = Elf32(stock_path.read_bytes(), str(stock_path))
    assert stock_elf.contents(next(s for s in stock_elf.sections if s['name'] == '.data')) == stock
    candidate = Elf32(candidate_path.read_bytes(), str(candidate_path))
    section = next(s for s in candidate.sections if s['name'] == '.text')
    assert section['address'] == 0x100113c4 and section['size'] <= 160
    rows = []
    decoded = []
    for path, start, end in ((stock_path, 0x49d04, 0x49da4),
                             (candidate_path, section['address'], section['address'] + section['size'])):
        text = subprocess.check_output([
            str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'),
            '-D', '--start-address=' + hex(start), '--stop-address=' + hex(end), str(path)
        ], text=True)
        code = decode(text)
        rows.append(walk(code, start, end))
        decoded.append((code, start, end))
    # Ensure this gate rejects escaping branches and indirect jumps, rather
    # than merely accepting the two current binaries.
    rejected = 0
    code, start, end = decoded[1]
    for instruction in (('br', hex(end), 2), ('jmp', 'r3', 2),
                        ('br', hex(start + 1), 2)):
        changed = dict(code)
        changed[start] = instruction
        try:
            walk(changed, start, end)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError('negative control accepted')
    return {'image_sha256': IMAGE_SHA,
            'compiled_sha256': sha(candidate.contents(section)),
            'stock': rows[0], 'candidate': rows[1], 'negative_controls_rejected': rejected,
            'source_admitted': False,
            'limits': ['All decoded paths from each function entry stay in its body or return; termination is not asserted.',
                       'Does not exclude external indirect entry, interrupts modifying PC, or preceding-code fallthrough.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-memset-control-flow.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print('Backup memset control flow:', result['stock']['reachable_instructions'],
          result['candidate']['reachable_instructions'], 'instructions;',
          result['negative_controls_rejected'], 'negative controls rejected')
