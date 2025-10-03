/**
 * Role Selector Component
 * Manages stakeholder role selection with descriptions
 */

class RoleSelector {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedRole = null;
        
        this.roles = [
            {
                value: '',
                label: 'Auto-detect',
                description: 'Let AI detect the best role based on your question',
                icon: '🤖'
            },
            {
                value: 'product_lead',
                label: 'Product Lead',
                description: 'Focus on metrics, trends, and user behavior',
                icon: '📊'
            },
            {
                value: 'tech_lead',
                label: 'Tech Lead',
                description: 'Technical issues, errors, and API integration',
                icon: '⚙️'
            },
            {
                value: 'compliance_lead',
                label: 'Compliance Lead',
                description: 'Regulatory requirements, KYC, and audit',
                icon: '⚖️'
            },
            {
                value: 'bank_alliance_lead',
                label: 'Bank Alliance Lead',
                description: 'SLA, partnerships, and integration health',
                icon: '🏦'
            }
        ];

        this.render();
        this.attachEventListeners();
    }

    render() {
        const html = `
            <div class="role-selector-component">
                <label for="roleSelect" style="display: block; margin-bottom: 8px; font-weight: 500; color: #555;">
                    Select your role:
                </label>
                <select id="roleSelect" class="role-select">
                    ${this.roles.map(role => `
                        <option value="${role.value}">
                            ${role.icon} ${role.label}
                        </option>
                    `).join('')}
                </select>
                <div id="roleDescription" class="role-description"></div>
            </div>
        `;

        this.container.innerHTML = html;
        this.addStyles();
        this.updateDescription();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .role-selector-component {
                margin-bottom: 20px;
            }

            .role-select {
                width: 100%;
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                cursor: pointer;
                background: white;
                transition: border-color 0.3s;
            }

            .role-select:hover {
                border-color: #667eea;
            }

            .role-select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .role-description {
                margin-top: 10px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 6px;
                font-size: 0.85em;
                color: #666;
                line-height: 1.4;
                min-height: 40px;
            }

            .role-description:empty {
                display: none;
            }
        `;
        document.head.appendChild(style);
    }

    attachEventListeners() {
        const select = document.getElementById('roleSelect');
        select.addEventListener('change', () => {
            this.selectedRole = select.value;
            this.updateDescription();
            this.onRoleChange(this.selectedRole);
        });
    }

    updateDescription() {
        const select = document.getElementById('roleSelect');
        const descriptionDiv = document.getElementById('roleDescription');
        
        const selectedRole = this.roles.find(r => r.value === select.value);
        if (selectedRole) {
            descriptionDiv.textContent = selectedRole.description;
        }
    }

    getSelectedRole() {
        return this.selectedRole || null;
    }

    setRole(roleValue) {
        const select = document.getElementById('roleSelect');
        if (select) {
            select.value = roleValue;
            this.selectedRole = roleValue;
            this.updateDescription();
        }
    }

    onRoleChange(role) {
        // Callback for when role changes
        // Can be overridden or extended
        console.log('Role changed to:', role || 'auto-detect');
    }
}

// Make available globally
window.RoleSelector = RoleSelector;