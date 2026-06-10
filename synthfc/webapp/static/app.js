// FC Dataset Viewer - JavaScript (Updated for JSONL + validation + pagination)

let data = { examples: [], metadata: null, file: null, stats: null };
let filteredExamples = [];
let selectedIndex = -1;
let currentFileInfo = null; // Info sul file corrente dal server

// Pagination state
let pagination = {
    page: 1,
    perPage: 50,
    totalPages: 1,
    totalCount: 0
};

// Fail filter state
let failFilterActive = false;

// Init
document.addEventListener('DOMContentLoaded', () => {
    refreshFiles();
});

// Refresh file list from server
async function refreshFiles() {
    try {
        const resp = await fetch('/api/files');
        const result = await resp.json();
        
        const select = document.getElementById('fileSelect');
        select.innerHTML = '<option value="">-- Seleziona file --</option>';
        
        result.files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f.name;
            opt.dataset.hasPostprocessed = f.has_postprocessed ? 'true' : 'false';
            opt.dataset.batchName = f.batch_name || '';
            opt.textContent = `${f.name} (${f.count} ex${f.model ? ', ' + f.model : ''})${f.has_postprocessed ? ' 📦' : ''}`;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error('Error loading files:', err);
    }
}

// Load selected file from dropdown
async function loadSelectedFile() {
    const select = document.getElementById('fileSelect');
    const filename = select.value;
    if (!filename) return;
    
    const selectedOpt = select.options[select.selectedIndex];
    currentFileInfo = {
        name: filename,
        hasPostprocessed: selectedOpt.dataset.hasPostprocessed === 'true',
        batchName: selectedOpt.dataset.batchName
    };
    
    // Mostra/nascondi toggle postprocessed
    updatePostprocessControls();
    
    // Reset pagination
    pagination.page = 1;
    
    await loadPage(1);
}

// Carica una pagina specifica
async function loadPage(page) {
    const filename = currentFileInfo?.name;
    if (!filename) return;
    
    try {
        const resp = await fetch(`/api/load/${encodeURIComponent(filename)}?page=${page}&per_page=${pagination.perPage}`);
        const result = await resp.json();
        
        if (result.error) {
            alert('Errore: ' + result.error);
            return;
        }
        
        // Salva dati
        data.examples = result.examples || [];
        data.metadata = result.metadata || null;
        data.file = filename;
        data.stats = result.stats || null;  // Stats calcolate su TUTTO il dataset
        
        // Aggiorna pagination (backend usa snake_case, frontend camelCase)
        const p = result.pagination || {};
        pagination = {
            page: p.page || 1,
            perPage: p.per_page || 50,
            totalPages: p.total_pages || 1,
            totalCount: p.total_count || result.count || 0
        };
        
        filteredExamples = [...data.examples];
        
        renderMetadata();
        renderStats();  // Usa stats dal server (calcolate su TUTTO)
        renderList();
        renderPagination();
    } catch (err) {
        alert('Errore nel caricamento: ' + err.message);
    }
}

// Toggle tra originale e postprocessed
async function togglePostprocessed() {
    if (!currentFileInfo) return;
    
    const usePostprocessed = document.getElementById('postprocessCheckbox').checked;
    const basePath = currentFileInfo.name.replace(/examples(_postprocessed)?\.jsonl$/, '');
    const filename = usePostprocessed 
        ? basePath + 'examples_postprocessed.jsonl'
        : basePath + 'examples.jsonl';
    
    // Aggiorna currentFileInfo e ricarica
    currentFileInfo.name = filename;
    pagination.page = 1;
    await loadPage(1);
}

// Mostra/nascondi controlli postprocess
function updatePostprocessControls() {
    const toggle = document.getElementById('postprocessToggle');
    const runBtn = document.getElementById('runPostprocessBtn');
    const checkbox = document.getElementById('postprocessCheckbox');
    
    if (currentFileInfo?.hasPostprocessed) {
        toggle.classList.remove('hidden');
        runBtn.classList.add('hidden');
        checkbox.checked = false;
    } else if (currentFileInfo?.batchName) {
        toggle.classList.add('hidden');
        runBtn.classList.remove('hidden');
    } else {
        toggle.classList.add('hidden');
        runBtn.classList.add('hidden');
    }
}

