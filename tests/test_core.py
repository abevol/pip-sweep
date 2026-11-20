import unittest
from unittest.mock import patch, MagicMock
from pip_sweep.core import DependencySweeper

class MockDistribution:
    def __init__(self, name, requires=None):
        self.name = name
        self.requires = requires or []

class TestDependencySweeper(unittest.TestCase):

    @patch('importlib.metadata.distributions')
    def test_basic_sweep(self, mock_dists):
        # 拓扑：a -> [b, c], c -> d
        mock_dists.return_value = [
            MockDistribution('a', ['b', 'c']),
            MockDistribution('b', []),
            MockDistribution('c', ['d']),
            MockDistribution('d', []),
            MockDistribution('pip', []),
        ]
        
        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()
        
        to_uninstall, kept = sweeper.find_garbage(['a'])
        self.assertEqual(set(to_uninstall), {'a', 'b', 'c', 'd'})

    @patch('importlib.metadata.distributions')
    def test_external_dependency_protection(self, mock_dists):
        # 拓扑：a -> [b, c], e -> c
        mock_dists.return_value = [
            MockDistribution('a', ['b', 'c']),
            MockDistribution('b', []),
            MockDistribution('c', []),
            MockDistribution('e', ['c']),
        ]
        
        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()
        
        to_uninstall, kept = sweeper.find_garbage(['a'])
        # c 应该被保留，因为被外部 e 依赖；b 被清理
        self.assertIn('a', to_uninstall)
        self.assertIn('b', to_uninstall)
        self.assertNotIn('c', to_uninstall)

    @patch('importlib.metadata.distributions')
    def test_circular_dependency(self, mock_dists):
        # 拓扑：a -> b, b -> c, c -> a
        mock_dists.return_value = [
            MockDistribution('a', ['b']),
            MockDistribution('b', ['c']),
            MockDistribution('c', ['a']),
        ]
        
        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()
        
        to_uninstall, kept = sweeper.find_garbage(['a'])
        self.assertEqual(set(to_uninstall), {'a', 'b', 'c'})

    @patch('importlib.metadata.distributions')
    def test_core_package_protection(self, mock_dists):
        # a -> pip
        mock_dists.return_value = [
            MockDistribution('a', ['pip']),
            MockDistribution('pip', []),
        ]
        
        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()
        
        to_uninstall, kept = sweeper.find_garbage(['a'])
        self.assertEqual(set(to_uninstall), {'a'})
        # pip 应该被保留
        kept_names = [pkg for pkg, _, _ in kept]
        self.assertIn('pip', kept_names)

    @patch('importlib.metadata.distributions')
    def test_exclude_keeps_package_and_its_subtree(self, mock_dists):
        # 拓扑：a -> [b, c], c -> d
        mock_dists.return_value = [
            MockDistribution('a', ['b', 'c']),
            MockDistribution('b', []),
            MockDistribution('c', ['d']),
            MockDistribution('d', []),
        ]

        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()

        # 保留 c，则 c 及其依赖 d 都应存活
        to_uninstall, kept = sweeper.find_garbage(['a'], exclude=['c'])
        self.assertEqual(set(to_uninstall), {'a', 'b'})
        self.assertNotIn('c', to_uninstall)
        self.assertNotIn('d', to_uninstall)

        kept_reasons = {pkg.lower(): reason for pkg, reason, _ in kept}
        self.assertEqual(kept_reasons.get('c'), 'user_excluded')

    @patch('importlib.metadata.distributions')
    def test_exclude_normalizes_names(self, mock_dists):
        # 用下划线/大写形式的排除名也应生效
        mock_dists.return_value = [
            MockDistribution('a', ['JSONPath_NG']),
            MockDistribution('jsonpath-ng', []),
        ]

        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()

        to_uninstall, _ = sweeper.find_garbage(['a'], exclude=['jsonpath_ng'])
        self.assertEqual(set(to_uninstall), {'a'})

    @patch('importlib.metadata.distributions')
    def test_exclude_not_installed_is_ignored(self, mock_dists):
        mock_dists.return_value = [
            MockDistribution('a', ['b']),
            MockDistribution('b', []),
        ]

        sweeper = DependencySweeper()
        sweeper.build_dependency_graph()

        to_uninstall, _ = sweeper.find_garbage(['a'], exclude=['ghost'])
        self.assertEqual(set(to_uninstall), {'a', 'b'})

if __name__ == '__main__':
    unittest.main()
