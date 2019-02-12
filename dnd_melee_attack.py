import numpy as np


def melee_attack(ac, hit_die = 6, num_hit_dice = 1, mod = 0, 
                bonus_crit_dice = 0, advantage = False, disadvantage = False, 
                crit_19 = False, reroll = False, GWM = False):
    """
    Things to add:
    - crit fail
    """
    
    attack = dict()
    
    if advantage:
        to_hit_dice = np.random.randint(1, 21, size=2)
        to_hit = np.max(to_hit_dice)
    elif disadvantage:
        to_hit_dice = np.random.randint(1, 21, size=2)
        to_hit = np.min(to_hit_dice)
    else:
        to_hit_dice = np.random.randint(1, 21)
        to_hit = to_hit_dice
     
    attack['to_hit_dice'] = to_hit_dice
    crit_check = to_hit # to avoid GWM messing up crits
    
    if GWM:
        to_hit -= 5
    
    attack['hit'] = False
    attack['crit'] = False
    attack['rolled_hit_dice'] = []
    
    if crit_check == 20:
        attack['hit'] = True
        attack['crit'] = True
        attack['rolled_hit_dice'] = np.random.randint(1, hit_die + 1, size = 
                                            2*num_hit_dice + bonus_crit_dice)
    elif crit_19 and crit_check == 19:
        attack['hit'] = True
        attack['crit']= True
        attack['rolled_hit_dice'] = np.random.randint(1, hit_die + 1, size = 
                                            2*num_hit_dice + bonus_crit_dice)
    elif to_hit >= ac:
        attack['hit'] = True
        attack['rolled_hit_dice'] = np.random.randint(1, hit_die + 1, size = 
                                            num_hit_dice)
        
    if attack['hit'] and reroll: # Great weapon fighter
        for i, die in enumerate(attack['rolled_hit_dice']):
            if die <= 2:
                attack['rolled_hit_dice'][i] = np.random.randint(1, hit_die + 1)
                
    attack['dmg']= np.sum(attack['rolled_hit_dice'])
    
    if attack['hit']:
        attack['dmg'] += mod
    
    if GWM and attack['hit']:
        attack['dmg'] += 10
    
    return attack
    
    
def melee_stats(n, ac, ci = 10, num_attacks = 1, hit_die = 6, num_hit_dice = 1, 
                mod = 0, bonus_crit_dice = 0, advantage = False, 
                disadvantage = False, 
                crit_19 = False, reroll = False, GWM = False):
    """

    """
    
    
    attack_stats = dict()
    
    hit_store = []
    crit_store = []
    hit_dice = []
    dmg_store = []
    for i in range(n):
        attack = melee_attack(ac, hit_die = hit_die, 
                              num_hit_dice = num_hit_dice, mod = mod, 
                              bonus_crit_dice = bonus_crit_dice, 
                              advantage = advantage, 
                              disadvantage = disadvantage, crit_19 = crit_19, 
                              reroll = reroll, GWM = GWM)
        
        hit_store.append(attack['hit'])
        crit_store.append(attack['crit'])
        hit_dice.append(attack['to_hit_dice'])
        dmg_store.append(attack['dmg'])

    attack_stats['hit_chance'] = sum(hit_store)/len(hit_store)
    attack_stats['crit_chance'] = sum(crit_store)/len(crit_store)
    attack_stats['dmg_mean'] = num_attacks * np.mean(dmg_store)
    
    # resample for generating confidence interval
    dmg_per_round = dmg_store
    for i in range(num_attacks-1):
        dmg_per_round += np.random.choice(dmg_store,n)
    
    attack_stats['dmg_per_round'] = dmg_per_round
    attack_stats['dmg_ci_lo'] = np.percentile(dmg_per_round, ci)
    attack_stats['dmg_ci_hi'] = np.percentile(dmg_per_round, 100 - ci)
    
    return attack_stats
    
    
def melee_stats_vs_ac(n, ac, ci = 10, num_attacks = 1, hit_die = 6, 
                      num_hit_dice = 1, mod = 0, bonus_crit_dice = 0, 
                      advantage = False, disadvantage = False, 
                      crit_19 = False, reroll = False, GWM = False):
    """

    """
    attack_stats_vs_ac = dict()
    attack_stats_vs_ac['hit_chance'] = []
    attack_stats_vs_ac['crit_chance'] = []
    attack_stats_vs_ac['dmg_mean'] = []
    attack_stats_vs_ac['dmg_ci_lo'] = []
    attack_stats_vs_ac['dmg_ci_hi'] = []
    
    for cur_ac in ac:
        attack_stats = melee_stats(n, cur_ac, ci = ci, 
                                   num_attacks = num_attacks, hit_die = hit_die, 
                                   num_hit_dice = num_hit_dice, mod = mod, 
                                   bonus_crit_dice = bonus_crit_dice, 
                                   advantage = advantage, 
                                   disadvantage = disadvantage, 
                                   crit_19 = crit_19, reroll = reroll, 
                                   GWM = GWM)
        
        attack_stats_vs_ac['hit_chance'].append(attack_stats['hit_chance'])
        attack_stats_vs_ac['crit_chance'].append(attack_stats['crit_chance'])
        attack_stats_vs_ac['dmg_mean'].append(attack_stats['dmg_mean'])
        attack_stats_vs_ac['dmg_ci_lo'].append(attack_stats['dmg_ci_lo'])
        attack_stats_vs_ac['dmg_ci_hi'].append(attack_stats['dmg_ci_hi'])
        
    return attack_stats_vs_ac