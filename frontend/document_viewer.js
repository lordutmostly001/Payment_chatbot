/**
 * Document Viewer Component
 * Displays source documents in a modal overlay
 */

class DocumentViewer {
    constructor() {
        this.isOpen = false;
        this.currentDocument = null;
        this.render();
        this.attachEventListeners();
    }

    render() {
        const modal = document.createElement('div');
        modal.id = 'documentViewerModal';
        modal.className = 'document-modal';
        modal.innerHTML = `
            <div class="modal-overlay" id="modalOverlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="documentTitle">Document Viewer</h3>
                    <button class="close-button" id="closeModal">&times;</button>
                </div>
                <div class="modal-body" id="documentContent">
                    <div class="document-info">
                        <p class="info-text">Select a source document from the chat to view it here.</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.addStyles();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .document-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 1000;
            }

            .document-modal.open {
                display: block;
            }

            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
            }

            .modal-content {
                position: relative;
                width: 90%;
                max-width: 900px;
                height: 80vh;
                margin: 5vh auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                display: flex;
                flex-direction: column;
                animation: modalSlideIn 0.3s ease-out;
            }

            @keyframes modalSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-50px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .modal-header h3 {
                margin: 0;
                color: #333;
                font-size: 1.3em;
            }

            .close-button {
                background: none;
                border: none;
                font-size: 2em;
                color: #999;
                cursor: pointer;
                line-height: 1;
                padding: 0;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                transition: all 0.2s;
            }

            .close-button:hover {
                background: #f5f5f5;
                color: #333;
            }

            .modal-body {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }

            .document-info {
                text-align: center;
                padding: 40px;
            }

            .info-text {
                color: #666;
                font-size: 1.1em;
            }

            .document-metadata {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }

            .metadata-item {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e0e0e0;
            }

            .metadata-item:last-child {
                border-bottom: none;
            }

            .metadata-label {
                font-weight: 600;
                color: #555;
            }

            .metadata-value {
                color: #666;
            }

            .document-preview {
                background: white;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                line-height: 1.6;
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            .loading-spinner {
                text-align: center;
                padding: 40px;
            }

            .spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .error-message {
                background: #fee;
                border: 1px solid #fcc;
                padding: 15px;
                border-radius: 8px;
                color: #c33;
            }
        `;
        document.head.appendChild(style);
    }

    attachEventListeners() {
        const modal = document.getElementById('documentViewerModal');
        const overlay = document.getElementById('modalOverlay');
        const closeButton = document.getElementById('closeModal');

        closeButton.addEventListener('click', () => this.close());
        overlay.addEventListener('click', () => this.close());

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    async openDocument(documentPath) {
        this.currentDocument = documentPath;
        const modal = document.getElementById('documentViewerModal');
        const title = document.getElementById('documentTitle');
        const content = document.getElementById('documentContent');

        // Extract filename from path
        const filename = documentPath.split('/').pop().split('\\').pop();
        title.textContent = filename;

        // Show modal
        modal.classList.add('open');
        this.isOpen = true;

        // Show loading
        content.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading document...</p>
            </div>
        `;

        try {
            // In a real implementation, you would fetch the document content
            // For now, we'll show metadata and a preview
            await this.loadDocumentContent(documentPath);
        } catch (error) {
            content.innerHTML = `
                <div class="error-message">
                    <strong>Error loading document:</strong>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    async loadDocumentContent(documentPath) {
        const content = document.getElementById('documentContent');

        // Simulated document metadata and preview
        // In production, you would fetch this from your API
        const metadata = {
            filename: documentPath.split('/').pop().split('\\').pop(),
            path: documentPath,
            type: this.getDocumentType(documentPath),
            size: 'N/A',
            lastModified: 'N/A'
        };

        content.innerHTML = `
            <div class="document-metadata">
                <div class="metadata-item">
                    <span class="metadata-label">📄 Filename:</span>
                    <span class="metadata-value">${metadata.filename}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">📂 Path:</span>
                    <span class="metadata-value">${metadata.path}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">📋 Type:</span>
                    <span class="metadata-value">${metadata.type}</span>
                </div>
            </div>
            <div class="document-info">
                <p class="info-text">
                    This document was used as a source for the chatbot's response.
                    Full document preview coming soon.
                </p>
                <p style="margin-top: 20px; color: #999; font-size: 0.9em;">
                    💡 Tip: Documents are stored in the vector database and used for RAG retrieval.
                </p>
            </div>
        `;
    }

    getDocumentType(path) {
        const filename = path.toLowerCase();
        if (filename.includes('upi')) return 'UPI Transaction';
        if (filename.includes('api') || filename.includes('bank')) return 'Bank API Response';
        if (filename.includes('compliance') || filename.includes('kyc')) return 'Compliance Report';
        if (filename.includes('sla') || filename.includes('partnership')) return 'Partnership SLA';
        return 'Payment Document';
    }

    close() {
        const modal = document.getElementById('documentViewerModal');
        modal.classList.remove('open');
        this.isOpen = false;
        this.currentDocument = null;
    }

    isModalOpen() {
        return this.isOpen;
    }
}

// Initialize globally
window.documentViewer = new DocumentViewer();
window.DocumentViewer = DocumentViewer;