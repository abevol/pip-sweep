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
        kept_names = [pkg for pkg, _ in kept]
        self.assertIn('pip', kept_names)

if __name__ == '__main__':
    unittest.main()