// Esegui postprocess
async function runPostprocess() {
    if (!currentFileInfo?.batchName) return;
    
    const btn = document.getElementById('runPostprocessBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Processing...';
    
    try {
        const resp = await fetch(`/api/postprocess/${currentFileInfo.batchName}`, { method: 'POST' });
        const result = await resp.json();
        
        if (result.error) {
            alert('Errore: ' + result.error);
            return;
        }
        
        alert(`✅ Post-processing completato!\n\nEsempi modificati: ${result.stats.examples_modified}\nUser merged: ${result.stats.user_merged}\nReflections rimosse: ${result.stats.reflections_removed}`);
        
        // Aggiorna stato e ricarica
        currentFileInfo.hasPostprocessed = true;
        updatePostprocessControls();
        
        // Auto-switch a postprocessed
        document.getElementById('postprocessCheckbox').checked = true;
        togglePostprocessed();
        
        // Refresh dropdown per aggiornare badge
        refreshFiles();
        
    } catch (err) {
        alert('Errore: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '⚙️ Run Postprocess';
    }
}

// File Upload (local)
document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const content = e.target.result;
            
            // Parse JSONL or JSON
            if (file.name.endsWith('.jsonl')) {
                const lines = content.split('\n').filter(l => l.trim());
                data.metadata = null;
                data.examples = [];
                
                lines.forEach(line => {
                    const obj = JSON.parse(line);
                    if (obj._metadata) {
                        data.metadata = obj;
                    } else {
                        data.examples.push(obj);
                    }
                });
            } else {
                const parsed = JSON.parse(content);
                data.examples = Array.isArray(parsed) ? parsed : (parsed.examples || []);
                data.metadata = null;
            }
            
            data.file = file.name;
            filteredExamples = [...data.examples];
            
            renderMetadata();
            renderStats();
            renderList();
        } catch (err) {
            alert('Errore nel parsing: ' + err.message);
        }
    };
    reader.readAsText(file);
});

function loadFile() {
    document.getElementById('fileInput').click();
}

// Metadata display
function renderMetadata() {
    const container = document.getElementById('metadata');
    if (!data.metadata) {
        container.innerHTML = '';
        return;
    }
    
    const m = data.metadata;
    container.innerHTML = `
        <span class="meta-item">📁 ${data.file}</span>
        <span class="meta-item">🤖 ${m.model || 'unknown'}</span>
        <span class="meta-item">📅 ${m.generated_at ? new Date(m.generated_at).toLocaleString() : '?'}</span>
        <span class="meta-item">🌡️ temp: ${m.temperature || '?'}</span>
        ${m.errors > 0 ? `<span class="meta-item error">💥 ${m.errors} errors</span>` : ''}
    `;
}

// Stats - usa stats dal server (calcolate su TUTTO il dataset)
function renderStats() {
    // Se abbiamo stats dal server, usale (sono su TUTTO il dataset)
    const stats = data.stats || calculateStatsFromPage();
    const failCount = stats.fail_convo ?? stats.failConvo ?? 0;
    
    document.getElementById('stats').innerHTML = `
        <div class="stat-box total">
            <div class="stat-value">${stats.total}</div>
            <div class="stat-label">Totali</div>
        </div>
        <div class="stat-box pass">
            <div class="stat-value">${stats.pass_convo ?? stats.passConvo}</div>
            <div class="stat-label">✅ OK</div>
        </div>
        <div class="stat-box fail clickable ${failFilterActive ? 'active-filter' : ''}" onclick="toggleFailFilter()" title="Clicca per filtrare solo FAIL">
            <div class="stat-value">${failCount}</div>
            <div class="stat-label">❌ Fail</div>
        </div>
        <div class="stat-box warn">
            <div class="stat-value">${stats.warn_convo ?? stats.warnConvo}</div>
            <div class="stat-label">⚠️ Warn</div>
        </div>
        <div class="stat-box error">
            <div class="stat-value">${stats.errors}</div>
            <div class="stat-label">💥 Errors</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">${stats.avg_score ?? stats.avgScore}%</div>
            <div class="stat-label">Avg Score</div>
        </div>
    `;
}

