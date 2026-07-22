import unittest

from clusterduck.core.bindings import Environment
from clusterduck.core.settings import Settings
from clusterduck.core.var_t import Var_t


class VarTests(unittest.TestCase):
    def test_supported_sweep_inputs(self):
        self.assertEqual(Var_t("scalar", 2).sweep, [2])
        self.assertEqual(Var_t("text", "benzene").sweep, ["benzene"])
        self.assertEqual(Var_t("integer_range", (1, 5, 2)).sweep, [1, 3, 5])
        self.assertEqual(Var_t("descending", (3, 1, -1)).sweep, [3, 2, 1])
        self.assertEqual(Var_t("float_range", (0.1, 0.3, 0.1)).sweep, [0.1, 0.2, 0.3])

    def test_invalid_sweeps_are_rejected(self):
        with self.assertRaises(ValueError):
            Var_t("bad-name", [1])
        with self.assertRaises(ValueError):
            Var_t("empty", [])
        with self.assertRaises(ValueError):
            Var_t("zero_step", (1, 2, 0))
        with self.assertRaises(ValueError):
            Var_t("wrong_direction", (1, 2, -1))
        with self.assertRaises(ValueError):
            Var_t("newline", ["not\nvalid"])

    def test_task_count_does_not_require_config_materialization(self):
        settings = Settings()
        settings.add_vars("a", [1, 2, 3])
        settings.add_vars("b", range(4))
        self.assertEqual(settings.task_count, 12)

    def test_duplicate_parameter_is_rejected(self):
        settings = Settings()
        settings.add_vars("method", ["a"])
        with self.assertRaises(ValueError):
            settings.add_vars("method", ["b"])

    def test_reserved_sbatch_options_are_rejected(self):
        settings = Settings()
        with self.assertRaises(ValueError):
            settings.add("array", "0-10")

    def test_environment_variable_is_validated(self):
        Environment("OMP_NUM_THREADS")
        with self.assertRaises(ValueError):
            Environment("NOT-VALID")


if __name__ == "__main__":
    unittest.main()
