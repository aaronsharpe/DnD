"""
Dnd_melee_accack is for performing melee attacks in DnD as well as returning
statistics for given melee attack input parameters
"""

import numpy as np

def melee_attack(armor_class, hit_die=6, num_hit_dice=1, to_hit_mod=0, mod=0,
                 bonus_crit_dice=0, advantage=False, disadvantage=False,
                 crit_19=False, reroll=False, gwm=False):
    """
    Check to see if a melee attack against a given armor_class will hit then
    perform the attack

    Arguments:
        armor_class: armor class to check hit against
        hit_die: the size of the damage die that will be rolled
        num_hit_dice: the number of hit die that will be rolled for damage
        to_hit_mod: added modifier when making attacks
        mod: added modifier to damage
        bonus_crit_die: additional hit dice awarded on a critical hit
        advantage: roll to hit twice and take the max result
        disadvantage: roll to hit twice and take the min result
        crit_19: A to hit roll of 19 counts as a critical
        reroll: When rolling damage, reroll 1's and 2's once
        gwm: incorperates great weapon master feat, -5 to hit and +10 to dmg
    """

    to_hit = roll_to_hit(armor_class, to_hit_mod=to_hit_mod,
                         advantage=advantage, disadvantage=disadvantage,
                         crit_19=crit_19, gwm=gwm)

    attack = roll_dmg(to_hit=to_hit['to_hit_dice'], hit=to_hit['hit'],
                      crit=to_hit['crit'], hit_die=hit_die,
                      num_hit_dice=num_hit_dice, mod=mod,
                      bonus_crit_dice=bonus_crit_dice, reroll=reroll, gwm=gwm)

    return attack


def roll_to_hit(armor_class, to_hit_mod=0, advantage=False, disadvantage=False,
                crit_19=False, gwm=False):
    """
    Check to see if a melee attack against a given armor_class will hit
    """

    hit_roll = dict()

    if advantage:
        to_hit_dice = np.random.randint(1, 21, size=2)
        to_hit = np.max(to_hit_dice)
    elif disadvantage:
        to_hit_dice = np.random.randint(1, 21, size=2)
        to_hit = np.min(to_hit_dice)
    else:
        to_hit_dice = np.random.randint(1, 21)
        to_hit = to_hit_dice

    hit_roll['to_hit_dice'] = to_hit_dice
    hit_roll['to_hit_mod'] = to_hit_mod

    if to_hit == 20 or (to_hit == 19 and crit_19):
        hit_roll['hit'] = True
        hit_roll['crit'] = True

    elif to_hit == 1:
        hit_roll['hit'] = False
        hit_roll['crit'] = False

    else:
        hit_roll['hit'] = to_hit + to_hit_mod - (5 if gwm else 0) >= armor_class
        hit_roll['crit'] = False

    return hit_roll


def roll_dmg(to_hit=None, hit=False, crit=False, hit_die=6, num_hit_dice=1,
             mod=0, bonus_crit_dice=0, reroll=False, gwm=False):
    """
    Function to roll damage on a succesful hit
    """

    attack = dict()

    # If no hit info is provided, will generate a generic attack
    if to_hit is None:
        attack['to_hit_dice'] = np.random.randint(1, 21, size=2)
        hit = True
        crit = True
    else:
        attack['to_hit_dice'] = to_hit

    attack['rolled_hit_dice'] = []
    attack['hit'] = hit
    attack['crit'] = crit
    attack['mod'] = mod
    attack['bonus_crit_dice'] = bonus_crit_dice
    attack['reroll'] = reroll
    attack['gwm'] = gwm

    if crit:
        attack['rolled_hit_dice'] = np.random.randint(1, hit_die + 1, size=
                                                      2*num_hit_dice +
                                                      bonus_crit_dice)
    elif hit:
        attack['rolled_hit_dice'] = np.random.randint(1, hit_die + 1, size=
                                                      num_hit_dice)

    # For great weapon fighter, reroll any 1's and 2's
    if attack['hit'] and reroll:
        for i, die in enumerate(attack['rolled_hit_dice']):
            if die <= 2:
                attack['rolled_hit_dice'][i] = np.random.randint(1, hit_die + 1)

    attack['dmg'] = np.sum(attack['rolled_hit_dice'])

    if attack['hit']:
        attack['dmg'] += mod

    if gwm and attack['hit']:
        attack['dmg'] += 10

    return attack


