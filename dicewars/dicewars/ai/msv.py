import logging
import copy
import math
import random

from dicewars.ai.utils import possible_attacks, probability_of_successful_attack, probability_of_holding_area
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:

    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.players_order = players_order
        self.logger = logging.getLogger('AI')

        # ATTACK_WEIGHT in (0.8, 0.2)
        # y = 0.2 + 0.6 * (1 - sqrt(x/6 - 2/6))
        self.ATTACK_WEIGHT = {2: 0.8, 3: 0.56, 4: 0.45, 5: 0.45, 6: 0.45, 7: 0.45, 8: 0.45}

        # ATTACK HOLD THRESHOLD MEAN in (0.125, 0.485)
        # y = 0.06 * x + 0.005
        self.ATTACK_HOLD_THRESHOLD_MEAN = {2: 0.125, 3: 0.185, 4: 0.245, 5: 0.245, 6: 0.245, 7: 0.245, 8: 0.245}

        # DIFF_WIN_THRESHOLD_MEAN
        self.DIFF_WIN_THRESHOLD_MEAN = 0.00175

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        return self.get_command(board)

    def get_command(self, board):
        alive_players = self.get_alive_players(board)

        ATTACK_HOLD_THRESHOLD = random.uniform(self.ATTACK_HOLD_THRESHOLD_MEAN[alive_players] - 0.025,
                                               self.ATTACK_HOLD_THRESHOLD_MEAN[alive_players] + 0.025)
        DIFF_EVAL_THRESHOLD = random.uniform(self.DIFF_WIN_THRESHOLD_MEAN - 0.0005,
                                             self.DIFF_WIN_THRESHOLD_MEAN + 0.0005)
        WIN_COEFF_THRESHOLD = random.uniform(self.ATTACK_HOLD_THRESHOLD_MEAN[alive_players] - 0.025,
                                             self.ATTACK_HOLD_THRESHOLD_MEAN[alive_players] + 0.025)
        HOLD_SOURCE_WEIGHT = 1 / 3 * (1 - self.ATTACK_WEIGHT[alive_players])
        HOLD_TARGET_WEIGHT = 2 / 3 * (1 - self.ATTACK_WEIGHT[alive_players])

        # ATTACK_HOLD_WEIGHT in (0.5, 0.75)
        ATTACK_HOLD_WEIGHT = 0.75 - self.get_aggresivity(alive_players) * 0.25
        DIFF_WIN_WEIGHT = (1 - ATTACK_HOLD_WEIGHT) / 2
        DIFF_LOSE_WEIGHT = (1 - ATTACK_HOLD_WEIGHT) / 4
        LOSE_HOLD_WEIGHT = (1 - ATTACK_HOLD_WEIGHT) / 4

        attack_hold_prob = []
        diff_eval_win = []
        diff_eval_lose = []
        lose_hold_prob = []

        current_eval = self.evaluate(board, self.player_name)

        for source, target in possible_attacks(board, self.player_name):
            win_board = copy.deepcopy(board)
            lose_board = copy.deepcopy(board)

            target_name_str = str(target.get_name())
            target_name_int = target.get_name()
            source_name_str = str(source.get_name())
            source_name_int = source.get_name()

            win_board.areas[target_name_str].set_owner(self.player_name)
            win_board.areas[target_name_str].set_dice(win_board.areas[source_name_str].get_dice() - 1)
            win_board.areas[source_name_str].set_dice(1)
            lose_board.areas[source_name_str].set_dice(1)

            # 1) attack_hold_prob
            attack_prob = probability_of_successful_attack(board, source_name_int, target_name_int)

            # We don't want to consider attacks with chance of successful under 20%
            if attack_prob < 0.2:
                continue

            hold_target_prob = probability_of_holding_area(
                win_board, target_name_int, win_board.areas[target_name_str].get_dice(), self.player_name
            )
            hold_source_prob = probability_of_holding_area(
                win_board, source_name_int, win_board.areas[source_name_str].get_dice(), self.player_name
            )
            attack_hold_coeff = (self.ATTACK_WEIGHT[alive_players] * attack_prob + HOLD_TARGET_WEIGHT * hold_target_prob
                                 + HOLD_SOURCE_WEIGHT * hold_source_prob) / 3

            # 2) diff_eval_win
            win_eval = self.evaluate(win_board, self.player_name)
            diff_eval_win_coeff = win_eval - current_eval

            good_action = False

            # The treshhold of good / not good attacks
            if alive_players == 2:
                if attack_hold_coeff > WIN_COEFF_THRESHOLD or attack_prob > 0.95:
                    good_action = True
            else:
                if (attack_hold_coeff > ATTACK_HOLD_THRESHOLD / 2 and diff_eval_win_coeff > 2 * DIFF_EVAL_THRESHOLD)\
                   or (attack_hold_coeff > ATTACK_HOLD_THRESHOLD and diff_eval_win_coeff > DIFF_EVAL_THRESHOLD)\
                   or attack_prob > 0.975\
                   or self.check_next_turn(win_board, target, hold_target_prob):
                    good_action = True

            if good_action:
                rank = 0
                if self.check_next_turn(win_board, target, hold_target_prob):
                    rank = 2

                attack_hold_prob.append((source_name_int, target_name_int, attack_hold_coeff*rank))
                diff_eval_win.append((source_name_int, target_name_int, diff_eval_win_coeff*rank))

                # 3) diff_eval_lose
                lose_eval = self.evaluate(lose_board, self.player_name)
                diff_eval_lose_coeff = lose_eval - current_eval
                diff_eval_lose.append((source_name_int, target_name_int, diff_eval_lose_coeff*rank))

                # 4) lose_hold_prob
                lose_hold_prob_coeff = probability_of_holding_area(
                    lose_board, source_name_int, lose_board.areas[source_name_str].get_dice(), self.player_name
                )
                lose_hold_prob.append((source_name_int, target_name_int, lose_hold_prob_coeff*rank))

        # # Sorting lists
        # attack_hold_prob.sort(key=lambda tup: tup[2])
        # diff_eval_win.sort(key=lambda tup: tup[2])
        # diff_eval_lose.sort(key=lambda tup: tup[2])
        # lose_hold_prob.sort(key=lambda tup: tup[2])

        # List with possible actions
        possible_actions = []

        for source, target, attack_hold_coeff in attack_hold_prob:
            diff_win_coeff = [tup for tup in diff_eval_win if tup[0] == source and tup[1] == target][0][2]
            diff_lose_coeff = [tup for tup in diff_eval_lose if tup[0] == source and tup[1] == target][0][2]
            lose_hold_coeff = [tup for tup in lose_hold_prob if tup[0] == source and tup[1] == target][0][2]
            action_coeff = (ATTACK_HOLD_WEIGHT * attack_hold_coeff + DIFF_WIN_WEIGHT * diff_win_coeff +
                            DIFF_LOSE_WEIGHT * diff_lose_coeff + LOSE_HOLD_WEIGHT * lose_hold_coeff) / 4
            possible_actions.append((source, target, action_coeff))

        possible_actions.sort(key=lambda tup: tup[2])

        if possible_actions:
            return BattleCommand(possible_actions[0][0], possible_actions[0][1])
        else:
            return EndTurnCommand()

    def evaluate(self, board, player_name):
        """ Evaluate the state of the game from the player perspective
        """
        SCORE_WEIGHT = 9 / 10
        DICES_WEIGHT = 1 / 10

        max_score = len(board.areas)
        total_dices = sum([board.get_player_dice(player) for player in self.players_order])
        player_dices = board.get_player_dice(player_name)
        player_score = self.get_score_by_player(board, self.player_name)

        enemies = {}
        for enemy in self.players_order:
            if enemy != player_name:
                score = self.get_score_by_player(board, enemy)
                dices = board.get_player_dice(enemy)
                enemies[enemy] = {"score": score, "dices": dices}

        enemies_score = sum(enemy["score"] for enemy in enemies.values())
        enemies_dices = sum(enemy["dices"] for enemy in enemies.values())

        # me:    y = sqrt(x/n)
        # enemy: y = 1 - sqrt(x/n)

        if self.get_alive_players(board) == 2:
            evaluation = (SCORE_WEIGHT / 2 * math.sqrt((player_score / max_score) / max_score) +
                          DICES_WEIGHT / 2 * math.sqrt((player_dices / total_dices) / 8 * max_score) +
                          SCORE_WEIGHT / 2 * (1 - math.sqrt((enemies_score / max_score) / max_score)) +
                          DICES_WEIGHT / 2 * (1 - math.sqrt((enemies_dices / total_dices) / 8 * max_score))) / 4
        else:
            evaluation = (SCORE_WEIGHT * math.sqrt((player_score / max_score) / max_score) +
                          DICES_WEIGHT * math.sqrt((player_dices / total_dices) / 8 * max_score)) / 2

        return evaluation

    def check_next_turn(self, win_board, target, hold_prob):
        # neighbours of current target area
        if win_board.areas[str(target.get_name())].can_attack():
            for neighbour in target.get_adjacent_areas():
                neighbour = win_board.get_area(neighbour)
                # if neighbour of current target is not my area
                if neighbour.get_owner_name() != self.player_name and \
                        probability_of_successful_attack(win_board, target.get_name(), neighbour.get_name()) > 0.2:
                    # check whether the neighbour has neighbour which is in the my largest current region
                    for potential_target in neighbour.get_adjacent_areas():
                        if potential_target in self.get_largest_region(win_board) and hold_prob == 1.0:
                            return True
        return False

    @staticmethod
    def get_alive_players(board):
        enemies_alive = set()
        [enemies_alive.add(area.owner_name) for area in board.areas.values()]
        return len(enemies_alive)

    @staticmethod
    def get_aggresivity(alive_players):
        # y = 1 - sqrt(x/6 - 2/6)
        # return number in (1, 0)
        return 1 - math.sqrt(alive_players / 6 - 2 / 6)

    @staticmethod
    def get_score_by_player(board, player_name, skip_area=None):
        """Get score of the player in the board
        """
        players_regions = board.get_players_regions(player_name, skip_area=skip_area)
        max_region_size = max(len(region) for region in players_regions)
        return max_region_size

    def get_largest_region(self, board):
        players_regions = board.get_players_regions(self.player_name)
        max_region_size = max(len(region) for region in players_regions)
        max_sized_regions = [region for region in players_regions if len(region) == max_region_size]
        return max_sized_regions[0]
