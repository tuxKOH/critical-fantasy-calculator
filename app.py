from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

class DamageCalculator:
    @staticmethod
    def calculate_damage(data):
        try:
            # Get base values
            damage_type = data.get('damageType', 'attack')
            min_damage = float(data.get('minDamage', 0))
            max_damage = float(data.get('maxDamage', 0))
            magic_damage = float(data.get('magicDamage', 0))
            crit_rate = float(data.get('critRate', 0)) / 100
            crit_damage = float(data.get('critDamage', 150)) / 100
            
            # Calculate average damage
            avg_damage = (min_damage + max_damage) / 2
            
            # Get potion effects
            has_magic_potion = data.get('magicPotion', False)
            has_attack_potion = data.get('attackPotion', False)
            has_golden_apple = data.get('goldenApple', False)
            
            # Apply potion effects to base stats
            effective_min_damage = min_damage
            effective_max_damage = max_damage
            effective_avg_damage = avg_damage
            effective_magic_damage = magic_damage
            
            if has_attack_potion:
                effective_min_damage *= 1.75
                effective_max_damage *= 1.75
                effective_avg_damage *= 1.75
            if has_golden_apple:
                effective_min_damage *= 1.5
                effective_max_damage *= 1.5
                effective_avg_damage *= 1.5
            if has_magic_potion:
                effective_magic_damage *= 1.75
            
            # Get selected equipment
            equipment = data.get('equipment', [])
            
            # Calculate base crit damage (using average damage)
            base_crit_multiplier = 1 + (crit_rate * (crit_damage - 1))
            total_damage = effective_avg_damage * base_crit_multiplier
            
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
            flame_set_count = 0
            burn_chance = 0
            has_volatile_gem = False
            
            # Check for flame set items and calculate burn chance
            flame_items = ['daybreak', 'evernight', 'volatile_gem']
            for item in flame_items:
                if item in equipment:
                    flame_set_count += 1
                    if item == 'daybreak':
                        burn_chance += 0.52
                    elif item == 'evernight':
                        burn_chance += 0.40
                    elif item == 'volatile_gem':
                        burn_chance += 0.11
                        has_volatile_gem = True
            
            # Apply flame set bonus
            if flame_set_count >= 2:
                burn_chance += 0.10
            
            # Calculate burn damage (uses potion-boosted magic damage)
            if burn_chance > 0:
                burn_damage = effective_magic_damage * 0.33 * 5
                if has_volatile_gem:
                    burn_damage += effective_magic_damage * 0.20
                dot_damage += burn_damage * min(burn_chance, 1)
            
            # Queenbee Crown (bleeding) - uses potion-boosted average damage
            if 'queenbee_crown' in equipment:
                bleeding_damage = effective_avg_damage * 0.25 * 5
                dot_damage += bleeding_damage * 0.26
            
            # Volatile Gem poison - uses potion-boosted magic damage
            if has_volatile_gem:
                poison_damage = effective_magic_damage * 0.40 * 5
                poison_damage += effective_magic_damage * 0.20
                dot_damage += poison_damage * 0.11
            
            # Blood Butcher - uses potion-boosted min damage
            if 'blood_butcher' in equipment:
                blood_damage = effective_min_damage * 0.05 * 9  # 9 seconds of 5% min damage per second
                dot_damage += blood_damage
            
            # Total final damage
            final_damage = total_damage + dot_damage
            
            return {
                'success': True,
                'min_damage': round(min_damage, 2),
                'max_damage': round(max_damage, 2),
                'avg_damage': round(avg_damage, 2),
                'effective_min_damage': round(effective_min_damage, 2),
                'effective_max_damage': round(effective_max_damage, 2),
                'effective_avg_damage': round(effective_avg_damage, 2),
                'effective_magic_damage': round(effective_magic_damage, 2),
                'crit_multiplied_damage': round(total_damage, 2),
                'dot_damage': round(dot_damage, 2),
                'final_damage': round(final_damage, 2),
                'effective_multiplier': round(final_damage / avg_damage, 2) if avg_damage > 0 else 0,
                'burn_chance': round(burn_chance * 100, 1),
                'flame_set_count': flame_set_count,
                'potion_effects': {
                    'magic_potion': has_magic_potion,
                    'attack_potion': has_attack_potion,
                    'golden_apple': has_golden_apple
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    result = DamageCalculator.calculate_damage(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)