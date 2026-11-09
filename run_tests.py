"""No pytest dependency required for the bundled physics tests."""
import unittest
from pathlib import Path
from threadpoolctl import threadpool_limits
with threadpool_limits(limits=1):
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent/'tests'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
