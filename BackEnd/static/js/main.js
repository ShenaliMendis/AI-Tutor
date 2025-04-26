/**
 * AI Tutor - Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add loading indicators to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Loading...
                `;
                
                // Store original text for restoration
                submitButton.setAttribute('data-original-text', originalText);
                
                // Add a loading overlay
                const loadingOverlay = document.createElement('div');
                loadingOverlay.className = 'loading-overlay';
                loadingOverlay.innerHTML = `
                    <div class="spinner-grow text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Generating content with AI...</p>
                    <p class="small text-muted">This may take up to 30 seconds</p>
                `;
                document.body.appendChild(loadingOverlay);
            }
        });
    });
    
    // Add automatic link detection to lesson content
    const lessonContent = document.getElementById('lesson-content');
    if (lessonContent) {
        // Make links open in new tab
        const links = lessonContent.querySelectorAll('a');
        links.forEach(link => {
            if (!link.hasAttribute('target')) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });
        
        // Add line numbers to code blocks
        const codeBlocks = lessonContent.querySelectorAll('pre code');
        codeBlocks.forEach(codeBlock => {
            const lines = codeBlock.textContent.split('\n');
            if (lines.length > 5) { // Only add line numbers if there are more than 5 lines
                let lineNumbersContent = '';
                let codeContent = '';
                
                lines.forEach((line, index) => {
                    lineNumbersContent += `<span class="line-number">${index + 1}</span>`;
                    codeContent += `<span class="line">${line}</span>`;
                });
                
                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-with-line-numbers';
                
                const lineNumbers = document.createElement('div');
                lineNumbers.className = 'line-numbers';
                lineNumbers.innerHTML = lineNumbersContent;
                
                const codeLines = document.createElement('div');
                codeLines.className = 'code-lines';
                codeLines.innerHTML = codeContent;
                
                wrapper.appendChild(lineNumbers);
                wrapper.appendChild(codeLines);
                
                // Replace the original code block
                codeBlock.parentNode.replaceWith(wrapper);
            }
        });
    }
    
    // Add tooltips to quiz options
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add progress tracking
    updateProgress();
    
    function updateProgress() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const value = bar.getAttribute('aria-valuenow');
            bar.style.width = `${value}%`;
        });
    }
});

// Add a CSS class to style code blocks after Prism.js syntax highlighting
window.addEventListener('load', function() {
    document.querySelectorAll('pre').forEach(pre => {
        pre.classList.add('styled-code-block');
    });
});

// Style for loading overlay
const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.9);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .code-block-with-line-numbers {
        display: flex;
        background-color: #282c34;
        border-radius: 0.5rem;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .line-numbers {
        display: flex;
        flex-direction: column;
        padding: 1rem 0.5rem;
        background-color: rgba(0, 0, 0, 0.2);
        color: #abb2bf;
        text-align: right;
        user-select: none;
    }
    
    .code-lines {
        flex-grow: 1;
        padding: 1rem;
        overflow-x: auto;
        color: #abb2bf;
    }
    
    .line {
        display: block;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    }
    
    .styled-code-block {
        position: relative;
    }
`;
document.head.appendChild(style);
