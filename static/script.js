// Critical Fantasy Damage Calculator JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let selectedEquipment = [];
    const maxEquipment = 3;
    let equipmentDatabase = {};
    let weaponDatabase = {};
    let currentTierFilter = 'all';
    let currentSearchFilter = '';
    let currentResult = null;
    let currentOptimizationType = 'final_damage';
    let currentVersion = 'current';
    
    const setIndicators = {
        'flame': { class: 'flame-set-indicator', text: 'Flame' },
        'wolf_howl': { class: 'wolf-set-indicator', text: 'Wolf' },
        'crimson': { class: 'crimson-set-indicator', text: 'Crimson' },
        'queen_bee': { class: 'queen-bee-set-indicator', text: 'Queen Bee' },
        'explorer': { class: 'explorer-set-indicator', text: 'Explorer' },
        'forest_dweller': { class: 'forest-set-indicator', text: 'Forest' },
        'library_ruina': { class: 'library-set-indicator', text: 'Library' },
        'blessing': { class: 'blessing-set-indicator', text: 'Blessing' }
    };
    
    function initialize() {
        equipmentDatabase = window.equipmentDb || {};
        weaponDatabase = window.weaponDb || {};
        
        initializeEquipment();
        setupEventListeners();
        updatePoints();
        updateWeaponInfo();
        calculateDamage();
    }
    
    function initializeEquipment() {
        const equipmentList = document.getElementById('equipmentList');
        equipmentList.innerHTML = '';
        
        Object.entries(equipmentDatabase).forEach(([id, data]) => {
            if (filterEquipmentItem(id, data)) {
                const item = createEquipmentItem(id, data);
                equipmentList.appendChild(item);
            }
        });
    }
    
    function createEquipmentItem(id, data) {
        const div = document.createElement('div');
        div.className = 'equipment-item';
        div.setAttribute('data-id', id);
        div.setAttribute('data-tier', data.tier);
        
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const levelReq = data.level_req || 0;
        const meetsLevelReq = levelReq <= playerLevel;
        
        if (!meetsLevelReq) {
            div.style.opacity = '0.6';
        }
        
        const isOldItem = id.includes('_old');
        if (isOldItem) {
            div.classList.add('equipment-old');
        }
        
        const stats = [];
        if (data.stats.atk_min !== undefined && data.stats.atk_max !== undefined) {
            stats.push(`ATK: ${data.stats.atk_min}-${data.stats.atk_max}`);
        } else if (data.stats.atk_min !== undefined) {
            stats.push(`ATK: ${data.stats.atk_min}`);
        }
        if (data.stats.magic !== undefined) {
            stats.push(`Magic: ${data.stats.magic}`);
        }
        if (data.stats.crit_chance !== undefined) {
            stats.push(`Crit: +${data.stats.crit_chance}%`);
        }
        if (data.stats.crit_damage !== undefined) {
            stats.push(`Crit DMG: +${data.stats.crit_damage}%`);
        }
        if (data.stats.health !== undefined) {
            stats.push(`HP: +${data.stats.health}`);
        }
        if (data.stats.shield !== undefined) {
            stats.push(`Shield: +${data.stats.shield}`);
        }
        
        const effects = [];
        if (data.special_effects && data.special_effects.damage_multiplier) {
            effects.push(`${data.special_effects.damage_multiplier}x Damage`);
        }
        if (data.special_effects && data.special_effects.double_damage_chance) {
            effects.push(`${data.special_effects.double_damage_chance * 100}% 2x Damage`);
        }
        if (data.special_effects && data.special_effects.burn_chance) {
            effects.push(`+${data.special_effects.burn_chance * 100}% Burn`);
        }
        if (data.special_effects && data.special_effects.bleed_chance) {
            effects.push(`+${data.special_effects.bleed_chance * 100}% Bleed`);
        }
        if (data.special_effects && data.special_effects.poison_chance) {
            effects.push(`+${data.special_effects.poison_chance * 100}% Poison`);
        }
        if (data.special_effects && data.special_effects.blood_butcher) {
            effects.push('Blood Butcher Debuff');
        }
        if (data.special_effects && data.special_effects.freeze_chance) {
            effects.push(`+${data.special_effects.freeze_chance * 100}% Freeze`);
        }
        if (data.special_effects && data.special_effects.dot_bonus) {
            effects.push('+20% Magic to DoT');
        }
        
        let setIndicator = '';
        if (data.set && setIndicators[data.set]) {
            const setInfo = setIndicators[data.set];
            setIndicator = `<span class="${setInfo.class} set-indicators">${setInfo.text}</span>`;
        }
        
        let versionInfo = '';
        if (isOldItem) {
            versionInfo = `<span class="old-version-tag">OLD</span>`;
        }
        
        let levelInfo = '';
        if (levelReq > 0) {
            levelInfo = `<span style="color: ${meetsLevelReq ? '#28a745' : '#dc3545'}; font-size: 0.8em;">Lv. ${levelReq}</span>`;
        }
        
        let imageHtml = '';
        if (data.image_url && data.image_url.trim()) {
            const cleanUrl = data.image_url.trim();
            imageHtml = `
                <div class="equipment-image">
                    <img src="${cleanUrl}" alt="${data.name}" 
                         onerror="this.style.display='none'"
                         style="max-width: 40px; max-height: 40px; object-fit: contain; margin-right: 8px;">
                </div>
            `;
        }
        
        div.innerHTML = `
            <div class="equipment-header">
                ${imageHtml}
                <div style="flex: 1;">
                    <div class="equipment-name">${data.name} ${versionInfo} ${levelInfo} ${setIndicator}</div>
                    <div class="equipment-stats">${stats.join(', ')}</div>
                    <div class="equipment-effects">${effects.join(', ')}</div>
                </div>
                <div class="equipment-tier">T${data.tier}</div>
            </div>
        `;
        
        if (meetsLevelReq) {
            div.addEventListener('click', () => toggleEquipmentSelection(id));
        } else {
            div.style.cursor = 'not-allowed';
            div.title = `Requires Level ${levelReq}`;
        }
        
        return div;
    }
    
    function filterEquipmentItem(id, data) {
        const matchesSearch = data.name.toLowerCase().includes(currentSearchFilter.toLowerCase()) ||
                            id.toLowerCase().includes(currentSearchFilter.toLowerCase());
        const matchesTier = currentTierFilter === 'all' || data.tier === currentTierFilter;
        
        const isOldItem = id.includes('_old');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const matchesVersion = useOldVersion ? 
            (isOldItem || !equipmentDatabase[id + '_old']) :
            !isOldItem;
        
        return matchesSearch && matchesTier && matchesVersion;
    }
    
    function filterEquipment() {
        currentSearchFilter = document.getElementById('equipmentSearch').value;
        initializeEquipment();
    }
    
    function filterByTier(tier) {
        currentTierFilter = tier;
        document.querySelectorAll('.tier-filter').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        initializeEquipment();
    }
    
    function toggleEquipmentSelection(id) {
        const eqData = equipmentDatabase[id];
        if (!eqData) return;
        
        const isOldItem = id.includes('_old');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        
        const baseId = isOldItem ? id.replace('_old', '') : id;
        const oppositeId = isOldItem ? baseId : baseId + '_old';
        
        if (selectedEquipment.includes(oppositeId)) {
            alert(`Cannot select both old and new versions of ${eqData.name.replace(' (Old)', '').replace(' (New)', '')}!`);
            return;
        }
        
        if (selectedEquipment.includes(id)) {
            selectedEquipment = selectedEquipment.filter(eq => eq !== id);
            document.querySelector(`.equipment-item[data-id="${id}"]`).classList.remove('selected');
        } else {
            if (selectedEquipment.length < maxEquipment) {
                selectedEquipment.push(id);
                document.querySelector(`.equipment-item[data-id="${id}"]`).classList.add('selected');
            } else {
                alert('You can only select up to 3 equipment items!');
            }
        }
        updateSelectedEquipmentDisplay();
        calculateDamage();
    }
    
    function updateEquipmentDisplay() {
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        initializeEquipment();
        
        selectedEquipment = selectedEquipment.filter(id => {
            const eqData = equipmentDatabase[id];
            if (!eqData) return false;
            
            const meetsLevelReq = (eqData.level_req || 0) <= playerLevel;
            if (!meetsLevelReq) {
                const element = document.querySelector(`.equipment-item[data-id="${id}"]`);
                if (element) element.classList.remove('selected');
                return false;
            }
            
            return true;
        });
        
        updateSelectedEquipmentDisplay();
        addPointLimits();
        updatePoints();
        calculateDamage();
    }
    
    function updateSelectedEquipmentDisplay() {
        const container = document.getElementById('selectedEquipment');
        container.innerHTML = '';
        
        selectedEquipment.forEach(id => {
            const data = equipmentDatabase[id];
            if (data) {
                const div = document.createElement('div');
                div.className = 'selected-item';
                const isOldItem = id.includes('_old');
                const oldTag = isOldItem ? '<span style="color:#dc3545; font-size:0.8em;">(OLD)</span>' : '';
                div.innerHTML = `
                    ${data.name} ${oldTag}
                    <button class="remove-item" data-id="${id}">×</button>
                `;
                container.appendChild(div);
            }
        });
        
        container.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                removeEquipment(id);
            });
        });
    }
    
    function removeEquipment(id) {
        selectedEquipment = selectedEquipment.filter(eq => eq !== id);
        document.querySelector(`.equipment-item[data-id="${id}"]`).classList.remove('selected');
        updateSelectedEquipmentDisplay();
        calculateDamage();
    }
    
    function toggleGameVersion(version) {
        const toggleCurrent = document.getElementById('toggleCurrent');
        const toggleOld = document.getElementById('toggleOld');
        const useOldVersion = version === 'old';
        
        toggleCurrent.classList.toggle('active', !useOldVersion);
        toggleOld.classList.toggle('active', useOldVersion);
        
        currentVersion = version;
        
        updateEquipmentDisplay();
    }
    
    function updateWeaponInfo() {
        const weaponSelect = document.getElementById('weaponSelect');
        const weaponInfo = document.getElementById('weaponInfo');
        const selectedWeapon = weaponSelect.value;
        
        if (selectedWeapon && weaponDatabase[selectedWeapon]) {
            const weapon = weaponDatabase[selectedWeapon];
            const stats = [];
            
            if (weapon.stats.atk_min !== undefined && weapon.stats.atk_max !== undefined) {
                stats.push(`ATK: ${weapon.stats.atk_min}-${weapon.stats.atk_max}`);
            } else if (weapon.stats.atk_min !== undefined) {
                stats.push(`ATK: ${weapon.stats.atk_min}`);
            }
            if (weapon.stats.magic !== undefined) {
                stats.push(`Magic: ${weapon.stats.magic}`);
            }
            if (weapon.stats.crit_chance !== undefined) {
                stats.push(`Crit: +${weapon.stats.crit_chance}%`);
            }
            if (weapon.stats.crit_damage !== undefined) {
                stats.push(`Crit DMG: +${weapon.stats.crit_damage}%`);
            }
            
            const damageType = weapon.type === 'staff' ? 'Magic' : 'Physical';
            
            let setInfo = '';
            if (weapon.set && setIndicators[weapon.set]) {
                const setData = setIndicators[weapon.set];
                setInfo = `<span class="${setData.class} set-indicators">${setData.text}</span>`;
            }
            
            const levelReq = weapon.level_req || 0;
            let levelInfo = '';
            if (levelReq > 0) {
                levelInfo = `<br><small>Level Requirement: ${levelReq}</small>`;
            }
            
            let furiosoInfo = '';
            if (selectedWeapon === 'furioso') {
                furiosoInfo = `<br><small style="color: #4a90e2;">Updated: 3.7x total damage + bleed on 4th hit</small>`;
            }
            
            let imageHtml = '';
            if (weapon.image_url && weapon.image_url.trim()) {
                imageHtml = `
                    <div style="float: left; margin-right: 10px; margin-bottom: 5px;">
                        <img src="${weapon.image_url.trim()}" alt="${weapon.name}" 
                             style="max-width: 60px; max-height: 60px; object-fit: contain; border-radius: 4px; border: 1px solid #e0e0e0;"
                             onerror="this.style.display='none'">
                    </div>
                `;
            }
            
            weaponInfo.innerHTML = `
                <div style="overflow: hidden;">
                    ${imageHtml}
                    <div>
                        <strong>${weapon.name}</strong> (${damageType}) ${setInfo}${levelInfo}${furiosoInfo}<br>
                        ${stats.join(', ')}
                    </div>
                </div>
            `;
        } else {
            weaponInfo.innerHTML = 'No weapon selected';
        }
    }
    
    function toggleInputSystem(system) {
        document.getElementById('togglePoints').classList.toggle('active', system === 'points');
        document.getElementById('toggleManual').classList.toggle('active', system === 'manual');
        document.getElementById('pointsSection').style.display = system === 'points' ? 'block' : 'none';
        document.getElementById('manualSection').style.display = system === 'manual' ? 'block' : 'none';
        
        calculateDamage();
    }
    
    function updatePoints() {
        const strength = parseInt(document.getElementById('strength').value) || 0;
        const vitality = parseInt(document.getElementById('vitality').value) || 0;
        const intelligence = parseInt(document.getElementById('intelligence').value) || 0;
        const dexterity = parseInt(document.getElementById('dexterity').value) || 0;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        const total = strength + vitality + intelligence + dexterity;
        const maxPoints = playerLevel * 2;
        
        document.getElementById('totalPoints').textContent = total;
        document.getElementById('remainingPoints').textContent = maxPoints - total;
        document.getElementById('maxPoints').textContent = maxPoints;
        
        calculateDamage();
    }
    
    function setOptimizationType(type) {
        currentOptimizationType = type;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }
    
    function calculateDamage() {
        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const classLevel = parseInt(document.getElementById('classLevel').value) || 15;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
            classLevel: classLevel,
            equipment: selectedEquipment,
            magicPotion: document.getElementById('magicPotion').checked,
            attackPotion: document.getElementById('attackPotion').checked,
            goldenApple: document.getElementById('goldenApple').checked
        };
        
        if (usePointSystem) {
            data.strength = parseInt(document.getElementById('strength').value) || 0;
            data.vitality = parseInt(document.getElementById('vitality').value) || 0;
            data.intelligence = parseInt(document.getElementById('intelligence').value) || 0;
            data.dexterity = parseInt(document.getElementById('dexterity').value) || 0;
            data.defense = 0;
        } else {
            data.minDamage = document.getElementById('minDamage').value;
            data.maxDamage = document.getElementById('maxDamage').value;
            data.magicDamage = document.getElementById('magicDamage').value;
            data.critRate = document.getElementById('critRate').value;
            data.critDamage = document.getElementById('critDamage').value;
        }
        
        if (!usePointSystem && (!data.minDamage || !data.maxDamage || !data.magicDamage)) {
            return;
        }
        
        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                currentResult = result;
                
                const classLevelBadge = document.getElementById('classLevelBadge');
                if (result.class_level && result.class_multiplier) {
                    classLevelBadge.textContent = `Class: ${result.class_multiplier}x`;
                    classLevelBadge.style.display = 'inline-block';
                } else {
                    classLevelBadge.style.display = 'none';
                }
                
                document.getElementById('resultBaseDamage').textContent = result.base_damage.toLocaleString();
                document.getElementById('resultDot').textContent = result.dot_damage.toLocaleString();
                document.getElementById('resultFinal').textContent = result.final_damage.toLocaleString();
                
                document.getElementById('resultDamageAfterCrit').textContent = result.damage_after_crit.toLocaleString();
                
                document.getElementById('resultMultiplier').textContent = result.effective_multiplier + 'x';
                document.getElementById('resultDamageType').textContent = result.damage_type === 'magic' ? 'Magic' : 'Physical';
                
                if (result.ten_second_damage) {
                    document.getElementById('resultTenSecond').textContent = result.ten_second_damage.total_damage.toLocaleString();
                    document.getElementById('resultMechanic').textContent = result.ten_second_damage.mechanic;
                }
                
                if (result.calculated_stats && result.player_stats) {
                    document.getElementById('playerStatsSection').style.display = 'block';
                    
                    let dotStatsHtml = '';
                    if (result.burn_chance > 0 || result.bleed_chance > 0 || result.poison_chance > 0 || result.has_blood_butcher) {
                        dotStatsHtml = `
                            <div class="result-item">
                                <span class="result-label">DoT Attributes:</span>
                                <span class="result-value">
                                    ${result.burn_chance > 0 ? `Burn: ${result.burn_chance}%` : ''}
                                    ${result.bleed_chance > 0 ? `Bleed: ${result.bleed_chance}%` : ''}
                                    ${result.poison_chance > 0 ? `Poison: ${result.poison_chance}%` : ''}
                                    ${result.has_blood_butcher ? 'Blood Butcher' : ''}
                                </span>
                            </div>
                        `;
                    }
                    
                    document.getElementById('playerStatsContent').innerHTML = `
                        <div class="result-item">
                            <span class="result-label">HP:</span>
                            <span class="result-value">${(result.player_stats.health || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Shield:</span>
                            <span class="result-value">${(result.player_stats.shield || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Total HP:</span>
                            <span class="result-value">${(result.player_stats.total_hp || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Attack Range (Post-potion):</span>
                            <span class="result-value">${(result.player_stats.min_damage || 0).toLocaleString()} - ${(result.player_stats.max_damage || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Magic Damage (Post-potion):</span>
                            <span class="result-value">${(result.player_stats.magic_damage || 0).toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Attack Multiplier:</span>
                            <span class="result-value">${(result.player_stats.attack_multiplier || 1.0).toFixed(2)}x</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Crit Rate:</span>
                            <span class="result-value">${result.crit_rate.toLocaleString()}%</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Crit Damage:</span>
                            <span class="result-value">${result.crit_damage.toLocaleString()}%</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Class Level:</span>
                            <span class="result-value">${result.class_level} (${result.class_multiplier}x)</span>
                        </div>
                        ${dotStatsHtml}
                    `;
                } else {
                    document.getElementById('playerStatsSection').style.display = 'none';
                }
                
                document.getElementById('resultSection').style.display = 'block';
            } else {
                console.error('Calculation failed:', result.error);
            }
        })
        .catch(error => {
            console.error('Error calculating damage:', error);
        });
    }
    
    function optimizeDamageAdvanced() {
        const optimizeBtn = document.getElementById('optimizeBtn');
        optimizeBtn.textContent = 'Calculating...';
        optimizeBtn.disabled = true;

        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const classLevel = parseInt(document.getElementById('classLevel').value) || 15;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
            classLevel: classLevel,
            magicPotion: document.getElementById('magicPotion').checked,
            attackPotion: document.getElementById('attackPotion').checked,
            goldenApple: document.getElementById('goldenApple').checked,
            optimizationType: currentOptimizationType
        };
        
        if (usePointSystem) {
            data.strength = parseInt(document.getElementById('strength').value) || 0;
            data.vitality = parseInt(document.getElementById('vitality').value) || 0;
            data.intelligence = parseInt(document.getElementById('intelligence').value) || 0;
            data.dexterity = parseInt(document.getElementById('dexterity').value) || 0;
            data.defense = 0;
        } else {
            data.minDamage = document.getElementById('minDamage').value;
            data.maxDamage = document.getElementById('maxDamage').value;
            data.magicDamage = document.getElementById('magicDamage').value;
            data.critRate = document.getElementById('critRate').value;
            data.critDamage = document.getElementById('critDamage').value;
        }
        
        fetch('/optimize_advanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                displayOptimizationResults(result);
            } else {
                alert('Optimization failed: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error optimizing damage:', error);
            alert('Optimization failed due to an error.');
        })
        .finally(() => {
            optimizeBtn.textContent = 'Find Best Combinations';
            optimizeBtn.disabled = false;
        });
    }

    function displayOptimizationResults(result) {
        const section = document.getElementById('optimizeResultSection');
        const content = document.getElementById('optimizeResultsContent');
        
        let html = `<p>Tested ${result.total_combinations_tested.toLocaleString()} combinations (${result.available_equipment_count} available equipment)</p>`;
        html += `<p>Version: ${result.version} ${result.allows_mixed_versions ? '(Mixed versions allowed)' : ''}</p>`;
        
        const scoreLabel = {
            'final_damage': 'Final Damage',
            'ten_second': '10s Total Damage', 
            'dot': 'DoT Damage'
        }[result.optimization_type] || 'Score';
        
        result.top_combinations.forEach((combo, index) => {
            const hasOldItems = combo.equipment_ids.some(id => id.includes('_old'));
            const versionTag = hasOldItems ? '<span style="color: #dc3545; font-size: 0.9em;">(Mixed)</span>' : '';
            
            html += `
                <div class="optimize-combo">
                    <h4>#${index + 1} - ${scoreLabel}: ${combo.score.toLocaleString()} ${versionTag}</h4>
                    <p><strong>Final Damage:</strong> ${combo.final_damage.toLocaleString()}</p>
                    <p><strong>10s Total Damage:</strong> ${combo.ten_second_total.toLocaleString()}</p>
                    <p><strong>DoT Damage:</strong> ${combo.dot_damage.toLocaleString()}</p>
                    <p><strong>Equipment:</strong> ${combo.equipment_names.join(', ')}</p>
                    <p><strong>Crit:</strong> ${combo.crit_rate}% rate, ${combo.crit_damage}% damage</p>
                    <button class="apply-combo-btn" data-ids='${JSON.stringify(combo.equipment_ids)}'>Apply This Combo</button>
                </div>
            `;
        });
        
        content.innerHTML = html;
        section.style.display = 'block';
        
        content.querySelectorAll('.apply-combo-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const equipmentIds = JSON.parse(this.getAttribute('data-ids'));
                applyOptimizedCombo(equipmentIds);
            });
        });
    }

    function applyOptimizedCombo(equipmentIds) {
        selectedEquipment.forEach(id => {
            const element = document.querySelector(`.equipment-item[data-id="${id}"]`);
            if (element) element.classList.remove('selected');
        });
        
        selectedEquipment = [...equipmentIds];
        selectedEquipment.forEach(id => {
            const element = document.querySelector(`.equipment-item[data-id="${id}"]`);
            if (element) element.classList.add('selected');
        });
        
        updateSelectedEquipmentDisplay();
        calculateDamage();
        
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
    }
    
    function optimizeStats() {
        const vitality = parseInt(document.getElementById('vitality').value) || 0;
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        const data = {
            vitality: vitality,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel
        };
        
        fetch('/optimize_stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                applyOptimizedStats(result.recommendation);
            } else {
                alert('Stats optimization failed: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error optimizing stats:', error);
            alert('Stats optimization failed due to an error.');
        });
    }

    function applyOptimizedStats(recommendation) {
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        document.getElementById('strength').value = recommendation.strength;
        document.getElementById('intelligence').value = recommendation.intelligence;
        document.getElementById('dexterity').value = recommendation.dexterity;
        
        updatePoints();
        calculateDamage();
        
        alert(`Optimized stats applied!\n${recommendation.reason}\n\nStrength: ${recommendation.strength}\nIntelligence: ${recommendation.intelligence}\nDexterity: ${recommendation.dexterity}\n\nTotal Used: ${recommendation.total_used}/${playerLevel * 2}`);
    }
    
    function showExtraData() {
        if (!currentResult) return;
        
        const modal = document.getElementById('extraDataModal');
        const content = document.getElementById('extraDataContent');
        
        const details = currentResult.calculation_details;
        
        let html = `
            <div class="detail-section">
                <h4>Class Level</h4>
                <div class="detail-item">
                    <span>Level:</span>
                    <span>${currentResult.class_level}</span>
                </div>
                <div class="detail-item">
                    <span>Multiplier:</span>
                    <span>${currentResult.class_multiplier}x</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Base Stats</h4>
                <div class="detail-item">
                    <span>Min Damage:</span>
                    <span>${details.base_stats.min_damage.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span>Max Damage:</span>
                    <span>${details.base_stats.max_damage.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span>Magic Damage:</span>
                    <span>${details.base_stats.magic_damage.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span>Base Crit Rate:</span>
                    <span>${details.base_stats.base_crit_rate.toLocaleString()}%</span>
                </div>
                <div class="detail-item">
                    <span>Base Crit Damage:</span>
                    <span>${details.base_stats.base_crit_damage.toLocaleString()}%</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>After Equipment</h4>
                <div class="detail-item">
                    <span>Total Crit Rate:</span>
                    <span>${details.after_equipment.total_crit_rate.toLocaleString()}%</span>
                </div>
                <div class="detail-item">
                    <span>Total Crit Damage:</span>
                    <span>${details.after_equipment.total_crit_damage.toLocaleString()}%</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Crit Calculation</h4>
                <div class="detail-item">
                    <span>Effective Crit Rate:</span>
                    <span>${details.crit_calculation.crit_rate_percent.toFixed(1)}%</span>
                </div>
                <div class="detail-item">
                    <span>Crit Damage Multiplier:</span>
                    <span>${details.crit_calculation.crit_damage_multiplier.toFixed(2)}x</span>
                </div>
                <div class="detail-item">
                    <span>Crit Base Damage:</span>
                    <span>${details.crit_calculation.crit_base_damage.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span>Expected Damage:</span>
                    <span>${details.crit_calculation.expected_damage.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span>Damage After Crit:</span>
                    <span>${details.crit_calculation.damage_after_crit.toLocaleString()}</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Set Bonuses Applied</h4>
        `;
        
        if (currentResult.set_bonuses_applied) {
            Object.entries(currentResult.set_bonuses_applied).forEach(([set, applied]) => {
                if (applied) {
                    html += `<div class="detail-item">
                        <span>${set.replace('_', ' ').toUpperCase()}:</span>
                        <span>✓ Active</span>
                    </div>`;
                }
            });
        }
        
        html += `</div>`;
        
        if (currentResult.dot_damage > 0 && details.dot_calculation) {
            html += `
                <div class="detail-section">
                    <h4>DoT Calculations</h4>
                    <div class="detail-item">
                        <span>Burn Chance:</span>
                        <span>${(details.dot_calculation.burn_chance || 0).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span>Bleed Chance:</span>
                        <span>${(details.dot_calculation.bleed_chance || 0).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span>Poison Chance:</span>
                        <span>${(details.dot_calculation.poison_chance || 0).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span>Blood Butcher:</span>
                        <span>${details.dot_calculation.has_blood_butcher ? '✓ Active' : 'Not Active'}</span>
                    </div>
                </div>
            `;
        }
        
        content.innerHTML = html;
        modal.style.display = 'block';
    }
    
    function closeExtraData() {
        document.getElementById('extraDataModal').style.display = 'none';
    }
    
    function addPointLimits() {
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const maxPoints = playerLevel * 2;
        
        document.getElementById('strength').max = maxPoints;
        document.getElementById('vitality').max = maxPoints;
        document.getElementById('intelligence').max = maxPoints;
        document.getElementById('dexterity').max = 50;
    }
    
    // ==================== 後端圖片生成功能 ====================
    
    // 分享計算結果為圖片
    function shareResultAsImage() {
        if (!currentResult) {
            showNotification('Please calculate damage first', 'error');
            return;
        }
        
        const shareBtn = document.getElementById('shareResultBtn');
        const originalText = shareBtn.textContent;
        shareBtn.textContent = 'Generating Image...';
        shareBtn.disabled = true;
        
        // 收集當前配置數據
        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const classLevel = parseInt(document.getElementById('classLevel').value) || 15;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
            classLevel: classLevel,
            equipment: selectedEquipment,
            magicPotion: document.getElementById('magicPotion').checked,
            attackPotion: document.getElementById('attackPotion').checked,
            goldenApple: document.getElementById('goldenApple').checked
        };
        
        if (usePointSystem) {
            data.strength = parseInt(document.getElementById('strength').value) || 0;
            data.vitality = parseInt(document.getElementById('vitality').value) || 0;
            data.intelligence = parseInt(document.getElementById('intelligence').value) || 0;
            data.dexterity = parseInt(document.getElementById('dexterity').value) || 0;
            data.defense = 0;
        } else {
            data.minDamage = document.getElementById('minDamage').value;
            data.maxDamage = document.getElementById('maxDamage').value;
            data.magicDamage = document.getElementById('magicDamage').value;
            data.critRate = document.getElementById('critRate').value;
            data.critDamage = document.getElementById('critDamage').value;
        }
        
        // 發送請求生成圖片
        fetch('/generate_result_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                // 創建下載鏈接
                const timestamp = new Date().getTime();
                return response.blob().then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `damage-calc-result-${timestamp}.png`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showNotification('Image generated successfully!', 'success');
                });
            } else {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to generate image');
                });
            }
        })
        .catch(error => {
            console.error('Error generating image:', error);
            showNotification(`Failed to generate image: ${error.message}`, 'error');
        })
        .finally(() => {
            shareBtn.textContent = originalText;
            shareBtn.disabled = false;
        });
    }
    
    // 分享優化排名為圖片
    function shareOptimizationAsImage() {
        const optimizeResults = document.getElementById('optimizeResultsContent');
        if (!optimizeResults || optimizeResults.children.length === 0) {
            showNotification('No optimization results to share', 'error');
            return;
        }
        
        const shareBtn = document.getElementById('shareOptimizeBtn');
        const originalText = shareBtn.textContent;
        shareBtn.textContent = 'Generating Image...';
        shareBtn.disabled = true;
        
        // 收集當前配置數據
        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const classLevel = parseInt(document.getElementById('classLevel').value) || 15;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
            classLevel: classLevel,
            magicPotion: document.getElementById('magicPotion').checked,
            attackPotion: document.getElementById('attackPotion').checked,
            goldenApple: document.getElementById('goldenApple').checked,
            optimizationType: currentOptimizationType
        };
        
        if (usePointSystem) {
            data.strength = parseInt(document.getElementById('strength').value) || 0;
            data.vitality = parseInt(document.getElementById('vitality').value) || 0;
            data.intelligence = parseInt(document.getElementById('intelligence').value) || 0;
            data.dexterity = parseInt(document.getElementById('dexterity').value) || 0;
            data.defense = 0;
        } else {
            data.minDamage = document.getElementById('minDamage').value;
            data.maxDamage = document.getElementById('maxDamage').value;
            data.magicDamage = document.getElementById('magicDamage').value;
            data.critRate = document.getElementById('critRate').value;
            data.critDamage = document.getElementById('critDamage').value;
        }
        
        // 發送請求生成圖片
        fetch('/generate_ranking_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                // 創建下載鏈接
                const timestamp = new Date().getTime();
                return response.blob().then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `damage-calc-ranking-${timestamp}.png`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showNotification('Ranking image generated successfully!', 'success');
                });
            } else {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to generate image');
                });
            }
        })
        .catch(error => {
            console.error('Error generating ranking image:', error);
            showNotification(`Failed to generate ranking image: ${error.message}`, 'error');
        })
        .finally(() => {
            shareBtn.textContent = originalText;
            shareBtn.disabled = false;
        });
    }
    
    // 顯示通知消息
    function showNotification(message, type = 'info') {
        // 移除現有的通知
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // 創建新通知
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // 3秒後自動移除
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // 添加動畫樣式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    function setupEventListeners() {
        document.querySelector('.calculate-btn').addEventListener('click', calculateDamage);
        document.getElementById('optimizeBtn').addEventListener('click', optimizeDamageAdvanced);
        document.querySelector('.extra-data-btn').addEventListener('click', showExtraData);
        document.querySelector('.close-modal').addEventListener('click', closeExtraData);
        document.getElementById('togglePoints').addEventListener('click', () => toggleInputSystem('points'));
        document.getElementById('toggleManual').addEventListener('click', () => toggleInputSystem('manual'));
        document.getElementById('toggleCurrent').addEventListener('click', () => toggleGameVersion('current'));
        document.getElementById('toggleOld').addEventListener('click', () => toggleGameVersion('old'));
        document.getElementById('equipmentSearch').addEventListener('input', filterEquipment);
        
        document.querySelectorAll('.tier-filter').forEach((btn, index) => {
            const tiers = ['all', 'I', 'II', 'III', 'IV', 'V'];
            btn.addEventListener('click', function() {
                filterByTier(tiers[index]);
            });
        });
        
        document.getElementById('weaponSelect').addEventListener('change', updateWeaponInfo);
        document.getElementById('playerLevel').addEventListener('change', updateEquipmentDisplay);
        document.getElementById('classLevel').addEventListener('change', calculateDamage);
        
        ['strength', 'vitality', 'intelligence', 'dexterity'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', updatePoints);
            }
        });
        
        ['magicPotion', 'attackPotion', 'goldenApple'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', calculateDamage);
            }
        });
        
        ['minDamage', 'maxDamage', 'magicDamage', 'critRate', 'critDamage'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', calculateDamage);
            }
        });
        
        const optimizationFilters = document.querySelector('.optimization-filters');
        if (optimizationFilters) {
            optimizationFilters.addEventListener('click', function(e) {
                if (e.target.classList.contains('filter-btn')) {
                    const type = e.target.textContent.includes('Final') ? 'final_damage' :
                                e.target.textContent.includes('10s') ? 'ten_second' : 'dot';
                    
                    currentOptimizationType = type;
                    
                    document.querySelectorAll('.filter-btn').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    e.target.classList.add('active');
                }
            });
        }
        
        const optimizeStatsBtn = document.getElementById('optimizeStatsBtn');
        if (optimizeStatsBtn) {
            optimizeStatsBtn.addEventListener('click', optimizeStats);
        }
        
        // 添加分享按鈕監聽器
        document.getElementById('shareResultBtn').addEventListener('click', shareResultAsImage);
        document.getElementById('shareOptimizeBtn').addEventListener('click', shareOptimizationAsImage);
        
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('extraDataModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    initialize();
});