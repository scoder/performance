#!/usr/bin/env python3
import io
import os.path
import subprocess
import sys
import tempfile
import textwrap
import unittest


DATA_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), 'data'))


def run_cmd(cmd):
    print("Execute: %s" % ' '.join(cmd))
    proc = subprocess.Popen(cmd)
    try:
        proc.wait()
    except:
        proc.kill()
        proc.wait()
        raise

    exitcode = proc.returncode
    if exitcode:
        sys.exit(exitcode)


class CompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cmd = [sys.executable, '-m', 'performance', 'venv', 'create']
        run_cmd(cmd)

    def compare(self, *args):
        cmd = [sys.executable, '-m', 'performance', 'compare',
               os.path.join(DATA_DIR, 'py2.json'),
               os.path.join(DATA_DIR, 'py3.json')]
        cmd.extend(args)
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
        return proc.communicate()[0]

    def test_compare(self):
        stdout = self.compare()
        self.assertEqual(stdout, textwrap.dedent('''
            ### call_simple ###
            Median +- Std dev: 11.4 ms +- 2.1 ms -> 13.6 ms +- 1.3 ms: 1.19x slower
            Significant (t=-3.38)

        '''))

    def test_csv(self):
        with tempfile.NamedTemporaryFile("w") as tmp:
            stdout = self.compare("--csv", tmp.name)

            with io.open(tmp.name, "r") as fp:
                csv = fp.read()

            self.assertEqual(csv, textwrap.dedent('''
                Benchmark,Base,Changed
                call_simple,0.011193,0.013267
            ''').lstrip())

    def test_compare_table(self):
        stdout = self.compare("-O", "table")
        self.assertEqual(stdout, textwrap.dedent('''
            +-------------+----------+----------+--------------+-----------------------+
            | Benchmark   | py2.json | py3.json | Change       | Significance          |
            +=============+==========+==========+==============+=======================+
            | call_simple | 0.01     | 0.01     | 1.19x slower | Significant (t=-3.38) |
            +-------------+----------+----------+--------------+-----------------------+
        ''').lstrip())


if __name__ == "__main__":
    unittest.main()
