/**
 * AutoPublisherAI Dashboard - Main JavaScript
 * 
 * This file contains all the client-side logic for the dashboard.
 * It's written in vanilla JavaScript for maximum performance and minimal dependencies.
 */

// ==============================================
// Configuration
// ==============================================
const CONFIG = {
    apiUrl: localStorage.getItem('apiUrl') || 'http://localhost:8000',
    refreshInterval: 5000, // 5 seconds
    maxWorkflows: 50
};

// ==============================================
// State Management
// ==============================================
const state = {
    workflows: new Map(),
    stats: {
        total: 0,
        published: 0,
        processing: 0,
        failed: 0
    },
    refreshTimer: null
};

// ==============================================
// Utility Functions
// ==============================================

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    
    // Set icon based on type
    const icons = {
        success: 'fa-check-circle text-green-500',
        error: 'fa-exclamation-circle text-red-500',
        warning: 'fa-exclamation-triangle text-yellow-500',
        info: 'fa-info-circle text-blue-500'
    };
    
    toastIcon.className = `fas ${icons[type] || icons.info} ml-3 text-xl`;
    toastMessage.textContent = message;
    
    // Show toast
    toast.classList.remove('hidden');
    toast.classList.add('toast-show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.classList.remove('toast-show', 'toast-hide');
        }, 300);
    }, 3000);
}

/**
 * Format date to Arabic
 */
