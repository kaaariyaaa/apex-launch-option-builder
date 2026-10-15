import unittest
from pathlib import Path
from runpy import run_path

module = run_path(str(Path(__file__).with_name('prepare-data.py')))
build, read = module['build'], module['read']


class CatalogTest(unittest.TestCase):
    def test_supplied_catalog(self):
        options = build(read('all.csv'), read('candidates.csv'))
        self.assertEqual(len(options), 4042)
        self.assertEqual(sum(option['candidate'] for option in options), 330)
        self.assertEqual(sum(option['registrations'] for option in options), 4114)
        self.assertEqual(len({option['id'] for option in options}), len(options))
        by_name = {option['name']: option for option in options}
        self.assertTrue(by_name['+fps_max']['candidate'])
        self.assertEqual(by_name['+fps_max']['example'], '+fps_max 200')
        self.assertEqual(by_name['+fps_max']['default'], '-1')
        self.assertEqual(by_name['-dev']['format'], '-dev')
        self.assertEqual(by_name['-affinity=']['format'], '-affinity={value}')
        self.assertTrue(by_name['+break']['uncertain'])
        self.assertEqual(by_name['+ssao_downsample_scale']['default'], '')
        self.assertEqual(by_name['+ssao_downsample_scale']['defaults'], ['1.f'])
        for name in ('+party_privacy', '-eac_launcher_settings'):
            self.assertEqual(by_name[name]['default'], '')
            self.assertTrue(by_name[name]['defaults'][0].startswith('不明'))
        self.assertTrue(all(not option['cfg'] for option in options))
        for option in options:
            if len(option['defaults']) > 1:
                self.assertEqual(option['default'], '')

    def test_conflicting_defaults_are_preserved(self):
        row = next(row for row in read('all.csv') if row['起動オプション'] == '+fps_max')
        duplicate = dict(row, デフォルト値='120')
        option, = build([row, duplicate], read('candidates.csv')[:1])
        self.assertEqual(option['defaults'], ['-1', '120'])
        self.assertEqual(option['default'], '')
        self.assertEqual(option['registrations'], 2)

    def test_invalid_or_missing_names_fail(self):
        row = read('all.csv')[0]
        with self.assertRaises(ValueError):
            build([dict(row, 起動オプション='bad name')], [])
        with self.assertRaises(ValueError):
            build([], read('candidates.csv'))


if __name__ == '__main__':
    unittest.main()