// Fallback: calcola stats dalla pagina corrente (per upload locale)
function calculateStatsFromPage() {
    let passConvo = 0, failConvo = 0, warnConvo = 0, errors = 0;
    let totalScore = 0;
    let validatedCount = 0;
    const byCheck = {};
    
    data.examples.forEach(ex => {
        if (ex.error) {
            errors++;
            return;
        }
        
        if (ex.validation) {
            totalScore += ex.validation.score || 0;
            validatedCount++;
            
            if (ex.validation.failed > 0) {
                failConvo++;
            } else if (ex.validation.warnings > 0) {
                warnConvo++;
            } else {
                passConvo++;
            }
            
            (ex.validation.results || []).forEach(r => {
                const checkName = r.param;
                if (!byCheck[checkName]) {
                    byCheck[checkName] = { pass: 0, fail: 0, warn: 0 };
                }
                if (r.status === '✅') byCheck[checkName].pass++;
                else if (r.status === '❌') byCheck[checkName].fail++;
                else if (r.status === '⚠️') byCheck[checkName].warn++;
            });
        }
    });
    
    const avgScore = validatedCount > 0 ? Math.round((totalScore / validatedCount) * 100) : 0;
    
    return { 
        total: pagination.totalCount || data.examples.length, 
        passConvo, failConvo, warnConvo, errors,
        avgScore,
        byCheck
    };
}