function formatDate(dateString) {
    if (!dateString) return 'غير محدد';
    const date = new Date(dateString);
    return date.toLocaleString('ar-EG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const statusMap = {
        'pending': { text: 'قيد الانتظار', class: 'status-pending' },
        'generating_content': { text: 'توليد المحتوى', class: 'status-generating' },
        'content_generated': { text: 'تم التوليد', class: 'status-generating' },
        'publishing': { text: 'جاري النشر', class: 'status-publishing' },
        'published': { text: 'تم النشر', class: 'status-published' },
        'failed': { text: 'فشل', class: 'status-failed' }
    };
    
    const statusInfo = statusMap[status] || { text: status, class: 'status-pending' };
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

/**
 * Get platform icon HTML
 */
function getPlatformIcon(platform) {
    const icons = {
        'wordpress': '<i class="fab fa-wordpress"></i>',
        'instagram': '<i class="fab fa-instagram"></i>',
        'facebook': '<i class="fab fa-facebook"></i>',
        'x': '<i class="fab fa-x-twitter"></i>'
    };
    
    return icons[platform] || '<i class="fas fa-globe"></i>';
}

// ==============================================
// API Functions
// ==============================================

/**
 * Execute workflow (create and publish article)
 */
async function executeWorkflow(workflowData) {
    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/v1/workflow/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(workflowData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Error executing workflow:', error);
        throw error;
    }
}

/**
 * Get workflow status
 */
async function getWorkflowStatus(workflowId) {
    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/v1/workflow/status/${workflowId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Error getting workflow status:', error);
        throw error;
    }
}

// ==============================================
// UI Functions
// ==============================================

/**
 * Create workflow card HTML
 */
function createWorkflowCard(workflow) {
    const progressPercent = workflow.progress_percentage || 0;
    
    return `
        <div class="workflow-card bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-800 mb-1">
                        ${workflow.article_title || 'جاري التوليد...'}
                    </h3>
                    <p class="text-sm text-gray-500">
                        ${workflow.current_step || 'في انتظار البدء'}
                    </p>
                </div>
                ${getStatusBadge(workflow.status)}
            </div>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div class="progress-bar h-2" style="width: ${progressPercent}%"></div>
            </div>
            
            <div class="flex items-center justify-between text-sm">
                <div class="flex items-center space-x-2 space-x-reverse">
                    <span class="text-gray-600">التقدم:</span>
                    <span class="font-semibold text-primary">${progressPercent}%</span>
                </div>
                
                ${workflow.word_count ? `
                    <div class="flex items-center space-x-2 space-x-reverse">
                        <i class="fas fa-file-word text-gray-400"></i>
                        <span class="text-gray-600">${workflow.word_count} كلمة</span>
                    </div>
                ` : ''}
            </div>
            
            ${workflow.publishing_results && workflow.publishing_results.length > 0 ? `
                <div class="mt-3 pt-3 border-t border-gray-200">
                    <p class="text-xs text-gray-500 mb-2">المنصات:</p>
                    <div class="flex items-center space-x-2 space-x-reverse">
                        ${workflow.publishing_results.map(result => `
                            <div class="flex items-center space-x-1 space-x-reverse">
                                ${getPlatformIcon(result.platform)}
                                ${result.success ? 
                                    '<i class="fas fa-check-circle text-green-500 text-xs"></i>' : 
                                    '<i class="fas fa-times-circle text-red-500 text-xs"></i>'}
                                ${result.post_url ? 
                                    `<a href="${result.post_url}" target="_blank" class="text-xs text-primary hover:underline">
                                        <i class="fas fa-external-link-alt"></i>
                                    </a>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${workflow.error_message ? `
                <div class="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <i class="fas fa-exclamation-triangle ml-1"></i>
                    ${workflow.error_message}
                </div>
            ` : ''}
            
            <div class="mt-3 text-xs text-gray-400">
                <i class="fas fa-clock ml-1"></i>
                ${formatDate(workflow.created_at)}
            </div>
        </div>
    `;
}

/**
 * Update workflows display
 */
function updateWorkflowsDisplay() {
    const container = document.getElementById('workflowsContainer');
    
    if (state.workflows.size === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <i class="fas fa-inbox text-6xl mb-4"></i>
                <p>لا توجد مهام حالياً</p>
                <p class="text-sm mt-2">ابدأ بإنشاء مقال جديد</p>
            </div>
        `;
        return;
    }
    
    // Sort workflows by creation date (newest first)
    const sortedWorkflows = Array.from(state.workflows.values())
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    container.innerHTML = sortedWorkflows
        .map(workflow => createWorkflowCard(workflow))
        .join('');
}

/**
 * Update statistics
 */
function updateStats() {
    document.getElementById('totalArticles').textContent = state.stats.total;
    document.getElementById('publishedArticles').textContent = state.stats.published;
    document.getElementById('processingArticles').textContent = state.stats.processing;
    document.getElementById('failedArticles').textContent = state.stats.failed;
}

/**
 * Calculate statistics from workflows
 */
function calculateStats() {
    state.stats = {
        total: state.workflows.size,
        published: 0,
        processing: 0,
        failed: 0
    };
    
    state.workflows.forEach(workflow => {
        if (workflow.status === 'published') {
            state.stats.published++;
        } else if (workflow.status === 'failed') {
            state.stats.failed++;
        } else {
            state.stats.processing++;
        }
    });
    
    updateStats();
}

/**
 * Add or update workflow
 */
function addOrUpdateWorkflow(workflow) {
    state.workflows.set(workflow.workflow_id, workflow);
    
    // Limit to max workflows
    if (state.workflows.size > CONFIG.maxWorkflows) {
        const oldestKey = Array.from(state.workflows.keys())[0];
        state.workflows.delete(oldestKey);
    }
    
    calculateStats();
    updateWorkflowsDisplay();
}

/**
 * Refresh workflow status
 */
async function refreshWorkflowStatus(workflowId) {
    try {
        const workflow = await getWorkflowStatus(workflowId);
        addOrUpdateWorkflow(workflow);
    } catch (error) {
        console.error(`Error refreshing workflow ${workflowId}:`, error);
    }
}

/**
 * Auto-refresh active workflows
 */
function startAutoRefresh() {
    if (state.refreshTimer) {
        clearInterval(state.refreshTimer);
    }
    
    state.refreshTimer = setInterval(() => {
        // Refresh only active workflows
        state.workflows.forEach((workflow, id) => {
            if (!['published', 'failed'].includes(workflow.status)) {
                refreshWorkflowStatus(id);
            }
        });
    }, CONFIG.refreshInterval);
}

// ==============================================
// Event Handlers
// ==============================================

/**
 * Handle form submission
 */
document.getElementById('createArticleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const createBtn = document.getElementById('createBtn');
    const originalBtnText = createBtn.innerHTML;
    
    try {
        // Disable button
        createBtn.disabled = true;
        createBtn.innerHTML = '<i class="fas fa-spinner animate-spin ml-2"></i> جاري الإنشاء...';
        
        // Collect form data
        const topic = document.getElementById('topicInput').value.trim();
        const language = document.getElementById('languageSelect').value;
        const wordCount = parseInt(document.getElementById('wordCountInput').value);
        const seoLevel = document.getElementById('seoLevelSelect').value;
        const includeImage = document.getElementById('includeImageCheckbox').checked;
        const includeFaq = document.getElementById('includeFaqCheckbox').checked;
        
        // Collect publishing targets
        const publishingTargets = [];
        
        if (document.getElementById('wordpressCheckbox').checked) {
            publishingTargets.push({
                platform: 'wordpress',
                post_status: 'publish'
            });
        }
        
        if (document.getElementById('instagramCheckbox').checked) {
            publishingTargets.push({
                platform: 'instagram'
            });
        }
        
        if (publishingTargets.length === 0) {
            showToast('يرجى اختيار منصة واحدة على الأقل للنشر', 'warning');
            return;
        }
        
        // Build workflow request
        const workflowData = {
            content_params: {
                topic,
                language,
                target_length: wordCount,
                seo_level: seoLevel,
                include_image: includeImage,
                include_faq: includeFaq
            },
            publishing_targets: publishingTargets,
            auto_publish: true
        };
        
        // Execute workflow
        const result = await executeWorkflow(workflowData);
        
        // Add to state
        addOrUpdateWorkflow(result);
        
        // Show success message
        showToast('تم بدء عملية الإنشاء والنشر بنجاح!', 'success');
        
        // Clear form
        document.getElementById('topicInput').value = '';
        
        // Start auto-refresh
        startAutoRefresh();
        
    } catch (error) {
        console.error('Error creating workflow:', error);
        showToast('حدث خطأ أثناء إنشاء المهمة: ' + error.message, 'error');
    } finally {
        // Re-enable button
        createBtn.disabled = false;
        createBtn.innerHTML = originalBtnText;
    }
});

/**
 * Advanced options toggle
 */
document.getElementById('advancedToggle').addEventListener('click', () => {
    const advancedOptions = document.getElementById('advancedOptions');
    const icon = document.querySelector('#advancedToggle i');
    
    if (advancedOptions.classList.contains('hidden')) {
        advancedOptions.classList.remove('hidden');
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    } else {
        advancedOptions.classList.add('hidden');
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    }
});

/**
 * Settings modal
 */
document.getElementById('settingsBtn').addEventListener('click', () => {
    document.getElementById('settingsModal').classList.remove('hidden');
    document.getElementById('settingsModal').classList.add('modal-show');
    document.getElementById('apiUrlInput').value = CONFIG.apiUrl;
});

document.getElementById('closeSettingsBtn').addEventListener('click', () => {
    document.getElementById('settingsModal').classList.add('hidden');
});

document.getElementById('saveSettingsBtn').addEventListener('click', () => {
    const apiUrl = document.getElementById('apiUrlInput').value.trim();
    
    if (!apiUrl) {
        showToast('يرجى إدخال عنوان API صحيح', 'warning');
        return;
    }
    
    CONFIG.apiUrl = apiUrl;
    localStorage.setItem('apiUrl', apiUrl);
    
    showToast('تم حفظ الإعدادات بنجاح', 'success');
    document.getElementById('settingsModal').classList.add('hidden');
});

/**
 * Refresh button
 */
document.getElementById('refreshBtn').addEventListener('click', () => {
    const btn = document.getElementById('refreshBtn');
    btn.classList.add('animate-spin');
    
    // Refresh all workflows
    const promises = Array.from(state.workflows.keys()).map(id => refreshWorkflowStatus(id));
    
    Promise.all(promises).finally(() => {
        setTimeout(() => {
            btn.classList.remove('animate-spin');
        }, 500);
    });
});

// ==============================================
// Initialization
// ==============================================

/**
 * Initialize the dashboard
 */
function init() {
    console.log('AutoPublisherAI Dashboard initialized');
    
    // Load workflows from localStorage
    const savedWorkflows = localStorage.getItem('workflows');
    if (savedWorkflows) {
        try {
            const workflows = JSON.parse(savedWorkflows);
            workflows.forEach(workflow => {
                state.workflows.set(workflow.workflow_id, workflow);
            });
            calculateStats();
            updateWorkflowsDisplay();
        } catch (error) {
            console.error('Error loading saved workflows:', error);
        }
    }
    
    // Start auto-refresh if there are active workflows
    const hasActiveWorkflows = Array.from(state.workflows.values())
        .some(w => !['published', 'failed'].includes(w.status));
    
    if (hasActiveWorkflows) {
        startAutoRefresh();
    }
}

// Save workflows to localStorage before unload
window.addEventListener('beforeunload', () => {
    const workflows = Array.from(state.workflows.values());
    localStorage.setItem('workflows', JSON.stringify(workflows));
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

