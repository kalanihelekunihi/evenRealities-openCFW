# SPDX-License-Identifier: MIT
import unittest
from tools import model_gx8002_spi_register_master as m


class SPIRegistrationModelTests(unittest.TestCase):
    def test_validation_order(self):
        self.assertEqual(m.expected(m.Case(master=0))[0],[])
        trace,words,result=m.expected(m.Case(selects=0,bus=-1))
        self.assertEqual(trace,[('read32',m.MASTER+4,0)])
        self.assertEqual(result,(-22)&m.MASK)

    def test_append_after_existing(self):
        case=m.Case(old_count=2);trace,words,result=m.expected(case)
        entry=m.MASTER+28;previous=m.OLD+64+28
        self.assertEqual(words[previous],entry)
        self.assertEqual(words[entry+4],previous)
        self.assertEqual(words[m.HEAD+4],entry)

    def test_only_first_eligible_flash(self):
        case=m.Case(flashes=((0,0),(0,0)))
        initial=m.Model(case).words;trace,words,result=m.expected(case)
        self.assertEqual(words[m.FLASH+4],m.MASTER)
        self.assertEqual(words[m.FLASH+64+4],initial[m.FLASH+64+4])

    def test_bus_and_select_filter(self):
        case=m.Case(bus=2,selects=2,flashes=((1,0),(2,2),(2,1)))
        trace,words,result=m.expected(case)
        self.assertEqual([x[1] for x in trace if x[0]=='read8'],[m.FLASH+64+12,m.FLASH+128+12])
        self.assertEqual(words[m.FLASH+128+4],m.MASTER)

    def test_sentinel_next_is_read(self):
        trace,words,result=m.expected(m.Case())
        self.assertEqual(trace[-1],('read32',m.HEAD+8,m.HEAD+8))


if __name__=='__main__':unittest.main()