def melee_stats(iters, armor_class, ci=10, num_attacks=1, hit_die=6, num_hit_dice=1,
                mod=0, bonus_crit_dice=0, advantage=False,
                disadvantage=False,
                crit_19=False, reroll=False, gwm=False):
    """
    Returns statistics a melee attack against a given armor class

    Arguments:
        iters: numbers of times to try attacking armor_class
        ci: confidence interval for computing statistics
        num_attacks: number of times each attack is performed
    """

    attack_stats = dict()

    hit_store = np.empty(iters)
    crit_store = np.empty(iters)
    hit_dice = np.empty(iters)
    dmg_store = np.empty(iters)
    for i in range(iters):
        attack = melee_attack(armor_class, hit_die=hit_die,
                              num_hit_dice=num_hit_dice, mod=mod,
                              bonus_crit_dice=bonus_crit_dice,
                              advantage=advantage,
                              disadvantage=disadvantage, crit_19=crit_19,
                              reroll=reroll, gwm=gwm)

        hit_store[i] = attack['hit']
        crit_store[i] = attack['crit']
        dmg_store[i] = attack['dmg']

        if advantage:
            hit_dice[i] = np.max(attack['to_hit_dice'])
        elif disadvantage:
            hit_dice[i] = np.min(attack['to_hit_dice'])
        else:
            hit_dice[i] = attack['to_hit_dice']

    attack_stats['hit_chance'] = sum(hit_store)/len(hit_store)
    attack_stats['crit_chance'] = sum(crit_store)/len(crit_store)
    attack_stats['dmg_mean'] = num_attacks * np.mean(dmg_store)

    # resample for generating confidence interval
    dmg_per_round = dmg_store.copy()
    for _ in range(num_attacks-1):
        dmg_per_round += np.random.choice(dmg_store, iters)

    attack_stats['dmg_per_round'] = dmg_per_round
    attack_stats['dmg_ci_lo'] = np.percentile(dmg_per_round, ci)
    attack_stats['dmg_ci_hi'] = np.percentile(dmg_per_round, 100 - ci)

    return attack_stats


def melee_vs_ac(iters, armor_classes, ci=10, num_attacks=1, hit_die=6,
                      num_hit_dice=1, mod=0, bonus_crit_dice=0,
                      advantage=False, disadvantage=False,
                      crit_19=False, reroll=False, gwm=False):
    """
    Computes statistics for a series of armor_classes
    """
    attack_stats_vs_ac = dict()
    attack_stats_vs_ac['hit_chance'] = []
    attack_stats_vs_ac['crit_chance'] = []
    attack_stats_vs_ac['dmg_mean'] = []
    attack_stats_vs_ac['dmg_ci_lo'] = []
    attack_stats_vs_ac['dmg_ci_hi'] = []
    attack_stats_vs_ac['dmg_per_round'] = np.empty([len(armor_classes), iters])

    for i, armor_class in enumerate(armor_classes):
        attack_stats = melee_stats(iters, armor_class, ci=ci,
                                   num_attacks=num_attacks, hit_die=hit_die,
                                   num_hit_dice=num_hit_dice, mod=mod,
                                   bonus_crit_dice=bonus_crit_dice,
                                   advantage=advantage,
                                   disadvantage=disadvantage,
                                   crit_19=crit_19, reroll=reroll,
                                   gwm=gwm)

        attack_stats_vs_ac['hit_chance'].append(attack_stats['hit_chance'])
        attack_stats_vs_ac['crit_chance'].append(attack_stats['crit_chance'])
        attack_stats_vs_ac['dmg_mean'].append(attack_stats['dmg_mean'])
        attack_stats_vs_ac['dmg_ci_lo'].append(attack_stats['dmg_ci_lo'])
        attack_stats_vs_ac['dmg_ci_hi'].append(attack_stats['dmg_ci_hi'])
        attack_stats_vs_ac['dmg_per_round'][i,:] = attack_stats['dmg_per_round']

    return attack_stats_vs_ac
