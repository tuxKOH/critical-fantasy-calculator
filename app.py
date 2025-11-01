"""
Critical Fantasy Damage Calculator
Copyright (C) 2024  @tux_koh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask, render_template, request, jsonify
import math
from itertools import combinations

app = Flask(__name__)

class DamageCalculator:
    # Stat point multipliers
    STR_DMG_MIN = 2.96
    STR_DMG_MAX = 6.45
    INT_MAGIC = 6.0
    VIT_HP = 35
    DEF_SHIELD = 17
    DEX_CRIT = 0.8
    BASE_CRIT_RATE = 1.0  # Base 1% crit rate
    BASE_CRIT_DAMAGE = 100  # Base 100% crit damage = extra 100% damage
    MAX_DEX_CRIT = 50 * DEX_CRIT  # Max 50 dexterity points = 40% crit rate
    
    # Base stats for level 0 character
    BASE_MIN_ATK = 8
    BASE_MAX_ATK = 15
    BASE_MAGIC = 10
    
    @staticmethod
    def calculate_max_points(level):
        """Calculate maximum attribute points based on level"""
        return level * 2
    
    @staticmethod
    def calculate_equipment_bonus(equipment_data):
        """Calculate actual equipment bonuses from drop range"""
        bonuses = {
            'atk_min': 0,
            'atk_max': 0,
            'magic': 0,
            'crit_chance': 0,
            'crit_damage': 0,
            'health': 0,
            'shield': 0
        }
        
        stats = equipment_data.get('stats', {})
        
        # Handle attack range (physical equipment)
        if 'atk_min' in stats and 'atk_max' in stats:
            # Get the middle value of the drop range
            drop_min = stats['atk_min']
            drop_max = stats['atk_max']
            middle_value = (drop_min + drop_max) / 2
            
            # Apply the 0.85x to min and 1.25x to max for actual bonus
            bonuses['atk_min'] = middle_value * 0.85
            bonuses['atk_max'] = middle_value * 1.25
        
        # Handle magic damage (magic equipment)
        if 'magic' in stats:
            # For magic equipment, just use the value directly
            bonuses['magic'] = stats['magic']
        
        # Handle other stats (direct addition)
        if 'crit_chance' in stats:
            bonuses['crit_chance'] = stats['crit_chance']
        if 'crit_damage' in stats:
            bonuses['crit_damage'] = stats['crit_damage']
        if 'health' in stats:
            bonuses['health'] = stats['health']
        if 'shield' in stats:
            bonuses['shield'] = stats['shield']
            
        return bonuses
    
    @staticmethod
    def calculate_stats_from_points(strength, vitality, intelligence, dexterity, defense, level=190):
        """Calculate base stats from attribute points"""
        # Cap dexterity crit contribution at 50 points
        effective_dex_crit = min(dexterity, 50) * DamageCalculator.DEX_CRIT
        
        return {
            'min_damage': strength * DamageCalculator.STR_DMG_MIN + DamageCalculator.BASE_MIN_ATK,
            'max_damage': strength * DamageCalculator.STR_DMG_MAX + DamageCalculator.BASE_MAX_ATK,
            'health': vitality * DamageCalculator.VIT_HP,
            'magic_damage': intelligence * DamageCalculator.INT_MAGIC + DamageCalculator.BASE_MAGIC,
            'crit_chance': DamageCalculator.BASE_CRIT_RATE + effective_dex_crit,
            'crit_damage': DamageCalculator.BASE_CRIT_DAMAGE,
            'shield': defense * DamageCalculator.DEF_SHIELD
        }
    
    @staticmethod
    def calculate_three_hit_damage(base_damage, dot_damage, weapon_type, crit_multiplied_damage):
        """Calculate damage for 3 hits based on weapon type and class mechanics"""
        
        # Base damage per hit (without DoT)
        base_damage_per_hit = crit_multiplied_damage
        dot_damage_per_hit = dot_damage
        
        if weapon_type == 'staff':  # Flow (Mage)
            # Each hit: 100% magic damage + DoT
            # After 3 hits: extra 300% damage
            three_hits_damage = (base_damage_per_hit + dot_damage_per_hit) * 3
            bonus_damage = base_damage_per_hit * 3  # 300% bonus
            total_damage = three_hits_damage + bonus_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'bonus_damage': bonus_damage,
                'total_damage': total_damage,
                'mechanic': 'Flow: 100% per hit + 300% bonus after 3 hits'
            }
        
        elif weapon_type == 'bow':  # Brust (Archer)
            # Double damage on all hits
            three_hits_damage = (base_damage_per_hit * 2 + dot_damage_per_hit) * 3
            bonus_damage = 0
            
            return {
                'hit_1': base_damage_per_hit * 2 + dot_damage_per_hit,
                'hit_2': base_damage_per_hit * 2 + dot_damage_per_hit,
                'hit_3': base_damage_per_hit * 2 + dot_damage_per_hit,
                'bonus_damage': bonus_damage,
                'total_damage': three_hits_damage,
                'mechanic': 'Brust: 200% damage per hit'
            }
        
        elif weapon_type in ['sword', 'blade']:  # Chain (Blade)
            # Combo damage: 1x, 3x, 6x (arithmetic sequence)
            hit_multipliers = [1, 3, 6]
            hits_damage = [
                (base_damage_per_hit * multiplier + dot_damage_per_hit) 
                for multiplier in hit_multipliers
            ]
            total_damage = sum(hits_damage)
            
            return {
                'hit_1': hits_damage[0],
                'hit_2': hits_damage[1],
                'hit_3': hits_damage[2],
                'bonus_damage': 0,
                'total_damage': total_damage,
                'mechanic': 'Chain: 1x, 3x, 6x combo damage'
            }
        
        elif weapon_type == 'scythe':  # Reverberation (Scythe)
            # 25% chance for 4x damage on each hit
            # Calculate expected damage considering probability
            expected_damage_per_hit = (base_damage_per_hit * 4 * 0.25) + (base_damage_per_hit * 0.75) + dot_damage_per_hit
            three_hits_damage = expected_damage_per_hit * 3
            
            return {
                'hit_1': expected_damage_per_hit,
                'hit_2': expected_damage_per_hit,
                'hit_3': expected_damage_per_hit,
                'bonus_damage': 0,
                'total_damage': three_hits_damage,
                'mechanic': 'Reverberation: 25% chance for 400% damage'
            }
        
        else:  # Default (no special mechanic)
            three_hits_damage = (base_damage_per_hit + dot_damage_per_hit) * 3
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'bonus_damage': 0,
                'total_damage': three_hits_damage,
                'mechanic': 'Default: 100% damage per hit'
            }
    
    @staticmethod
    def calculate_damage(data):
        try:
            # Get base values - either from manual input or calculated from points
            use_point_system = data.get('usePointSystem', False)
            selected_weapon = data.get('selectedWeapon', '')
            player_level = data.get('playerLevel', 190)
            
            # Determine damage type based on weapon
            if selected_weapon:
                weapon_data = WEAPON_DB.get(selected_weapon, {})
                damage_type = 'magic' if weapon_data.get('type') == 'staff' else 'attack'
            else:
                damage_type = 'attack'  # Default to attack if no weapon selected
            
            if use_point_system:
                # Calculate stats from attribute points
                strength = int(data.get('strength', 0))
                vitality = int(data.get('vitality', 0))
                intelligence = int(data.get('intelligence', 0))
                dexterity = int(data.get('dexterity', 0))
                defense = int(data.get('defense', 0))
                
                base_stats = DamageCalculator.calculate_stats_from_points(
                    strength, vitality, intelligence, dexterity, defense, player_level
                )
                
                min_damage = base_stats['min_damage']
                max_damage = base_stats['max_damage']
                magic_damage = base_stats['magic_damage']
                base_crit_rate = base_stats['crit_chance']
                base_crit_damage = base_stats['crit_damage']
            else:
                # Use manual input
                min_damage = float(data.get('minDamage', 0)) or DamageCalculator.BASE_MIN_ATK
                max_damage = float(data.get('maxDamage', 0)) or DamageCalculator.BASE_MAX_ATK
                magic_damage = float(data.get('magicDamage', 0)) or DamageCalculator.BASE_MAGIC
                base_crit_rate = float(data.get('critRate', DamageCalculator.BASE_CRIT_RATE))
                base_crit_damage = float(data.get('critDamage', DamageCalculator.BASE_CRIT_DAMAGE))
            
            # Track set bonuses (FIXED: include weapon sets)
            set_counts = {
                'flame': 0,
                'wolf_howl': 0,
                'crimson': 0,
                'queen_bee': 0,
                'explorer': 0,
                'forest_dweller': 0,
                'library_ruina': 0,
                'blessing': 0
            }
            
            # Apply weapon stats if weapon is selected and count weapon set
            if selected_weapon:
                weapon_data = WEAPON_DB.get(selected_weapon, {})
                weapon_bonus = DamageCalculator.calculate_equipment_bonus(weapon_data)
                
                min_damage += weapon_bonus['atk_min']
                max_damage += weapon_bonus['atk_max']
                magic_damage += weapon_bonus['magic']
                # Apply weapon crit stats
                base_crit_rate += weapon_bonus['crit_chance']
                base_crit_damage += weapon_bonus['crit_damage']
                
                # Count weapon set piece (FIXED: add weapon to set count)
                if weapon_data.get('set'):
                    set_counts[weapon_data['set']] += 1
            
            # Calculate average physical damage
            avg_physical_damage = (min_damage + max_damage) / 2
            
            # Get potion effects
            has_magic_potion = data.get('magicPotion', False)
            has_attack_potion = data.get('attackPotion', False)
            has_golden_apple = data.get('goldenApple', False)
            
            # Get selected equipment
            equipment = data.get('equipment', [])
            
            # Apply equipment stat bonuses and calculate total crit rate
            total_crit_rate = base_crit_rate
            total_crit_damage = base_crit_damage
            
            # Apply equipment stats and count set pieces
            for eq in equipment:
                eq_data = EQUIPMENT_DB.get(eq, {})
                eq_bonus = DamageCalculator.calculate_equipment_bonus(eq_data)
                
                # Apply stat bonuses to BASE stats (so they get multiplied by potions)
                min_damage += eq_bonus['atk_min']
                max_damage += eq_bonus['atk_max']
                magic_damage += eq_bonus['magic']
                total_crit_rate += eq_bonus['crit_chance']
                total_crit_damage += eq_bonus['crit_damage']
                
                # Count set pieces
                if eq_data.get('set'):
                    set_counts[eq_data['set']] += 1
            
            # Recalculate average physical damage after equipment bonuses
            avg_physical_damage = (min_damage + max_damage) / 2
            
            # Apply potion effects to base stats (after equipment bonuses)
            effective_min_damage = min_damage
            effective_max_damage = max_damage
            effective_avg_physical_damage = avg_physical_damage
            effective_magic_damage = magic_damage
            
            if has_attack_potion:
                effective_min_damage *= 1.75
                effective_max_damage *= 1.75
                effective_avg_physical_damage *= 1.75
            if has_golden_apple:
                effective_min_damage *= 1.5
                effective_max_damage *= 1.5
                effective_avg_physical_damage *= 1.5
            if has_magic_potion:
                effective_magic_damage *= 1.75
            
            # Apply set bonuses
            set_bonus_applied = {
                'wolf_howl': False,
                'crimson': False,
                'forest_dweller': False,
                'explorer': False,
                'flame': False
            }
            
            # Debug: print set counts
            print(f"Set Counts: {set_counts}")
            
            # Wolf Howl Set: +12% crit chance for 2+ pieces
            if set_counts['wolf_howl'] >= 2:
                total_crit_rate += 12
                set_bonus_applied['wolf_howl'] = True
                print(f"Wolf Howl Set Bonus Applied: +12% crit chance (Count: {set_counts['wolf_howl']})")
            
            # Crimson Set: +18% magic damage for 2+ pieces
            if set_counts['crimson'] >= 2:
                effective_magic_damage *= 1.18
                set_bonus_applied['crimson'] = True
                print(f"Crimson Set Bonus Applied: +18% magic damage (Count: {set_counts['crimson']})")
            
            # Forest Dweller Set: +18% melee attack for 2+ pieces
            if set_counts['forest_dweller'] >= 2 and damage_type == 'attack':
                effective_min_damage *= 1.18
                effective_max_damage *= 1.18
                effective_avg_physical_damage *= 1.18
                set_bonus_applied['forest_dweller'] = True
                print(f"Forest Dweller Set Bonus Applied: +18% attack damage (Count: {set_counts['forest_dweller']})")
            
            # Explorer Set: +200 HP for 2+ pieces (applied in player stats)
            if set_counts['explorer'] >= 2:
                set_bonus_applied['explorer'] = True
                print(f"Explorer Set Bonus Applied: +200 HP (Count: {set_counts['explorer']})")
            
            # Calculate base damage based on damage type
            if damage_type == 'magic':
                base_damage = effective_magic_damage
                # For magic damage, crit uses the same base damage
                crit_base_damage = base_damage
            else:  # attack
                base_damage = effective_avg_physical_damage
                # For physical damage, crit uses MAX damage instead of average
                crit_base_damage = effective_max_damage
            
            # Calculate crit damage multiplier
            # Crit Damage 100% = extra 100% damage = total damage becomes 200% (2x)
            crit_rate = min(total_crit_rate / 100, 1.0)  # Cap at 100%
            crit_damage_multiplier = 1 + (total_crit_damage / 100)  # 100% crit damage = 2x multiplier
            
            # Calculate expected damage with crit
            # Non-crit damage uses base_damage, crit damage uses crit_base_damage * crit_damage_multiplier
            expected_non_crit_damage = base_damage * (1 - crit_rate)
            expected_crit_damage = crit_base_damage * crit_damage_multiplier * crit_rate
            total_damage = expected_non_crit_damage + expected_crit_damage
            
            # Apply equipment effects
            dot_damage = 0
            has_cursed_spellbook = 'cursed_spellbook' in equipment
            has_dual_sword = 'dual_sword' in equipment
            
            # Cursed Spellbook effect
            if has_cursed_spellbook:
                total_damage *= 1.3
            
            # Dual Sword effect
            if has_dual_sword:
                dual_sword_multiplier = 1 + (0.15 * (2 - 1))
                total_damage *= dual_sword_multiplier
            
            # Calculate DOT damage (unaffected by crit or equipment multipliers)
            flame_set_count = set_counts['flame']
            burn_chance = 0
            bleed_chance = 0
            poison_chance = 0
            has_volatile_gem = False
            
            # Check for flame set items and calculate burn chance
            flame_items = ['daybreak', 'evernight', 'volatile_gem']
            for item in equipment:
                if item in flame_items:
                    eq_data = EQUIPMENT_DB.get(item, {})
                    special_effects = eq_data.get('special_effects', {})
                    if item == 'daybreak':
                        burn_chance += special_effects.get('burn_chance', 0.52)
                    elif item == 'evernight':
                        burn_chance += special_effects.get('burn_chance', 0.40)
                    elif item == 'volatile_gem':
                        burn_chance += special_effects.get('burn_chance', 0.11)
                        poison_chance += special_effects.get('poison_chance', 0.11)
                        has_volatile_gem = True
            
            # Apply flame set bonus
            if flame_set_count >= 2:
                burn_chance += 0.10
                set_bonus_applied['flame'] = True
                print(f"Flame Set Bonus Applied: +10% burn chance (Count: {flame_set_count})")
            
            # Queenbee Crown (bleeding)
            if 'queenbee_crown' in equipment:
                eq_data = EQUIPMENT_DB.get('queenbee_crown', {})
                special_effects = eq_data.get('special_effects', {})
                bleed_chance += special_effects.get('bleed_chance', 0.26)
            
            # Calculate burn damage (uses potion-boosted magic damage)
            if burn_chance > 0:
                burn_damage = effective_magic_damage * 0.33 * 5
                if has_volatile_gem:
                    burn_damage += effective_magic_damage * 0.20
                dot_damage += burn_damage * min(burn_chance, 1)
            
            # Queenbee Crown bleeding damage - uses potion-boosted average physical damage
            if bleed_chance > 0:
                bleeding_damage = effective_avg_physical_damage * 0.25 * 5
                dot_damage += bleeding_damage * min(bleed_chance, 1)
            
            # Volatile Gem poison - uses potion-boosted magic damage
            if poison_chance > 0:
                poison_damage = effective_magic_damage * 0.40 * 5
                poison_damage += effective_magic_damage * 0.20
                dot_damage += poison_damage * min(poison_chance, 1)
            
            # Blood Butcher - uses potion-boosted min physical damage
            if 'blood_butcher' in equipment:
                blood_damage = effective_min_damage * 0.05 * 9
                dot_damage += blood_damage
            
            # Total final damage
            final_damage = total_damage + dot_damage
            
            # Calculate three hit damage
            weapon_type = WEAPON_DB.get(selected_weapon, {}).get('type', 'sword') if selected_weapon else 'sword'
            three_hit_data = DamageCalculator.calculate_three_hit_damage(
                base_damage, dot_damage, weapon_type, total_damage
            )
            
            # Prepare detailed calculation data
            calculation_details = {
                'base_stats': {
                    'min_damage': min_damage,
                    'max_damage': max_damage,
                    'magic_damage': magic_damage,
                    'base_crit_rate': base_crit_rate,
                    'base_crit_damage': base_crit_damage
                },
                'after_equipment': {
                    'min_damage': min_damage,
                    'max_damage': max_damage,
                    'magic_damage': magic_damage,
                    'total_crit_rate': total_crit_rate,
                    'total_crit_damage': total_crit_damage
                },
                'after_potions': {
                    'effective_min_damage': effective_min_damage,
                    'effective_max_damage': effective_max_damage,
                    'effective_magic_damage': effective_magic_damage
                },
                'set_bonuses': set_bonus_applied,
                'crit_calculation': {
                    'crit_rate_percent': crit_rate * 100,
                    'crit_damage_multiplier': crit_damage_multiplier,
                    'crit_base_damage': crit_base_damage,
                    'expected_non_crit_damage': expected_non_crit_damage,
                    'expected_crit_damage': expected_crit_damage
                },
                'dot_calculation': {
                    'burn_chance': burn_chance,
                    'bleed_chance': bleed_chance,
                    'poison_chance': poison_chance,
                    'burn_damage': burn_damage if burn_chance > 0 else 0,
                    'bleeding_damage': bleeding_damage if bleed_chance > 0 else 0,
                    'poison_damage': poison_damage if poison_chance > 0 else 0
                }
            }
            
            result = {
                'success': True,
                'min_damage': round(min_damage, 2),
                'max_damage': round(max_damage, 2),
                'magic_damage': round(magic_damage, 2),
                'avg_physical_damage': round(avg_physical_damage, 2),
                'effective_min_damage': round(effective_min_damage, 2),
                'effective_max_damage': round(effective_max_damage, 2),
                'effective_avg_physical_damage': round(effective_avg_physical_damage, 2),
                'effective_magic_damage': round(effective_magic_damage, 2),
                'base_damage': round(base_damage, 2),
                'crit_multiplied_damage': round(total_damage, 2),
                'dot_damage': round(dot_damage, 2),
                'final_damage': round(final_damage, 2),
                'effective_multiplier': round(final_damage / base_damage, 2) if base_damage > 0 else 0,
                'crit_rate': round(total_crit_rate, 1),
                'crit_damage': round(total_crit_damage, 1),
                'burn_chance': round(burn_chance * 100, 1),
                'bleed_chance': round(bleed_chance * 100, 1),
                'poison_chance': round(poison_chance * 100, 1),
                'flame_set_count': flame_set_count,
                'damage_type': damage_type,
                'set_counts': set_counts,
                'set_bonuses_applied': set_bonus_applied,
                'potion_effects': {
                    'magic_potion': has_magic_potion,
                    'attack_potion': has_attack_potion,
                    'golden_apple': has_golden_apple
                },
                'calculated_stats': use_point_system,
                'three_hit_damage': {
                    'hit_1': round(three_hit_data['hit_1'], 2),
                    'hit_2': round(three_hit_data['hit_2'], 2),
                    'hit_3': round(three_hit_data['hit_3'], 2),
                    'bonus_damage': round(three_hit_data['bonus_damage'], 2),
                    'total_damage': round(three_hit_data['total_damage'], 2),
                    'mechanic': three_hit_data['mechanic']
                },
                'calculation_details': calculation_details
            }
            
            if use_point_system:
                # Apply explorer set bonus to health
                explorer_hp_bonus = 200 if set_counts['explorer'] >= 2 else 0
                
                result['player_stats'] = {
                    'health': vitality * DamageCalculator.VIT_HP + explorer_hp_bonus,
                    'shield': defense * DamageCalculator.DEF_SHIELD,
                    'total_hp': vitality * DamageCalculator.VIT_HP + defense * DamageCalculator.DEF_SHIELD + explorer_hp_bonus,
                    'min_damage': min_damage,
                    'max_damage': max_damage,
                    'magic_damage': magic_damage,
                    'crit_rate': total_crit_rate,
                    'crit_damage': total_crit_damage
                }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Weapon Database with level requirements
WEAPON_DB = {
    'wooden_sword': {
        'name': 'Wooden Sword',
        'type': 'sword',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1
    },
    'wooden_staff': {
        'name': 'Wooden Staff', 
        'type': 'staff',
        'stats': {'magic': 4},
        'set': 'blessing',
        'level_req': 1
    },
    'wooden_bow': {
        'name': 'Wooden Bow',
        'type': 'bow', 
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1
    },
    'divine_blade': {
        'name': 'Divine Blade',
        'type': 'sword',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15
    },
    'forest_dweller_staff': {
        'name': 'Forest Dweller\'s Staff',
        'type': 'staff',
        'stats': {'magic': 60},
        'set': 'explorer',
        'level_req': 15
    },
    'forest_dweller_bow': {
        'name': 'Forest Dweller\'s Bow',
        'type': 'bow',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15
    },
    'crescendo_scythe': {
        'name': 'Crescendo Scythe',
        'type': 'scythe',
        'stats': {'atk_min': 75, 'atk_max': 75},
        'set': 'library_ruina',
        'level_req': 15
    },
    'emerald_staff': {
        'name': 'Emerald Staff',
        'type': 'staff', 
        'stats': {'magic': 500},
        'level_req': 65
    },
    'winter_howl': {
        'name': 'Winter Howl',
        'type': 'sword',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'wolf_howl',
        'level_req': 65
    },
    'eventide': {
        'name': 'Eventide',
        'type': 'bow',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'queen_bee',
        'level_req': 65
    }
}

# Equipment Database with level requirements
EQUIPMENT_DB = {
    # Tier I
    'burning_torch': {
        'name': 'Burning Torch',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'climbing_hook': {
        'name': 'Climbing Hook',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'hunting_dagger': {
        'name': 'Hunting Dagger',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'set': 'explorer',
        'level_req': 1
    },
    'lantern': {
        'name': 'Lantern',
        'tier': 'I',
        'stats': {'magic': 5},
        'special_effects': {},
        'level_req': 5
    },
    'metal_plate': {
        'name': 'Metal Plate',
        'tier': 'I',
        'stats': {'shield': 10},
        'special_effects': {},
        'level_req': 2
    },
    'mining_pickaxe': {
        'name': 'Mining Pickaxe',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'rabbits_foot': {
        'name': 'Rabbit\'s Foot',
        'tier': 'I',
        'stats': {'crit_chance': 3},
        'special_effects': {},
        'level_req': 5
    },
    'sharpener_rock': {
        'name': 'Sharpener\'s Rock',
        'tier': 'I', 
        'stats': {'crit_chance': 5, 'crit_damage': 10},
        'special_effects': {},
        'level_req': 10
    },
    'travellers_boots': {
        'name': 'Traveller\'s Boots',
        'tier': 'I',
        'stats': {'health': 20},
        'special_effects': {},
        'level_req': 1
    },
    
    # Tier II
    'adventurers_kit': {
        'name': 'Adventurer\'s Kit',
        'tier': 'II',
        'stats': {'health': 50, 'shield': 10},
        'special_effects': {},
        'level_req': 25
    },
    'ancient_hammer': {
        'name': 'Ancient Hammer',
        'tier': 'II',
        'stats': {'atk_min': 50, 'atk_max': 50},
        'special_effects': {},
        'level_req': 10
    },
    'ancient_wood_armor': {
        'name': 'Ancient Wood Armor',
        'tier': 'II',
        'stats': {'health': 80, 'shield': 15},
        'special_effects': {},
        'level_req': 10
    },
    'copper_sword': {
        'name': 'Copper Sword',
        'tier': 'II',
        'stats': {'atk_min': 30, 'atk_max': 30},
        'special_effects': {},
        'level_req': 5
    },
    'dual_sword': {
        'name': 'Dual Sword',
        'tier': 'II',
        'stats': {'atk_min': 135, 'atk_max': 149},
        'special_effects': {'double_damage_chance': 0.15},
        'level_req': 100
    },
    'forest_dweller_axe': {
        'name': 'Forest Dweller\'s Axe',
        'tier': 'II',
        'stats': {'atk_min': 40, 'atk_max': 40, 'crit_chance': 5},
        'special_effects': {'bleed_chance': 0.02},
        'set': 'forest_dweller',
        'level_req': 10
    },
    'volatile_crystal': {
        'name': 'Volatile Crystal',
        'tier': 'II',
        'stats': {'magic': 45},
        'special_effects': {},
        'level_req': 5
    },
    
    # Tier III
    'alderite_axe': {
        'name': 'Alderite Axe',
        'tier': 'III',
        'stats': {'atk_min': 175, 'atk_max': 194, 'magic': 140, 'crit_chance': 5},
        'special_effects': {},
        'level_req': 35
    },
    'aqua_crystal': {
        'name': 'Aqua Crystal',
        'tier': 'III',
        'stats': {'magic': 110},
        'special_effects': {},
        'level_req': 30
    },
    'arcane_spellbook': {
        'name': 'Arcane Spellbook',
        'tier': 'III',
        'stats': {'magic': 100},
        'special_effects': {},
        'level_req': 25
    },
    'corrupted_fang': {
        'name': 'Corrupted Fang',
        'tier': 'III',
        'stats': {'magic': 130, 'atk_min': 35, 'atk_max': 35},
        'special_effects': {},
        'level_req': 30
    },
    'daybreak': {
        'name': 'Daybreak',
        'tier': 'III',
        'stats': {'atk_min': 100, 'atk_max': 111},
        'special_effects': {'burn_chance': 0.52},
        'set': 'flame',
        'level_req': 70
    },
    'enchanted_blade': {
        'name': 'Enchanted Blade',
        'tier': 'III',
        'stats': {'atk_min': 125, 'atk_max': 125, 'magic': 100},
        'special_effects': {},
        'level_req': 25
    },
    'magicians_hat': {
        'name': 'Magician\'s Hat',
        'tier': 'III',
        'stats': {'magic': 80, 'health': 30},
        'special_effects': {},
        'level_req': 25
    },
    'mana_lantern': {
        'name': 'Mana Lantern',
        'tier': 'III',
        'stats': {'magic': 90},
        'special_effects': {},
        'level_req': 25
    },
    
    # Tier IV
    'atlantis_armor': {
        'name': 'Atlantis Armor',
        'tier': 'IV',
        'stats': {'health': 75, 'shield': 10},
        'special_effects': {},
        'level_req': 50
    },
    'bee_breastplate': {
        'name': 'Bee Breastplate',
        'tier': 'IV',
        'stats': {'health': 460, 'shield': 40},
        'special_effects': {},
        'set': 'queen_bee',
        'level_req': 65
    },
    'black_wolf_necklace': {
        'name': 'Black Wolf Necklace',
        'tier': 'IV',
        'stats': {'atk_min': 225, 'atk_max': 249, 'crit_chance': 15, 'crit_damage': 22},
        'special_effects': {},
        'set': 'wolf_howl',
        'level_req': 65
    },
    'blood_butcher': {
        'name': 'Blood Butcher',
        'tier': 'IV',
        'stats': {'atk_min': 250, 'atk_max': 277, 'crit_chance': 16},
        'special_effects': {'blood_butcher': True},
        'set': 'crimson',
        'level_req': 50
    },
    'crimson_slime_fang': {
        'name': 'Crimson Slime Fang',
        'tier': 'IV',
        'stats': {'magic': 220, 'crit_damage': 27},
        'special_effects': {},
        'set': 'crimson',
        'level_req': 65
    },
    'cursed_spellbook': {
        'name': 'Cursed Spellbook',
        'tier': 'IV',
        'stats': {'magic': 400},
        'special_effects': {'damage_multiplier': 1.3},
        'set': 'crimson',
        'level_req': 100
    },
    'evernight': {
        'name': 'Evernight',
        'tier': 'IV',
        'stats': {'atk_min': 450, 'atk_max': 450},
        'special_effects': {'burn_chance': 0.40},
        'set': 'flame',
        'level_req': 100
    },
    'forest_crown': {
        'name': 'Forest Crown',
        'tier': 'IV',
        'stats': {'health': 775, 'shield': 275},
        'special_effects': {},
        'level_req': 65
    },
    'ghost_lantern': {
        'name': 'Ghost Lantern',
        'tier': 'IV',
        'stats': {'magic': 480},
        'special_effects': {},
        'level_req': 65
    },
    'slime_crown': {
        'name': 'Slime Crown',
        'tier': 'IV',
        'stats': {'health': 200, 'shield': 50},
        'special_effects': {},
        'level_req': 35
    },
    'volcanic_axe': {
        'name': 'Volcanic Axe',
        'tier': 'IV',
        'stats': {'atk_min': 280, 'atk_max': 280},
        'special_effects': {'burn_chance': 0.05},
        'set': 'wolf_howl',
        'level_req': 65
    },
    'winter_spirit': {
        'name': 'Winter Spirit',
        'tier': 'IV',
        'stats': {'atk_min': 200, 'atk_max': 200, 'health': 50},
        'special_effects': {'freeze_chance': 0.02},
        'level_req': 65
    },
    
    # Tier V
    'queenbee_crown': {
        'name': 'Queen Bee\'s Crown',
        'tier': 'V',
        'stats': {'atk_min': 800, 'atk_max': 888, 'crit_chance': 20, 'crit_damage': 80},
        'special_effects': {'bleed_chance': 0.26},
        'set': 'queen_bee',
        'level_req': 150
    },
    'volatile_gem': {
        'name': 'Volatile Gem',
        'tier': 'V',
        'stats': {'magic': 315},
        'special_effects': {
            'burn_chance': 0.11,
            'poison_chance': 0.11,
            'dot_bonus': 0.20
        },
        'set': 'flame',
        'level_req': 150
    },
    
    # Mana-Focused Passives
    'mana_crystal': {
        'name': 'Mana Crystal',
        'tier': 'II',
        'stats': {'magic': 25},
        'special_effects': {},
        'level_req': 5
    },
    'aqua_lapis': {
        'name': 'Aqua Lapis',
        'tier': 'III',
        'stats': {'magic': 70},
        'special_effects': {},
        'level_req': 30
    }
}

def is_mobile_device(user_agent):
    """Detect if the request is from a mobile device"""
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'webos', 'windows phone', 'kindle'
    ]
    user_agent = user_agent.lower()
    return any(keyword in user_agent for keyword in mobile_keywords)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    return render_template('index.html', 
                         equipment_db=EQUIPMENT_DB, 
                         weapon_db=WEAPON_DB,
                         is_mobile=is_mobile)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    result = DamageCalculator.calculate_damage(data)
    return jsonify(result)

@app.route('/optimize', methods=['POST'])
def optimize_damage():
    """Find the best equipment combinations for maximum damage"""
    data = request.get_json()
    
    try:
        # Get base configuration
        base_config = {
            'usePointSystem': data.get('usePointSystem', False),
            'selectedWeapon': data.get('selectedWeapon', ''),
            'magicPotion': data.get('magicPotion', False),
            'attackPotion': data.get('attackPotion', False),
            'goldenApple': data.get('goldenApple', False)
        }
        
        if base_config['usePointSystem']:
            base_config.update({
                'strength': data.get('strength', 0),
                'vitality': data.get('vitality', 0),
                'intelligence': data.get('intelligence', 0),
                'dexterity': data.get('dexterity', 0),
                'defense': data.get('defense', 0)
            })
        else:
            base_config.update({
                'minDamage': data.get('minDamage', 0),
                'maxDamage': data.get('maxDamage', 0),
                'magicDamage': data.get('magicDamage', 0),
                'critRate': data.get('critRate', 1),
                'critDamage': data.get('critDamage', 100)
            })
        
        # Get all equipment IDs
        all_equipment = list(EQUIPMENT_DB.keys())
        max_equipment = 3
        
        # Generate all possible combinations
        all_combinations = list(combinations(all_equipment, max_equipment))
        
        # Test each combination and find the best ones
        results = []
        for i, combo in enumerate(all_combinations):
            if i % 100 == 0:  # Progress tracking for large datasets
                print(f"Testing combination {i}/{len(all_combinations)}")
            
            test_config = base_config.copy()
            test_config['equipment'] = list(combo)
            
            result = DamageCalculator.calculate_damage(test_config)
            if result['success']:
                results.append({
                    'equipment': list(combo),
                    'final_damage': result['final_damage'],
                    'three_hit_total': result['three_hit_damage']['total_damage'],
                    'crit_rate': result['crit_rate'],
                    'crit_damage': result['crit_damage']
                })
        
        # Sort by final damage (descending)
        results.sort(key=lambda x: x['final_damage'], reverse=True)
        
        # Return top 10 combinations
        top_combinations = results[:10]
        
        # Format results with equipment names
        formatted_results = []
        for combo in top_combinations:
            equipment_names = [EQUIPMENT_DB[eq_id]['name'] for eq_id in combo['equipment']]
            formatted_results.append({
                'equipment_ids': combo['equipment'],
                'equipment_names': equipment_names,
                'final_damage': round(combo['final_damage'], 2),
                'three_hit_total': round(combo['three_hit_total'], 2),
                'crit_rate': round(combo['crit_rate'], 1),
                'crit_damage': round(combo['crit_damage'], 1)
            })
        
        return jsonify({
            'success': True,
            'top_combinations': formatted_results,
            'total_combinations_tested': len(all_combinations)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/optimize_advanced', methods=['POST'])
def optimize_damage_advanced():
    """Find the best equipment combinations with different criteria"""
    data = request.get_json()
    
    try:
        # Get base configuration
        base_config = {
            'usePointSystem': data.get('usePointSystem', False),
            'selectedWeapon': data.get('selectedWeapon', ''),
            'magicPotion': data.get('magicPotion', False),
            'attackPotion': data.get('attackPotion', False),
            'goldenApple': data.get('goldenApple', False),
            'playerLevel': data.get('playerLevel', 190)  # Default to max level
        }
        
        if base_config['usePointSystem']:
            base_config.update({
                'strength': data.get('strength', 0),
                'vitality': data.get('vitality', 0),
                'intelligence': data.get('intelligence', 0),
                'dexterity': data.get('dexterity', 0),
                'defense': data.get('defense', 0)
            })
        else:
            base_config.update({
                'minDamage': data.get('minDamage', 0),
                'maxDamage': data.get('maxDamage', 0),
                'magicDamage': data.get('magicDamage', 0),
                'critRate': data.get('critRate', 1),
                'critDamage': data.get('critDamage', 100)
            })
        
        optimization_type = data.get('optimizationType', 'final_damage')  # final_damage, three_hit, first_hit, dot
        
        # Get all equipment IDs that meet level requirement
        player_level = base_config['playerLevel']
        available_equipment = [
            eq_id for eq_id, eq_data in EQUIPMENT_DB.items() 
            if eq_data.get('level_req', 0) <= player_level
        ]
        
        max_equipment = 3
        
        # Generate all possible combinations from available equipment
        all_combinations = list(combinations(available_equipment, max_equipment))
        
        # Test each combination and find the best ones
        results = []
        for i, combo in enumerate(all_combinations):
            if i % 100 == 0:  # Progress tracking
                print(f"Testing combination {i}/{len(all_combinations)}")
            
            test_config = base_config.copy()
            test_config['equipment'] = list(combo)
            
            result = DamageCalculator.calculate_damage(test_config)
            if result['success']:
                # Determine score based on optimization type
                if optimization_type == 'final_damage':
                    score = result['final_damage']
                elif optimization_type == 'three_hit':
                    score = result['three_hit_damage']['total_damage']
                elif optimization_type == 'first_hit':
                    score = result['three_hit_damage']['hit_1']
                elif optimization_type == 'dot':
                    score = result['dot_damage']
                else:
                    score = result['final_damage']
                
                results.append({
                    'equipment': list(combo),
                    'final_damage': result['final_damage'],
                    'three_hit_total': result['three_hit_damage']['total_damage'],
                    'first_hit': result['three_hit_damage']['hit_1'],
                    'dot_damage': result['dot_damage'],
                    'crit_rate': result['crit_rate'],
                    'crit_damage': result['crit_damage'],
                    'score': score
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 10 combinations
        top_combinations = results[:10]
        
        # Format results with equipment names
        formatted_results = []
        for combo in top_combinations:
            equipment_names = [EQUIPMENT_DB[eq_id]['name'] for eq_id in combo['equipment']]
            formatted_results.append({
                'equipment_ids': combo['equipment'],
                'equipment_names': equipment_names,
                'final_damage': round(combo['final_damage'], 2),
                'three_hit_total': round(combo['three_hit_total'], 2),
                'first_hit': round(combo['first_hit'], 2),
                'dot_damage': round(combo['dot_damage'], 2),
                'crit_rate': round(combo['crit_rate'], 1),
                'crit_damage': round(combo['crit_damage'], 1),
                'score': round(combo['score'], 2)
            })
        
        return jsonify({
            'success': True,
            'top_combinations': formatted_results,
            'total_combinations_tested': len(all_combinations),
            'optimization_type': optimization_type,
            'available_equipment_count': len(available_equipment)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 添加屬性點優化計算
@app.route('/optimize_stats', methods=['POST'])
def optimize_stats():
    """Calculate optimal stat distribution for given vitality"""
    data = request.get_json()
    
    try:
        player_level = data.get('playerLevel', 190)
        total_points = DamageCalculator.calculate_max_points(player_level)
        vitality = int(data.get('vitality', 0))
        selected_weapon = data.get('selectedWeapon', '')
        
        # Determine if magic or physical build based on weapon
        weapon_type = 'physical'
        if selected_weapon and WEAPON_DB.get(selected_weapon, {}).get('type') == 'staff':
            weapon_type = 'magic'
        
        remaining_points = total_points - vitality
        
        if remaining_points <= 0:
            return jsonify({
                'success': True,
                'recommendation': {
                    'strength': 0,
                    'intelligence': 0,
                    'dexterity': 0,
                    'defense': 0,
                    'reason': 'All points allocated to vitality'
                }
            })
        
        # For low levels, focus on main stat (STR/INT) over DEX
        # For high levels, balance between main stat and DEX
        # Defense is not recommended for damage optimization
        
        if player_level < 50:
            # Low level: 85% main stat, 15% DEX (no defense for damage)
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.85)
                dexterity = min(int(remaining_points * 0.15), 50)  # Cap at 50
                strength = 0
            else:
                strength = int(remaining_points * 0.85)
                dexterity = min(int(remaining_points * 0.15), 50)
                intelligence = 0
            defense = 0  # No points in defense for damage optimization
            
        elif player_level < 100:
            # Mid level: 75% main stat, 25% DEX (no defense for damage)
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.75)
                dexterity = min(int(remaining_points * 0.25), 50)
                strength = 0
            else:
                strength = int(remaining_points * 0.75)
                dexterity = min(int(remaining_points * 0.25), 50)
                intelligence = 0
            defense = 0  # No points in defense for damage optimization
            
        else:
            # High level: 65% main stat, 35% DEX (no defense for damage)
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.65)
                dexterity = min(int(remaining_points * 0.35), 50)
                strength = 0
            else:
                strength = int(remaining_points * 0.65)
                dexterity = min(int(remaining_points * 0.35), 50)
                intelligence = 0
            defense = 0  # No points in defense for damage optimization
        
        # Ensure we don't exceed point limit and distribute remaining points to main stat
        total_used = vitality + strength + intelligence + dexterity + defense
        remaining_after_optimization = total_points - total_used
        
        # Add remaining points to main stat
        if remaining_after_optimization > 0:
            if weapon_type == 'magic':
                intelligence += remaining_after_optimization
            else:
                strength += remaining_after_optimization
        
        return jsonify({
            'success': True,
            'recommendation': {
                'strength': strength,
                'intelligence': intelligence,
                'dexterity': dexterity,
                'defense': defense,
                'total_used': vitality + strength + intelligence + dexterity + defense,
                'remaining': total_points - (vitality + strength + intelligence + dexterity + defense),
                'weapon_type': weapon_type,
                'reason': f'Optimized for {weapon_type} damage at level {player_level}'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)