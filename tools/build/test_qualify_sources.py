"""Native binding knowledge is independent of available compiled providers."""
import unittest
from collections import defaultdict
from qualify_sources import add_r1_frontier_bindings


class FrontierBindingTests(unittest.TestCase):
    def bind(self, rows):
        symbols = defaultdict(lambda: defaultdict(set))
        entries = defaultdict(set)
        add_r1_frontier_bindings(symbols, entries, rows, 0x1000)
        return symbols, entries

    def test_unimplemented_entry_can_bind_caller_without_owning_code(self):
        row = dict(image='application', entry='0x00027200', size='0',
                   candidate_symbol='native_service', candidate_sources='',
                   status='unresolved_source_route')
        symbols, entries = self.bind([row])
        self.assertEqual(symbols['r1-application']['native_service'], {0x27201})
        self.assertEqual(entries['r1-application'], {0x27200})
        self.assertEqual(row['candidate_sources'], '')

    def test_duplicate_name_keeps_ambiguity_for_binding_rejection(self):
        rows = [dict(image='application', entry=entry, candidate_symbol='service')
                for entry in ['0x27200', '0x27300']]
        symbols, entries = self.bind(rows)
        self.assertEqual(symbols['r1-application']['service'], {0x27201, 0x27301})
        self.assertEqual(len(entries['r1-application']), 2)

    def test_duplicate_entry_is_not_ambiguous(self):
        row = dict(image='application', entry='0x27200', candidate_symbol='service')
        symbols, _ = self.bind([row, row])
        self.assertEqual(symbols['r1-application']['service'], {0x27201})

    def test_other_images_cannot_supply_application_bindings(self):
        symbols, entries = self.bind([
            dict(image='bootloader', entry='0x27200', candidate_symbol='service')])
        self.assertFalse(dict(symbols))
        self.assertFalse(dict(entries))

    def test_unaligned_out_of_range_and_malformed_entries_are_rejected(self):
        rows = [dict(image='application', entry=entry, candidate_symbol='service')
                for entry in ['0x26ffe', '0x28000', '0x27201', 'invalid', None]]
        rows.append(dict(image='application'))
        symbols, entries = self.bind(rows)
        self.assertFalse(dict(symbols))
        self.assertFalse(dict(entries))

    def test_valid_boundary_entries_and_unnamed_targets(self):
        rows = [dict(image='application', entry=entry, candidate_symbol='')
                for entry in ['0x27000', '0x27ffe']]
        symbols, entries = self.bind(rows)
        self.assertFalse(dict(symbols))
        self.assertEqual(entries['r1-application'], {0x27000, 0x27ffe})


if __name__ == '__main__':
    unittest.main()
