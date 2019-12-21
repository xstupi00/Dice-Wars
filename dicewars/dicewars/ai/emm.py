import logging
import copy

from dicewars.ai.utils import possible_attacks, probability_of_successful_attack, probability_of_holding_area
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:
    """ Expected Mini-Max
    """

    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.players_order = players_order
        self.logger = logging.getLogger('AI')

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        EVAL_WEIGHT = 900
        SUCC_WEIGHT = 2 / 6
        HOLD_WEIGHT = 1 / 6
        ATTACK_TRESHOLD = 2

        max_win_value = -1000
        current_state_evaluation = self.evaluate(board, self.player_name)
        self.logger.debug("current_state_evaluation = " + str(current_state_evaluation))

        best_source = 0
        best_target = 0

        for source, target in possible_attacks(board, self.player_name):
            self.logger.debug("I'm in the loop")
            win_board = copy.deepcopy(board)

            win_board.areas[str(target.get_name())].set_owner(self.player_name)
            win_board.areas[str(target.get_name())].set_dice(win_board.areas[str(source.get_name())].get_dice() - 1)
            win_board.areas[str(source.get_name())].set_dice(1)

            lose_board = copy.deepcopy(board)
            lose_board.areas[str(source.get_name())].set_dice(1)

            successful_attack_probability = probability_of_successful_attack(
                board, source.get_name(), target.get_name()
            )
            holding_attack_area_probability = probability_of_holding_area(
                board, target.get_name(), win_board.areas[str(target.get_name())].get_dice(), self.player_name
            )

            win_board_evaluation = self.evaluate(win_board, self.player_name)
            lose_board_evaluation = self.evaluate(lose_board, self.player_name)

            win_value = EVAL_WEIGHT * win_board_evaluation + SUCC_WEIGHT * successful_attack_probability + \
                        HOLD_WEIGHT * holding_attack_area_probability

            holding_source_probability = probability_of_holding_area(
                board, source.get_name(), lose_board.areas[str(source.get_name())].get_dice(), self.player_name
            )

            lose_value = EVAL_WEIGHT * lose_board_evaluation + SUCC_WEIGHT * (1 - successful_attack_probability) + \
                         HOLD_WEIGHT * holding_source_probability

            if max(lose_value, win_value) > max_win_value:
                max_win_value = max(lose_value, win_value)
                best_source = source
                best_target = target

            self.logger.debug("source = " + str(source.get_name()) + ", " + str(source.get_dice()))
            self.logger.debug("target = " + str(target.get_name()) + ", " + str(target.get_dice()))
            self.logger.debug("win_value = " + str(win_value))

        if max_win_value > ATTACK_TRESHOLD:
            self.logger.debug("best_source = " + str(best_source.get_name()) + ", " + str(best_source.get_dice()))
            self.logger.debug("best_target = " + str(best_target.get_name()) + ", " + str(best_target.get_dice()))
            self.logger.debug("max_win_value = " + str(max_win_value))
            return BattleCommand(best_source.get_name(), best_target.get_name())

        return EndTurnCommand()

    def evaluate(self, board, player_name):
        """ Evaluate the state of the game from the player perspective
        """
        SCORE_WEIGHT = 2
        DICES_WEIGHT = 1

        max_score = len(board.areas)
        self.logger.debug("max_score = " + str(max_score))

        total_dices = sum([board.get_player_dice(player) for player in self.players_order])
        self.logger.debug("total_dices = " + str(total_dices))

        player_dices = board.get_player_dice(player_name)
        self.logger.debug("dices = " + str(player_dices))

        player_score = self.get_score_by_player(board, self.player_name)
        self.logger.debug("score = " + str(player_score))

        enemies = {}
        for enemy in self.players_order:
            if enemy != player_name:
                score = self.get_score_by_player(board, enemy)
                dices = board.get_player_dice(enemy)
                enemies[enemy] = {"score": score, "dices": dices}

        enemies_score = sum(enemy["score"] for enemy in enemies.values())
        enemies_dices = sum(enemy["dices"] for enemy in enemies.values())

        self.logger.debug("enemies_score = " + str(enemies_score))
        self.logger.debug("enemies_dices = " + str(enemies_dices))

        evaluation = SCORE_WEIGHT * (player_score / max_score) + DICES_WEIGHT * (player_dices / total_dices) - \
                     SCORE_WEIGHT * (enemies_score / max_score) - DICES_WEIGHT * (enemies_dices / total_dices)

        max_evaluation = SCORE_WEIGHT * max_score + DICES_WEIGHT * 8 * max_score

        return evaluation / max_evaluation

    def get_score_by_player(self, board, player_name, skip_area=None):
        """Get score of the player in the board
        """
        players_regions = board.get_players_regions(player_name, skip_area=skip_area)
        max_region_size = max(len(region) for region in players_regions)

        return max_region_size
