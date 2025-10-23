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
    BASE_CRIT_DAMAGE = 100  # Base 100% crit damage
    MAX_DEX_CRIT = 50 * DEX_CRIT  # Max 50 dexterity points = 40% crit rate
    
    @staticmethod
    def calculate_stats_from_points(strength, vitality, intelligence, dexterity, defense):
        """Calculate base stats from attribute points"""
        # Cap dexterity crit contribution at 50 points
        effective_dex_crit = min(dexterity, 50) * DamageCalculator.DEX_CRIT
        
        return {
            'min_damage': strength * DamageCalculator.STR_DMG_MIN,
            'max_damage': strength * DamageCalculator.STR_DMG_MAX,
            'health': vitality * DamageCalculator.VIT_HP,
            'magic_damage': intelligence * DamageCalculator.INT_MAGIC,
            'crit_chance': DamageCalculator.BASE_CRIT_RATE + effective_dex_crit,
            'crit_damage': DamageCalculator.BASE_CRIT_DAMAGE,
            'shield': defense * DamageCalculator.DEF_SHIELD
        }
    
    @staticmethod
    def calculate_damage(data):
        try:
            # Get base values - either from manual input or calculated from points
            use_point_system = data.get('usePointSystem', False)
            selected_weapon = data.get('selectedWeapon', '')
            
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
                    strength, vitality, intelligence, dexterity, defense
                )
                
                min_damage = base_stats['min_damage']
                max_damage = base_stats['max_damage']
                magic_damage = base_stats['magic_damage']
                base_crit_rate = base_stats['crit_chance']
                base_crit_damage = base_stats['crit_damage']
            else:
                # Use manual input
                min_damage = float(data.get('minDamage', 0))
                max_damage = float(data.get('maxDamage', 0))
                magic_damage = float(data.get('magicDamage', 0))
                base_crit_rate = DamageCalculator.BASE_CRIT_RATE
                base_crit_damage = DamageCalculator.BASE_CRIT_DAMAGE
            
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
                weapon_stats = weapon_data.get('stats', {})
                min_damage += weapon_stats.get('atk_min', 0)
                max_damage += weapon_stats.get('atk_max', 0)
                magic_damage += weapon_stats.get('magic', 0)
                # Apply weapon crit stats
                base_crit_rate += weapon_stats.get('crit_chance', 0)
                base_crit_damage += weapon_stats.get('crit_damage', 0)
                
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
                stats = eq_data.get('stats', {})
                
                # Apply stat bonuses to BASE stats (so they get multiplied by potions)
                min_damage += stats.get('atk_min', 0)
                max_damage += stats.get('atk_max', 0)
                magic_damage += stats.get('magic', 0)
                total_crit_rate += stats.get('crit_chance', 0)
                total_crit_damage += stats.get('crit_damage', 0)
                
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
            else:  # attack
                base_damage = effective_avg_physical_damage
            
            # Calculate base crit damage
            crit_rate = min(total_crit_rate / 100, 1.0)  # Cap at 100%
            crit_damage_multiplier = total_crit_damage / 100
            base_crit_multiplier = 1 + (crit_rate * (crit_damage_multiplier - 1))
            total_damage = base_damage * base_crit_multiplier
            
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
                'calculated_stats': use_point_system
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

# Weapon Database
WEAPON_DB = {
    'wooden_sword': {
        'name': 'Wooden Sword',
        'type': 'sword',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing'
    },
    'wooden_staff': {
        'name': 'Wooden Staff', 
        'type': 'staff',
        'stats': {'magic': 4},
        'set': 'blessing'
    },
    'wooden_bow': {
        'name': 'Wooden Bow',
        'type': 'bow', 
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing'
    },
    'divine_blade': {
        'name': 'Divine Blade',
        'type': 'sword',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer'
    },
    'forest_dweller_staff': {
        'name': 'Forest Dweller\'s Staff',
        'type': 'staff',
        'stats': {'magic': 60},
        'set': 'explorer'
    },
    'forest_dweller_bow': {
        'name': 'Forest Dweller\'s Bow',
        'type': 'bow',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer'
    },
    'crescendo_scythe': {
        'name': 'Crescendo Scythe',
        'type': 'scythe',
        'stats': {'atk_min': 75, 'atk_max': 75},
        'set': 'library_ruina'
    },
    'emerald_staff': {
        'name': 'Emerald Staff',
        'type': 'staff', 
        'stats': {'magic': 500}
    },
    'winter_howl': {
        'name': 'Winter Howl',
        'type': 'sword',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'wolf_howl'
    },
    'eventide': {
        'name': 'Eventide',
        'type': 'bow',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'queen_bee'
    }
}

