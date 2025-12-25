// Critical Fantasy Damage Calculator JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let selectedEquipment = [];
    const maxEquipment = 3;
    let equipmentDatabase = {};
    let weaponDatabase = {};
    let currentTierFilter = 'all';
    let currentSearchFilter = '';
    let currentResult = null;
    let currentOptimizationType = 'final_damage';
    let currentVersion = 'current'; // 'current' or 'old'
    
    // Set indicator mapping
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
    
    // Initialize the application
    function initialize() {
        // Load data from server or use provided data
        equipmentDatabase = window.equipmentDb || {};
        weaponDatabase = window.weaponDb || {};
        
        // Initialize equipment list
        initializeEquipment();
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize points
        updatePoints();
        
        // Update weapon info
        updateWeaponInfo();
        
        // Initial calculation
        calculateDamage();
    }
    
    // Initialize equipment list
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
    
    // Create equipment item element with image support
    function createEquipmentItem(id, data) {
        const div = document.createElement('div');
        div.className = 'equipment-item';
        div.setAttribute('data-id', id);
        div.setAttribute('data-tier', data.tier);
        
        // Check level requirement
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const levelReq = data.level_req || 0;
        const meetsLevelReq = levelReq <= playerLevel;
        
        if (!meetsLevelReq) {
            div.style.opacity = '0.6';
        }
        
        // Check if it's an old version item
        const isOldItem = id.includes('_old');
        if (isOldItem) {
            div.classList.add('equipment-old');
        }
        
        // Build stats string
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
        
        // Build effects string
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
        
        // Add version and level requirement info
        let versionInfo = '';
        if (isOldItem) {
            versionInfo = `<span class="old-version-tag">OLD</span>`;
        }
        
        let levelInfo = '';
        if (levelReq > 0) {
            levelInfo = `<span style="color: ${meetsLevelReq ? '#28a745' : '#dc3545'}; font-size: 0.8em;">Lv. ${levelReq}</span>`;
        }
        
        // Add image if available
        let imageHtml = '';
        if (data.image_url && data.image_url.trim()) {
            // Clean up the URL
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
        
        // Only allow selection if level requirement is met
        if (meetsLevelReq) {
            div.addEventListener('click', () => toggleEquipmentSelection(id));
        } else {
            div.style.cursor = 'not-allowed';
            div.title = `Requires Level ${levelReq}`;
        }
        
        return div;
    }
    
    // Filter equipment based on search, tier, and version
    function filterEquipmentItem(id, data) {
        const matchesSearch = data.name.toLowerCase().includes(currentSearchFilter.toLowerCase()) ||
                            id.toLowerCase().includes(currentSearchFilter.toLowerCase());
        const matchesTier = currentTierFilter === 'all' || data.tier === currentTierFilter;
        
        // Version filtering
        const isOldItem = id.includes('_old');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const matchesVersion = useOldVersion ? 
            (isOldItem || !equipmentDatabase[id + '_old']) :  // Old version: show old items or items without old version
            !isOldItem;  // Current version: don't show old items
        
        return matchesSearch && matchesTier && matchesVersion;
    }
    
    // Filter equipment list
    function filterEquipment() {
        currentSearchFilter = document.getElementById('equipmentSearch').value;
        initializeEquipment();
    }
    
    // Filter by tier
    function filterByTier(tier) {
        currentTierFilter = tier;
        document.querySelectorAll('.tier-filter').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        initializeEquipment();
    }
    
    // Toggle equipment selection with version compatibility check
    function toggleEquipmentSelection(id) {
        const eqData = equipmentDatabase[id];
        if (!eqData) return;
        
        // Check for version conflicts
        const isOldItem = id.includes('_old');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        
        // Check if trying to select both old and new versions of the same item
        const baseId = isOldItem ? id.replace('_old', '') : id;
        const oppositeId = isOldItem ? baseId : baseId + '_old';
        
        if (selectedEquipment.includes(oppositeId)) {
            alert(`Cannot select both old and new versions of ${eqData.name.replace(' (Old)', '').replace(' (New)', '')}!`);
            return;
        }
        
        if (selectedEquipment.includes(id)) {
            // Deselect
            selectedEquipment = selectedEquipment.filter(eq => eq !== id);
            document.querySelector(`.equipment-item[data-id="${id}"]`).classList.remove('selected');
        } else {
            // Select
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
    
    // Update equipment display when level changes
    function updateEquipmentDisplay() {
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        // Update equipment list with current version filter
        initializeEquipment();
        
        // Remove equipment that no longer meets level requirements or version conflicts
        selectedEquipment = selectedEquipment.filter(id => {
            const eqData = equipmentDatabase[id];
            if (!eqData) return false;
            
            // Check level requirement
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
    
    // Update selected equipment display
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
        
        // Add event listeners to remove buttons
        container.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                removeEquipment(id);
            });
        });
    }
    
    // Remove equipment
    function removeEquipment(id) {
        selectedEquipment = selectedEquipment.filter(eq => eq !== id);
        document.querySelector(`.equipment-item[data-id="${id}"]`).classList.remove('selected');
        updateSelectedEquipmentDisplay();
        calculateDamage();
    }
    
    // Toggle game version
    function toggleGameVersion(version) {
        const toggleCurrent = document.getElementById('toggleCurrent');
        const toggleOld = document.getElementById('toggleOld');
        const useOldVersion = version === 'old';
        
        toggleCurrent.classList.toggle('active', !useOldVersion);
        toggleOld.classList.toggle('active', useOldVersion);
        
        currentVersion = version;
        
        // Update equipment display and adjust selected equipment
        updateEquipmentDisplay();
    }
    
    // Weapon selection with image support
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
        
        // Add level requirement
        const levelReq = weapon.level_req || 0;
        let levelInfo = '';
        if (levelReq > 0) {
            levelInfo = `<br><small>Level Requirement: ${levelReq}</small>`;
        }
        
        // Furioso special info
        let furiosoInfo = '';
        if (selectedWeapon === 'furioso') {
            furiosoInfo = `<br><small style="color: #4a90e2;">Updated: 3.7x total damage + bleed on 4th hit</small>`;
        }
        
        // Add weapon image
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
    
    // Toggle input system
    function toggleInputSystem(system) {
        document.getElementById('togglePoints').classList.toggle('active', system === 'points');
        document.getElementById('toggleManual').classList.toggle('active', system === 'manual');
        document.getElementById('pointsSection').style.display = system === 'points' ? 'block' : 'none';
        document.getElementById('manualSection').style.display = system === 'manual' ? 'block' : 'none';
        
        calculateDamage();
    }
    
    // Update points calculation
    function updatePoints() {
        const strength = parseInt(document.getElementById('strength').value) || 0;
        const vitality = parseInt(document.getElementById('vitality').value) || 0;
        const intelligence = parseInt(document.getElementById('intelligence').value) || 0;
        const dexterity = parseInt(document.getElementById('dexterity').value) || 0;
        const defense = parseInt(document.getElementById('defense').value) || 0;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        const total = strength + vitality + intelligence + dexterity + defense;
        const maxPoints = playerLevel * 2;
        
        document.getElementById('totalPoints').textContent = total;
        document.getElementById('remainingPoints').textContent = maxPoints - total;
        document.getElementById('maxPoints').textContent = maxPoints;
        
        calculateDamage();
    }
    
    // Set optimization type
    function setOptimizationType(type) {
        currentOptimizationType = type;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }
    
    // Main damage calculation function
    function calculateDamage() {
        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
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
            data.defense = parseInt(document.getElementById('defense').value) || 0;
        } else {
            data.minDamage = document.getElementById('minDamage').value;
            data.maxDamage = document.getElementById('maxDamage').value;
            data.magicDamage = document.getElementById('magicDamage').value;
            data.critRate = document.getElementById('critRate').value;
            data.critDamage = document.getElementById('critDamage').value;
        }
        
        // Don't calculate if required fields are empty
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
                
                // Update results display
                document.getElementById('resultBaseDamage').textContent = result.base_damage.toLocaleString();
                document.getElementById('resultCrit').textContent = result.crit_multiplied_damage.toLocaleString();
                document.getElementById('resultDot').textContent = result.dot_damage.toLocaleString();
                document.getElementById('resultFinal').textContent = result.final_damage.toLocaleString();
                document.getElementById('resultMultiplier').textContent = result.effective_multiplier + 'x';
                document.getElementById('resultCritRate').textContent = result.crit_rate.toLocaleString() + '%';
                document.getElementById('resultCritDamage').textContent = result.crit_damage.toLocaleString() + '%';
                document.getElementById('resultDamageType').textContent = result.damage_type === 'magic' ? 'Magic' : 'Physical';
                
                // Update ten second damage display
                if (result.ten_second_damage) {
                    document.getElementById('resultTenSecond').textContent = result.ten_second_damage.total_damage.toLocaleString();
                    document.getElementById('resultMechanic').textContent = result.ten_second_damage.mechanic;
                }
                
                // Show player stats if using point system
                if (result.calculated_stats && result.player_stats) {
                    document.getElementById('playerStatsSection').style.display = 'block';
                    
                    document.getElementById('playerStatsContent').innerHTML = `
                        <div class="result-item">
                            <span class="result-label">Health:</span>
                            <span class="result-value">${result.player_stats.health.toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Shield:</span>
                            <span class="result-value">${result.player_stats.shield.toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Total HP:</span>
                            <span class="result-value">${result.player_stats.total_hp.toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Attack Range:</span>
                            <span class="result-value">${result.player_stats.min_damage.toLocaleString()} - ${result.player_stats.max_damage.toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Magic Damage:</span>
                            <span class="result-value">${result.player_stats.magic_damage.toLocaleString()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Crit Rate:</span>
                            <span class="result-value">${result.crit_rate.toLocaleString()}%</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Crit Damage:</span>
                            <span class="result-value">${result.crit_damage.toLocaleString()}%</span>
                        </div>
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
    
    // Optimize damage function
    function optimizeDamageAdvanced() {
        const optimizeBtn = document.getElementById('optimizeBtn');
        optimizeBtn.textContent = 'Calculating...';
        optimizeBtn.disabled = true;

        const usePointSystem = document.getElementById('togglePoints').classList.contains('active');
        const useOldVersion = document.getElementById('toggleOld').classList.contains('active');
        const selectedWeapon = document.getElementById('weaponSelect').value;
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        const data = {
            usePointSystem: usePointSystem,
            useOldVersion: useOldVersion,
            selectedWeapon: selectedWeapon,
            playerLevel: playerLevel,
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
            data.defense = parseInt(document.getElementById('defense').value) || 0;
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

    // Display optimization results
    function displayOptimizationResults(result) {
        const section = document.getElementById('optimizeResultSection');
        const content = document.getElementById('optimizeResultsContent');
        
        let html = `<p>Tested ${result.total_combinations_tested.toLocaleString()} combinations (${result.available_equipment_count} available equipment)</p>`;
        html += `<p>Version: ${result.version} ${result.allows_mixed_versions ? '(Mixed versions allowed)' : ''}</p>`;
        
        const scoreLabel = {
            'final_damage': 'Final Damage',
            'ten_second': '10s Total Damage', 
            'first_hit': 'First Hit',
            'dot': 'DoT Damage'
        }[result.optimization_type] || 'Score';
        
        result.top_combinations.forEach((combo, index) => {
            // Check if this combo has old items
            const hasOldItems = combo.equipment_ids.some(id => id.includes('_old'));
            const versionTag = hasOldItems ? '<span style="color: #dc3545; font-size: 0.9em;">(Mixed)</span>' : '';
            
            html += `
                <div class="optimize-combo">
                    <h4>#${index + 1} - ${scoreLabel}: ${combo.score.toLocaleString()} ${versionTag}</h4>
                    <p><strong>Final Damage:</strong> ${combo.final_damage.toLocaleString()}</p>
                    <p><strong>10s Total Damage:</strong> ${combo.ten_second_total.toLocaleString()}</p>
                    <p><strong>First Hit:</strong> ${combo.first_hit.toLocaleString()}</p>
                    <p><strong>DoT Damage:</strong> ${combo.dot_damage.toLocaleString()}</p>
                    <p><strong>Equipment:</strong> ${combo.equipment_names.join(', ')}</p>
                    <p><strong>Crit:</strong> ${combo.crit_rate}% rate, ${combo.crit_damage}% damage</p>
                    <button class="apply-combo-btn" data-ids='${JSON.stringify(combo.equipment_ids)}'>Apply This Combo</button>
                </div>
            `;
        });
        
        content.innerHTML = html;
        section.style.display = 'block';
        
        // Add event listeners to apply buttons
        content.querySelectorAll('.apply-combo-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const equipmentIds = JSON.parse(this.getAttribute('data-ids'));
                applyOptimizedCombo(equipmentIds);
            });
        });
    }

    // Apply optimized combination
    function applyOptimizedCombo(equipmentIds) {
        // Clear current selection
        selectedEquipment.forEach(id => {
            const element = document.querySelector(`.equipment-item[data-id="${id}"]`);
            if (element) element.classList.remove('selected');
        });
        
        // Select new equipment
        selectedEquipment = [...equipmentIds];
        selectedEquipment.forEach(id => {
            const element = document.querySelector(`.equipment-item[data-id="${id}"]`);
            if (element) element.classList.add('selected');
        });
        
        updateSelectedEquipmentDisplay();
        calculateDamage();
        
        // Scroll to results
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Stats optimization function
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

    // Apply optimized stats
    function applyOptimizedStats(recommendation) {
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        
        document.getElementById('strength').value = recommendation.strength;
        document.getElementById('intelligence').value = recommendation.intelligence;
        document.getElementById('dexterity').value = recommendation.dexterity;
        document.getElementById('defense').value = recommendation.defense;
        
        updatePoints();
        calculateDamage();
        
        alert(`Optimized stats applied!\n${recommendation.reason}\n\nStrength: ${recommendation.strength}\nIntelligence: ${recommendation.intelligence}\nDexterity: ${recommendation.dexterity}\nDefense: ${recommendation.defense}\n\nTotal Used: ${recommendation.total_used}/${playerLevel * 2}`);
    }
    
    // Show extra data modal
    function showExtraData() {
        if (!currentResult) return;
        
        const modal = document.getElementById('extraDataModal');
        const content = document.getElementById('extraDataContent');
        
        const details = currentResult.calculation_details;
        
        let html = `
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
                        <span>${(details.dot_calculation.burn_chance * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span>Bleed Chance:</span>
                        <span>${(details.dot_calculation.bleed_chance * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span>Poison Chance:</span>
                        <span>${(details.dot_calculation.poison_chance * 100).toFixed(1)}%</span>
                    </div>
                </div>
            `;
        }
        
        content.innerHTML = html;
        modal.style.display = 'block';
    }
    
    // Close extra data modal
    function closeExtraData() {
        document.getElementById('extraDataModal').style.display = 'none';
    }
    
    // Add point limits to input fields
    function addPointLimits() {
        const playerLevel = parseInt(document.getElementById('playerLevel').value) || 190;
        const maxPoints = playerLevel * 2;
        
        // Set input field maximum values
        document.getElementById('strength').max = maxPoints;
        document.getElementById('vitality').max = maxPoints;
        document.getElementById('intelligence').max = maxPoints;
        document.getElementById('dexterity').max = 50; // DEX still capped at 50
        document.getElementById('defense').max = maxPoints;
    }

    // Setup event listeners
    function setupEventListeners() {
        // Calculate button
        document.querySelector('.calculate-btn').addEventListener('click', calculateDamage);
        
        // Optimize button
        document.getElementById('optimizeBtn').addEventListener('click', optimizeDamageAdvanced);
        
        // Extra data button
        document.querySelector('.extra-data-btn').addEventListener('click', showExtraData);
        
        // Close modal button
        document.querySelector('.close-modal').addEventListener('click', closeExtraData);
        
        // System toggle buttons
        document.getElementById('togglePoints').addEventListener('click', () => toggleInputSystem('points'));
        document.getElementById('toggleManual').addEventListener('click', () => toggleInputSystem('manual'));
        
        // Version toggle buttons
        document.getElementById('toggleCurrent').addEventListener('click', () => toggleGameVersion('current'));
        document.getElementById('toggleOld').addEventListener('click', () => toggleGameVersion('old'));
        
        // Equipment search
        document.getElementById('equipmentSearch').addEventListener('input', filterEquipment);
        
        // Tier filters
        document.querySelectorAll('.tier-filter').forEach((btn, index) => {
            btn.addEventListener('click', function() {
                const tiers = ['all', 'I', 'II', 'III', 'IV', 'V'];
                filterByTier(tiers[index]);
            });
        });
        
        // Weapon select
        document.getElementById('weaponSelect').addEventListener('change', updateWeaponInfo);
        
        // Player level change
        document.getElementById('playerLevel').addEventListener('change', updateEquipmentDisplay);
        
        // Attribute points changes
        ['strength', 'vitality', 'intelligence', 'dexterity', 'defense'].forEach(id => {
            document.getElementById(id)?.addEventListener('input', updatePoints);
        });
        
        // Potion toggles
        ['magicPotion', 'attackPotion', 'goldenApple'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', calculateDamage);
        });
        
        // Manual stat inputs
        ['minDamage', 'maxDamage', 'magicDamage', 'critRate', 'critDamage'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', calculateDamage);
            }
        });
        
        // Optimization filters (delegated event listener)
        document.querySelector('.optimization-filters').addEventListener('click', function(e) {
            if (e.target.classList.contains('filter-btn')) {
                const type = e.target.textContent.includes('Final') ? 'final_damage' :
                            e.target.textContent.includes('10s') ? 'ten_second' :
                            e.target.textContent.includes('First') ? 'first_hit' : 'dot';
                
                setOptimizationType(type);
                
                // Update active class
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
            }
        });
        
        // Optimize stats button
        document.addEventListener('click', function(e) {
            if (e.target && e.target.id === 'optimizeStatsBtn') {
                optimizeStats();
            }
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('extraDataModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Initialize the application
    initialize();
});