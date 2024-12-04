import unittest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from physics.enemy import EnemyManager, Enemy


class TestEnemyManager(unittest.TestCase):

    def setUp(self):
        """Configura o ambiente de teste"""
        self.enemy_manager = EnemyManager(spawn_interval=1)  # Intervalo de spawn de 1 segundo

    def test_spawn_enemy(self):
        """Testa se o inimigo é gerado corretamente com atributos diferentes"""
        # Gera um inimigo
        self.enemy_manager.spawn_enemy()

        # Verifica se o número de inimigos aumentou
        self.assertEqual(len(self.enemy_manager.enemies), 1)

        # Verifica se o inimigo gerado tem um dano e dano necessário para morrer definidos
        enemy = self.enemy_manager.enemies[0]
        self.assertTrue(hasattr(enemy, "damage"))
        self.assertTrue(hasattr(enemy, "damage_to_die"))

        # Verifica se o dano e o dano necessário para morrer são do tipo esperado
        self.assertIsInstance(enemy.damage, int)
        self.assertIsInstance(enemy.damage_to_die, int)

    def test_enemy_move_towards_player(self):
        """Testa se o inimigo se move (mesmo sem a presença do jogador)"""
        self.enemy_manager.spawn_enemy()
        enemy = self.enemy_manager.enemies[0]

        initial_x = enemy.x
        initial_y = enemy.y

        # Simula a atualização do inimigo (mesmo sem o jogador, ele pode se mover)
        enemy.update(None, dt=1)

        # Verifica se o inimigo se moveu
        self.assertNotEqual(enemy.x, initial_x)
        self.assertNotEqual(enemy.y, initial_y)

    def test_enemy_attack(self):
        """Testa se o inimigo tenta atacar (sem o player)"""
        self.enemy_manager.spawn_enemy()
        enemy = self.enemy_manager.enemies[0]

        initial_health = 100  # Simula a saúde do jogador como 100
        enemy.attack(Mock(health=initial_health))  # Mock do jogador

        # Verifica se o inimigo aplicou dano
        self.assertLess(initial_health, 100)

    def test_enemy_death(self):
        """Testa se o inimigo morre após receber o dano necessário"""
        self.enemy_manager.spawn_enemy()
        enemy = self.enemy_manager.enemies[0]

        # Dá dano ao inimigo até ele morrer
        enemy.health = enemy.damage_to_die
        enemy.update(None, dt=1)

        # Verifica se o inimigo está morto
        self.assertTrue(enemy.is_dead)

    def test_enemy_manager_update(self):
        """Testa se o EnemyManager atualiza corretamente os inimigos"""
        # Gera inimigos
        self.enemy_manager.spawn_enemy()
        self.enemy_manager.spawn_enemy()

        initial_enemy_count = len(self.enemy_manager.enemies)

        # Simula a atualização do EnemyManager (sem o player)
        self.enemy_manager.update(dt=1, player=None)

        # Verifica se o número de inimigos não mudou após a atualização
        self.assertEqual(len(self.enemy_manager.enemies), initial_enemy_count)

    def test_enemy_manager_removes_dead_enemies(self):
        """Testa se o EnemyManager remove inimigos mortos"""
        self.enemy_manager.spawn_enemy()

        # Pega o inimigo recém-criado
        enemy = self.enemy_manager.enemies[0]
        enemy.health = 0  # Simula a morte do inimigo

        # Atualiza o EnemyManager (removerá inimigos mortos)
        self.enemy_manager.update(dt=1, player=None)

        # Verifica se o inimigo foi removido
        self.assertEqual(len(self.enemy_manager.enemies), 0)


if __name__ == '__main__':
    unittest.main()
