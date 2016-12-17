import nose
import angr
import subprocess

import logging
l = logging.getLogger('angr.tests.test_signed_div')

import os
test_location = str(os.path.dirname(os.path.realpath(__file__)))


def run_signed_div():
    test_bin = os.path.join(test_location, "../../binaries/tests/i386/test_signed_div")
    b = angr.Project(test_bin)

    pg = b.factory.path_group()
    pg.explore()
    out_angr = pg.deadended[0].state.posix.dumps(1)
    proc = subprocess.Popen(test_bin, stdout=subprocess.PIPE)
    stdout_real, _ = proc.communicate()

    nose.tools.assert_equal(out_angr, stdout_real)

def test_signed_div():
    yield run_signed_div

if __name__ == "__main__":
    run_signed_div()