# Equipment Database (保持不变)
EQUIPMENT_DB = {
    # Tier I
    'hunting_dagger': {
        'name': 'Hunting Dagger',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'set': 'explorer'
    },
    'sharpener_rock': {
        'name': 'Sharpener\'s Rock',
        'tier': 'I', 
        'stats': {'crit_chance': 5, 'crit_damage': 10},
        'special_effects': {}
    },
    
    # Tier II
    'ancient_hammer': {
        'name': 'Ancient Hammer',
        'tier': 'II',
        'stats': {'atk_min': 50, 'atk_max': 50},
        'special_effects': {}
    },
    'forest_dweller_axe': {
        'name': 'Forest Dweller\'s Axe',
        'tier': 'II',
        'stats': {'atk_min': 40, 'atk_max': 40, 'crit_chance': 5},
        'special_effects': {'bleed_chance': 0.02},
        'set': 'forest_dweller'
    },
    'volatile_crystal': {
        'name': 'Volatile Crystal',
        'tier': 'II',
        'stats': {'magic': 45},
        'special_effects': {}
    },
    
    # Tier III
    'alderite_axe': {
        'name': 'Alderite Axe',
        'tier': 'III',
        'stats': {'atk_min': 175, 'atk_max': 194, 'magic': 140, 'crit_chance': 5},
        'special_effects': {}
    },
    'aqua_crystal': {
        'name': 'Aqua Crystal',
        'tier': 'III',
        'stats': {'magic': 110},
        'special_effects': {}
    },
    'arcane_spellbook': {
        'name': 'Arcane Spellbook',
        'tier': 'III',
        'stats': {'magic': 100},
        'special_effects': {}
    },
    'corrupted_fang': {
        'name': 'Corrupted Fang',
        'tier': 'III',
        'stats': {'magic': 130, 'atk_min': 35, 'atk_max': 35},
        'special_effects': {}
    },
    'daybreak': {
        'name': 'Daybreak',
        'tier': 'III',
        'stats': {'atk_min': 100, 'atk_max': 111},
        'special_effects': {'burn_chance': 0.52},
        'set': 'flame'
    },
    'enchanted_blade': {
        'name': 'Enchanted Blade',
        'tier': 'III',
        'stats': {'atk_min': 125, 'atk_max': 125, 'magic': 100},
        'special_effects': {}
    },
    
    # Tier IV
    'atlantis_armor': {
        'name': 'Atlantis Armor',
        'tier': 'IV',
        'stats': {'health': 75, 'shield': 10},
        'special_effects': {}
    },
    'bee_breastplate': {
        'name': 'Bee Breastplate',
        'tier': 'IV',
        'stats': {'health': 460, 'shield': 40},
        'special_effects': {},
        'set': 'queen_bee'
    },
    'black_wolf_necklace': {
        'name': 'Black Wolf Necklace',
        'tier': 'IV',
        'stats': {'atk_min': 225, 'atk_max': 249, 'crit_chance': 15, 'crit_damage': 22},
        'special_effects': {},
        'set': 'wolf_howl'
    },
    'blood_butcher': {
        'name': 'Blood Butcher',
        'tier': 'IV',
        'stats': {'atk_min': 250, 'atk_max': 277, 'crit_chance': 16},
        'special_effects': {'blood_butcher': True},
        'set': 'crimson'
    },
    'crimson_slime_fang': {
        'name': 'Crimson Slime Fang',
        'tier': 'IV',
        'stats': {'magic': 220, 'crit_damage': 27},
        'special_effects': {},
        'set': 'crimson'
    },
    'cursed_spellbook': {
        'name': 'Cursed Spellbook',
        'tier': 'IV',
        'stats': {'magic': 400},
        'special_effects': {'damage_multiplier': 1.3},
        'set': 'crimson'
    },
    'dual_sword': {
        'name': 'Dual Sword',
        'tier': 'IV',
        'stats': {'atk_min': 135, 'atk_max': 149},
        'special_effects': {'double_damage_chance': 0.15}
    },
    'evernight': {
        'name': 'Evernight',
        'tier': 'IV',
        'stats': {'atk_min': 450, 'atk_max': 450},
        'special_effects': {'burn_chance': 0.40},
        'set': 'flame'
    },
    'forest_crown': {
        'name': 'Forest Crown',
        'tier': 'IV',
        'stats': {'health': 775, 'shield': 275},
        'special_effects': {}
    },
    'volcanic_axe': {
        'name': 'Volcanic Axe',
        'tier': 'IV',
        'stats': {'atk_min': 280, 'atk_max': 280},
        'special_effects': {'burn_chance': 0.05},
        'set': 'wolf_howl'
    },
    'winter_spirit': {
        'name': 'Winter Spirit',
        'tier': 'IV',
        'stats': {'atk_min': 200, 'atk_max': 200, 'health': 50},
        'special_effects': {'freeze_chance': 0.02}
    },
    
    # Tier V
    'queenbee_crown': {
        'name': 'Queen Bee\'s Crown',
        'tier': 'V',
        'stats': {'atk_min': 800, 'atk_max': 888, 'crit_chance': 20, 'crit_damage': 80},
        'special_effects': {'bleed_chance': 0.26},
        'set': 'queen_bee'
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
        'set': 'flame'
    }
}

@app.route('/')
def index():
    return render_template('index.html', equipment_db=EQUIPMENT_DB, weapon_db=WEAPON_DB)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    result = DamageCalculator.calculate_damage(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)