function renderCheckStats(byCheck) {
    const container = document.getElementById('checkStats');
    if (!byCheck || Object.keys(byCheck).length === 0) {
        container.innerHTML = '';
        return;
    }
    
    // Ordina per numero di problemi (fail + warn)
    const sorted = Object.entries(byCheck).sort((a, b) => {
        const aProblems = a[1].fail + a[1].warn;
        const bProblems = b[1].fail + b[1].warn;
        return bProblems - aProblems;
    });
    
    let html = '<div class="check-stats-grid">';
    sorted.forEach(([checkName, counts]) => {
        const total = counts.pass + counts.fail + counts.warn;
        const passRate = total > 0 ? Math.round((counts.pass / total) * 100) : 100;
        const hasProblems = counts.fail > 0 || counts.warn > 0;
        
        html += `
            <div class="check-stat-item ${hasProblems ? 'has-problems' : ''}" 
                 onclick="filterByCheck('${checkName}')" 
                 title="Click per filtrare">
                <span class="check-name">${checkName}</span>
                <span class="check-counts">
                    <span class="c-pass">✅${counts.pass}</span>
                    <span class="c-fail">❌${counts.fail}</span>
                    <span class="c-warn">⚠️${counts.warn}</span>
                </span>
                <span class="check-rate ${passRate < 80 ? 'low' : ''}">${passRate}%</span>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
    
    // Popola anche il dropdown filtro
    // Escludi check poco utili per il filtering
    const excludeFromFilter = [
        'conversation_length', 
        'user_style', 
        'conversation_language',
        'system_prompt_type',
        'out_of_scope_requests'
    ];
    
    const filterSelect = document.getElementById('filterCheck');
    filterSelect.innerHTML = '<option value="all">Tutti i check</option>';
    sorted.forEach(([checkName, counts]) => {
        // Salta check esclusi
        if (excludeFromFilter.includes(checkName)) return;
        
        const problems = counts.fail + counts.warn;
        if (problems > 0) {
            filterSelect.innerHTML += `<option value="${checkName}">${checkName} (${problems} problemi)</option>`;
        }
    });
}

function filterByCheck(checkName) {
    // Non più usato
}

// Toggle fail filter - chiamato cliccando il box FAIL rosso
async function toggleFailFilter() {
    failFilterActive = !failFilterActive;
    
    // Aggiorna UI stats per mostrare stato attivo
    renderStats();
    
    // Mostra/nascondi filtro categorie
    const filterDiv = document.getElementById('failCategoryFilter');
    if (failFilterActive) {
        // Mostra filtro categorie FAIL
        const stats = data.stats || {};
        const byCheck = stats.by_check || {};
        
        // Categorie che possono avere FAIL (solo consecutive_roles e parallel_tool_calls)
        const failCategories = [];
        ['consecutive_roles', 'parallel_tool_calls'].forEach(cat => {
            const catData = byCheck[cat] || {};
            if (catData.fail > 0) {
                failCategories.push({ name: cat, count: catData.fail });
            }
        });
        
        if (failCategories.length > 0) {
            filterDiv.innerHTML = `
                <div class="fail-filter-header">
                    <span>🔍 Filtra per categoria:</span>
                    <select id="failCategorySelect" onchange="applyFailCategoryFilter()">
                        <option value="all">Tutti i FAIL (${failCategories.reduce((s, c) => s + c.count, 0)})</option>
                        ${failCategories.map(c => `<option value="${c.name}">${c.name} (${c.count})</option>`).join('')}
                    </select>
                </div>
            `;
            filterDiv.classList.remove('hidden');
        } else {
            filterDiv.innerHTML = '<div class="fail-filter-header">Nessun FAIL trovato</div>';
            filterDiv.classList.remove('hidden');
        }
        
        // Carica solo FAIL
        await loadPageWithFilter('fail');
    } else {
        filterDiv.classList.add('hidden');
        filterDiv.innerHTML = '';
        // Torna alla vista normale
        await loadPage(1);
    }
}

// Applica filtro categoria FAIL
async function applyFailCategoryFilter() {
    const select = document.getElementById('failCategorySelect');
    const category = select.value;
    await loadPageWithFilter('fail', category === 'all' ? null : category);
}

// Carica pagina con filtro status
async function loadPageWithFilter(status, failCategory = null) {
    const filename = currentFileInfo?.name;
    if (!filename) return;
    
    try {
        let url = `/api/load/${encodeURIComponent(filename)}?page=1&per_page=${pagination.perPage}&status=${status}`;
        if (failCategory) {
            url += `&fail_category=${failCategory}`;
        }
        
        const resp = await fetch(url);
        const result = await resp.json();
        
        if (result.error) {
            alert('Errore: ' + result.error);
            return;
        }
        
        data.examples = result.examples || [];
        // Mantieni le stats originali (su tutto)
        if (result.stats) {
            data.stats = result.stats;
        }
        
        const p = result.pagination || {};
        pagination = {
            page: p.page || 1,
            perPage: p.per_page || 50,
            totalPages: p.total_pages || 1,
            totalCount: p.total_count || result.count || 0
        };
        
        filteredExamples = [...data.examples];
        
        renderList();
        renderPagination();
    } catch (err) {
        alert('Errore nel caricamento: ' + err.message);
    }
}

// Get status for an example (for filtering/display)
function getExampleStatus(ex) {
    if (ex.error) return 'error';
    if (ex.validation) {
        if (ex.validation.failed > 0) return 'fail';
        if (ex.validation.warnings > 0) return 'warn';
        return 'pass';
    }
    // Fallback
    return validateExampleClient(ex).status;
}

// Client-side validation (fallback)
function validateExampleClient(ex) {
    const checks = [];
    const params = ex.params || {};
    const observed = ex.observed || {};
    const messages = ex.messages || [];
    
    // 1. Tool calls count
    const actualTC = observed.num_tool_calls ?? countToolCalls(messages);
    
    if (params.call_type === 'negative' || 
        (params.call_type === 'clarification' && params.clarification_outcome === 'unresolved')) {
        checks.push({
            param: 'call_type',
            expected: '0 tool calls',
            actual: actualTC,
            status: actualTC === 0 ? 'pass' : 'fail'
        });
    } else if (params.call_type === 'positive' || 
               (params.call_type === 'clarification' && params.clarification_outcome === 'resolved')) {
        checks.push({
            param: 'call_type',
            expected: '>0 tool calls',
            actual: actualTC,
            status: actualTC > 0 ? 'pass' : 'fail'
        });
    }
    
    // Calculate overall status
    const hasFailure = checks.some(c => c.status === 'fail');
    const hasWarning = checks.some(c => c.status === 'warn');
    const status = hasFailure ? 'fail' : (hasWarning ? 'warn' : 'pass');
    
    return { checks, status };
}

function countToolCalls(messages) {
    let count = 0;
    messages.forEach(m => {
        if (m.tool_calls && m.tool_calls.length > 0) {
            count += m.tool_calls.length;
        }
    });
    return count;
}

// List rendering
function renderList() {
    const container = document.getElementById('listItems');
    container.innerHTML = '';
    
    if (filteredExamples.length === 0) {
        container.innerHTML = '<div class="empty-list">Nessun esempio trovato</div>';
        return;
    }
    
    // Calcola l'indice globale per la numerazione
    const globalOffset = (pagination.page - 1) * pagination.perPage;
    
    filteredExamples.forEach((ex, idx) => {
        const status = getExampleStatus(ex);
        const params = ex.params || {};
        const callType = params.call_type || 'unknown';
        const subType = params.positive_type || params.negative_reason || params.clarification_outcome || '';
        const score = ex.validation?.score != null ? Math.round(ex.validation.score * 100) : '?';
        
        const item = document.createElement('div');
        item.className = `example-item ${selectedIndex === idx ? 'active' : ''} status-${status}`;
        item.onclick = () => selectExample(idx);
        
        item.innerHTML = `
            <div class="example-item-header">
                <span class="example-id">#${ex.id || (globalOffset + idx + 1)}</span>
                <span class="example-badge badge-${status}">${status.toUpperCase()}</span>
                <span class="example-score">${score}%</span>
            </div>
            <div class="example-meta">
                ${params.domain || 'N/A'} • ${params.conversation_language || '?'} • ${(ex.messages || []).length} msgs
            </div>
            <div class="example-type">${callType}/${subType}</div>
            ${ex.error ? `<div class="example-error">💥 ${ex.error.substring(0, 50)}...</div>` : ''}
        `;
        
        container.appendChild(item);
    });
}

// Pagination controls
function renderPagination() {
    const container = document.getElementById('paginationControls');
    if (!container) return;
    
    if (pagination.totalPages <= 1) {
        container.innerHTML = `<div class="pagination-info">Pagina 1 di 1 (${pagination.totalCount} esempi)</div>`;
        return;
    }
    
    const { page, totalPages, totalCount, perPage } = pagination;
    const start = (page - 1) * perPage + 1;
    const end = Math.min(page * perPage, totalCount);
    
    // Genera i numeri di pagina da mostrare
    let pageNumbers = [];
    const maxVisible = 5;
    let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
    }
    
    container.innerHTML = `
        <div class="pagination-info">
            ${start}-${end} di ${totalCount}
        </div>
        <div class="pagination-buttons">
            <button onclick="goToPage(1)" ${page === 1 ? 'disabled' : ''} title="Prima pagina">⏮</button>
            <button onclick="goToPage(${page - 1})" ${page === 1 ? 'disabled' : ''} title="Precedente">◀</button>
            ${pageNumbers.map(p => 
                `<button onclick="goToPage(${p})" class="${p === page ? 'active' : ''}">${p}</button>`
            ).join('')}
            <button onclick="goToPage(${page + 1})" ${page === totalPages ? 'disabled' : ''} title="Successiva">▶</button>
            <button onclick="goToPage(${totalPages})" ${page === totalPages ? 'disabled' : ''} title="Ultima pagina">⏭</button>
        </div>
        <div class="pagination-goto">
            <input type="number" id="gotoPageInput" min="1" max="${totalPages}" value="${page}" 
                   onkeydown="if(event.key==='Enter')goToPageInput()">
            <button onclick="goToPageInput()">Vai</button>
        </div>
    `;
}

async function goToPage(page) {
    if (page < 1 || page > pagination.totalPages) return;
    pagination.page = page;
    await loadPage(page);
    
    // Scroll to top of list
    document.getElementById('listItems').scrollTop = 0;
}

function goToPageInput() {
    const input = document.getElementById('gotoPageInput');
    const page = parseInt(input.value);
    if (page >= 1 && page <= pagination.totalPages) {
        goToPage(page);
    }
}

function filterExamples() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    
    filteredExamples = data.examples.filter((ex, idx) => {
        // Search filter
        if (search) {
            const searchable = JSON.stringify(ex).toLowerCase();
            if (!searchable.includes(search)) return false;
        }
        
        return true;
    });
    
    selectedIndex = -1;
    renderList();
}

// Detail view
function selectExample(idx) {
    selectedIndex = idx;
    renderList();
    renderDetail(filteredExamples[idx]);
}

function renderDetail(ex) {
    const panel = document.getElementById('detailPanel');
    const params = ex.params || {};
    const observed = ex.observed || {};
    const validation = ex.validation || {};
    const messages = ex.messages || [];
    const tools = ex.tools || [];
    
    // Check for error
    if (ex.error) {
        panel.innerHTML = `
            <div class="detail-section error-section">
                <div class="section-header">💥 Errore di Generazione</div>
                <div class="section-content">
                    <pre class="error-content">${escapeHtml(ex.error)}</pre>
                </div>
            </div>
            <div class="detail-section">
                <div class="section-header">⚙️ Parametri Richiesti</div>
                <div class="section-content">
                    <pre>${JSON.stringify(params, null, 2)}</pre>
                </div>
            </div>
        `;
        return;
    }
    
    panel.innerHTML = `
        <!-- Validation Section -->
        <div class="detail-section">
            <div class="section-header" onclick="toggleSection(this)">
                <span>✅ Validazione</span>
                <span class="section-badge">${validation.score != null ? Math.round(validation.score * 100) : '?'}% (${validation.passed || 0}/${(validation.passed || 0) + (validation.failed || 0) + (validation.warnings || 0)})</span>
            </div>
            <div class="section-content">
                ${validation.results ? `
                    <table class="validation-table">
                        <thead>
                            <tr>
                                <th>Parametro</th>
                                <th>Expected</th>
                                <th>Actual</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${validation.results.map(r => `
                                <tr>
                                    <td>${r.param}</td>
                                    <td>${r.expected}</td>
                                    <td>${r.observed}</td>
                                    <td>${r.status}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                ` : '<p>Validazione non disponibile</p>'}
            </div>
        </div>
        
        <!-- Parameters vs Observed -->
        <div class="detail-section">
            <div class="section-header" onclick="toggleSection(this)">
                <span>⚙️ Params vs Observed</span>
            </div>
            <div class="section-content">
                <div class="comparison-grid">
                    <div class="comparison-col">
                        <h4>Requested</h4>
                        ${Object.entries(params).map(([k, v]) => `
                            <div class="param-row">
                                <span class="param-key">${k}</span>
                                <span class="param-value">${formatValue(v)}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="comparison-col">
                        <h4>Observed</h4>
                        ${Object.entries(observed).map(([k, v]) => `
                            <div class="param-row">
                                <span class="param-key">${k}</span>
                                <span class="param-value">${formatValue(v)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- System Prompt Section -->
        <div class="detail-section">
            <div class="section-header" onclick="toggleSection(this)">
                <span>📋 System Prompt</span>
            </div>
            <div class="section-content">
                <div class="system-prompt">${ex.system_prompt || '<em>(none)</em>'}</div>
            </div>
        </div>
        
        <!-- Conversation Section -->
        <div class="detail-section">
            <div class="section-header" onclick="toggleSection(this)">
                <span>💬 Conversazione (${messages.length} messaggi)</span>
            </div>
            <div class="section-content conversation-content">
                ${messages.map(m => renderMessage(m)).join('')}
            </div>
        </div>
        
        <!-- Tools Section -->
        <div class="detail-section collapsed">
            <div class="section-header" onclick="toggleSection(this)">
                <span>🔧 Tools (${tools.length})</span>
            </div>
            <div class="section-content" style="display: none;">
                <div class="tools-list">
                    ${tools.map(t => `
                        <span class="tool-tag" title="${escapeHtml(t.function?.description || '')}">${t.function?.name || t.name || 'unknown'}</span>
                    `).join('')}
                </div>
            </div>
        </div>
        
        <!-- Raw JSON -->
        <div class="detail-section collapsed">
            <div class="section-header" onclick="toggleSection(this)">
                <span>📄 Raw JSON</span>
            </div>
            <div class="section-content" style="display: none;">
                <pre class="raw-json">${escapeHtml(JSON.stringify(ex, null, 2))}</pre>
            </div>
        </div>
    `;
}

function renderMessage(msg) {
    const role = msg.role || 'unknown';
    let content = '';
    
    if (msg.content) {
        content = `<div class="message-content">${escapeHtml(msg.content)}</div>`;
    }
    
    if (msg.tool_calls && msg.tool_calls.length > 0) {
        content += msg.tool_calls.map(tc => `
            <div class="tool-call">
                <span class="tool-name">🔧 ${tc.function?.name || 'unknown'}()</span>
                <pre>${formatJson(tc.function?.arguments)}</pre>
            </div>
        `).join('');
    }
    
    return `
        <div class="message message-${role}">
            <div class="message-role">${role}${msg.tool_call_id ? ` <span class="tool-id">[${msg.tool_call_id}]</span>` : ''}</div>
            ${content}
        </div>
    `;
}

function toggleSection(header) {
    const content = header.nextElementSibling;
    const isHidden = content.style.display === 'none';
    content.style.display = isHidden ? 'block' : 'none';
    header.parentElement.classList.toggle('collapsed', !isHidden);
}

// Utilities
function formatValue(v) {
    if (v === null || v === undefined) return '-';
    if (Array.isArray(v)) return v.join(', ');
    if (typeof v === 'object') return JSON.stringify(v);
    return String(v);
}

function formatJson(str) {
    if (!str) return '';
    try {
        return JSON.stringify(JSON.parse(str), null, 2);
    } catch {
        return str;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
