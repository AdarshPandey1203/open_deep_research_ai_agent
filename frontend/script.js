document.addEventListener('DOMContentLoaded', () => {
    // Core DOM Elements
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const newChatBtn = document.getElementById("newChatBtn");
    const clearHistoryBtn = document.getElementById("clearHistoryBtn");
    const historyList = document.getElementById("historyList");
    const historyCountBadge = document.getElementById("historyCountBadge");
    const historySearchInput = document.getElementById("historySearchInput");
    
    // Theme elements
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeIcon = document.getElementById("themeIcon");
    
    // Header & Modes
    const sessionTitle = document.getElementById("sessionTitle");
    const systemStatusLabel = document.getElementById("systemStatusLabel");
    const exportBtn = document.getElementById("exportBtn");
    const modeDeepResearch = document.getElementById("modeDeepResearch");
    const modeChat = document.getElementById("modeChat");
    const activeModeBadge = document.getElementById("activeModeBadge");
    let currentMode = "deep_research";

    // Chat Viewport
    const chatViewport = document.getElementById("chatViewport");
    const heroState = document.getElementById("heroState");
    const messagesList = document.getElementById("messagesList");
    const researchProgress = document.getElementById("researchProgress");
    const progressText = document.getElementById("progressText");
    const stepElements = [
        document.getElementById("step1"),
        document.getElementById("step2"),
        document.getElementById("step3"),
        document.getElementById("step4")
    ];

    // Input Elements
    const queryInput = document.getElementById("queryInput");
    const sendBtn = document.getElementById("sendBtn");
    const attachBtn = document.getElementById("attachBtn");
    const fileInput = document.getElementById("fileInput");
    const attachedFilesRow = document.getElementById("attachedFilesRow");

    // Settings Modal
    const settingsBtn = document.getElementById("settingsBtn");
    const settingsModal = document.getElementById("settingsModal");
    const closeModalBtn = document.getElementById("closeModalBtn");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const toggleKeyVisibility = document.getElementById("toggleKeyVisibility");
    const saveKeyBtn = document.getElementById("saveKeyBtn");
    const apiStatusMessage = document.getElementById("apiStatusMessage");
    const toast = document.getElementById("toast");

    // Local State
    let currentChatId = null;
    let selectedFiles = [];
    let progressTimer = null;
    let cachedHistory = [];

    // Configure marked.js with highlight.js syntax highlighting
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                if (window.hljs) {
                    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                    return hljs.highlight(code, { language }).value;
                }
                return code;
            }
        });
    }

    // Helper: Toast Notifications
    function showToast(message, duration = 3000) {
        toast.textContent = message;
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, duration);
    }

    // --- Theme Controller ---
    function applyTheme() {
        const saved = localStorage.getItem("deep_research_theme") || "dark";
        if (saved === "dark") {
            document.body.classList.add("dark-mode");
            themeIcon.textContent = "☀️";
        } else {
            document.body.classList.remove("dark-mode");
            themeIcon.textContent = "🌙";
        }
    }

    themeToggleBtn.addEventListener("click", () => {
        const isDark = document.body.classList.toggle("dark-mode");
        themeIcon.textContent = isDark ? "☀️" : "🌙";
        localStorage.setItem("deep_research_theme", isDark ? "dark" : "light");
    });
    applyTheme();

    // --- Sidebar Toggle ---
    sidebarToggle.addEventListener("click", () => {
        if (window.innerWidth <= 900) {
            sidebar.classList.toggle("mobile-open");
        } else {
            sidebar.classList.toggle("collapsed");
        }
    });

    // Keyboard shortcut for sidebar: Ctrl+B / Cmd+B
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
            e.preventDefault();
            sidebarToggle.click();
        }
    });

    // --- Mode Selection Controller ---
    modeDeepResearch.addEventListener("click", () => {
        currentMode = "deep_research";
        modeDeepResearch.classList.add("active");
        modeChat.classList.remove("active");
        queryInput.placeholder = "Enter research topic or question for academic literature synthesis...";
        activeModeBadge.innerHTML = "Mode: <b>Deep Research (arXiv + Web)</b>";
    });

    modeChat.addEventListener("click", () => {
        currentMode = "chat";
        modeChat.classList.add("active");
        modeDeepResearch.classList.remove("active");
        queryInput.placeholder = "Ask a question, analyze an attached PDF, or paste a URL...";
        activeModeBadge.innerHTML = "Mode: <b>Fast AI Chat</b>";
    });

    // Preset query launcher for hero cards
    window.setQuery = (text) => {
        queryInput.value = text;
        queryInput.focus();
        adjustTextareaHeight();
        // Auto scroll to input on mobile
        queryInput.scrollIntoView({ behavior: 'smooth' });
    };

    // --- Auto-expanding Textarea ---
    function adjustTextareaHeight() {
        queryInput.style.height = 'auto';
        queryInput.style.height = Math.min(queryInput.scrollHeight, 160) + 'px';
    }
    queryInput.addEventListener("input", adjustTextareaHeight);

    queryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // --- File Attachments ---
    attachBtn.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        for (const file of fileInput.files) {
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        }
        renderFileChips();
        fileInput.value = "";
    });

    function renderFileChips() {
        attachedFilesRow.innerHTML = "";
        selectedFiles.forEach((file, index) => {
            const sizeKb = (file.size / 1024).toFixed(1);
            const chip = document.createElement("div");
            chip.className = "file-chip";
            chip.innerHTML = `
                <span>📄 ${file.name} (${sizeKb} KB)</span>
                <span class="remove-file" data-index="${index}">&times;</span>
            `;
            chip.querySelector(".remove-file").addEventListener("click", (e) => {
                const idx = parseInt(e.target.dataset.index);
                selectedFiles.splice(idx, 1);
                renderFileChips();
            });
            attachedFilesRow.appendChild(chip);
        });
    }

    // --- Animated Pipeline Progress ---
    function startProgress(isDeepResearch = true) {
        researchProgress.classList.remove("hidden");
        systemStatusLabel.textContent = isDeepResearch ? "Researching..." : "Thinking...";
        
        stepElements.forEach((el, idx) => {
            el.className = idx === 0 ? "pipeline-step active" : "pipeline-step";
        });

        const messages = [
            "Decomposing research query & generating sub-questions...",
            "Searching arXiv academic preprints & web repositories...",
            "Extracting content & cleaning primary literature...",
            "Synthesizing comprehensive peer-grade research report..."
        ];

        progressText.textContent = messages[0];
        let stepIdx = 0;

        if (isDeepResearch) {
            progressTimer = setInterval(() => {
                if (stepIdx < 3) {
                    stepIdx++;
                    stepElements.forEach((el, i) => {
                        el.className = i <= stepIdx ? "pipeline-step active" : "pipeline-step";
                    });
                    progressText.textContent = messages[stepIdx];
                }
            }, 3000);
        }
    }

    function stopProgress() {
        clearInterval(progressTimer);
        researchProgress.classList.add("hidden");
        systemStatusLabel.textContent = "Ready";
    }

    // --- Message Card Rendering ---
    function appendMessageCard(role, content) {
        heroState.classList.add("hidden");

        const card = document.createElement("div");
        card.className = `message-card ${role}`;

        const isUser = role === "user";
        const authorName = isUser ? "You" : "Deep Research Agent";
        const badgeIcon = isUser ? "👤" : "🔬";
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let bodyHtml = "";
        let summaryHtml = "";
        let sourcesHtml = "";

        if (typeof content === "object" && content !== null) {
            const rawBody = content.body || "";
            bodyHtml = window.marked ? marked.parse(rawBody) : rawBody.replace(/\n/g, "<br>");

            // Executive Summary Box
            if (content.summary) {
                summaryHtml = `
                    <div class="summary-box">
                        <div class="summary-title">
                            <span>💡</span> Executive Summary
                        </div>
                        <div class="summary-text">${content.summary}</div>
                    </div>
                `;
            }

            // Primary Sources Grid
            if (content.research_papers && content.research_papers.length > 0) {
                let cardsHtml = "";
                content.research_papers.forEach(p => {
                    const title = p.title || p.href || "Academic Paper";
                    const sourceTag = (p.source || "Literature").toLowerCase();
                    const badgeClass = sourceTag.includes("arxiv") ? "arxiv" : "web";
                    const snippet = p.body || "Primary citation source.";

                    cardsHtml += `
                        <a href="${p.href}" target="_blank" rel="noopener noreferrer" class="source-card" title="${title}">
                            <div class="source-header-row">
                                <span class="source-badge ${badgeClass}">${p.source || 'Source'}</span>
                                <span class="source-arrow">↗</span>
                            </div>
                            <div class="source-name">${title}</div>
                            <div class="source-excerpt">${snippet}</div>
                        </a>
                    `;
                });

                sourcesHtml = `
                    <div class="sources-section">
                        <div class="sources-title">
                            <span>📚</span> Primary Literature & Citations
                        </div>
                        <div class="sources-grid">${cardsHtml}</div>
                    </div>
                `;
            }
        } else {
            const raw = String(content || "");
            bodyHtml = window.marked ? marked.parse(raw) : raw.replace(/\n/g, "<br>");
        }

        // Action Toolbar
        let actionsHtml = "";
        if (!isUser) {
            actionsHtml = `
                <div class="message-actions">
                    <button class="action-btn copy-btn" title="Copy text to clipboard">
                        📋 Copy Report
                    </button>
                    <button class="action-btn export-single-btn" title="Save as .MD file">
                        📥 Download .MD
                    </button>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="message-meta">
                <span class="message-author">
                    <span class="message-author-badge">${badgeIcon}</span>
                    <span>${authorName}</span>
                </span>
                <span>${timeStr}</span>
            </div>
            <div class="message-content">
                ${bodyHtml}
                ${summaryHtml}
                ${sourcesHtml}
            </div>
            ${actionsHtml}
        `;

        // Wire Copy Action
        const copyBtn = card.querySelector(".copy-btn");
        if (copyBtn) {
            copyBtn.addEventListener("click", () => {
                const text = card.querySelector(".message-content").innerText;
                navigator.clipboard.writeText(text).then(() => {
                    showToast("Report copied to clipboard!");
                });
            });
        }

        // Wire Single Download Action
        const exportSingleBtn = card.querySelector(".export-single-btn");
        if (exportSingleBtn) {
            exportSingleBtn.addEventListener("click", () => {
                const text = card.querySelector(".message-content").innerText;
                const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `research_synthesis_${Date.now()}.md`;
                a.click();
                URL.revokeObjectURL(url);
            });
        }

        messagesList.appendChild(card);
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    // --- Message Send Logic ---
    async function sendMessage() {
        const query = queryInput.value.trim();
        const filesToSend = [...selectedFiles];

        if (!query && filesToSend.length === 0) {
            showToast("Please enter a research topic or attach a document!");
            return;
        }

        // Display user message in chat
        let userDisplay = query;
        if (filesToSend.length > 0) {
            const names = filesToSend.map(f => f.name).join(", ");
            userDisplay = query ? `📄 **Attached (${names})**\n\n${query}` : `📄 **Attached Document(s)**: ${names}`;
        }
        appendMessageCard("user", userDisplay);

        // Reset inputs
        queryInput.value = "";
        adjustTextareaHeight();
        selectedFiles = [];
        renderFileChips();

        startProgress(currentMode === "deep_research");
        sendBtn.disabled = true;

        const formData = new FormData();
        formData.append("user_input", query);
        formData.append("mode", currentMode);
        if (currentChatId !== null) {
            formData.append("chat_id", currentChatId);
        }
        for (const file of filesToSend) {
            formData.append("file", file);
        }

        try {
            const res = await fetch("/chat", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            stopProgress();

            if (data.error) {
                appendMessageCard("assistant", `⚠️ **Error**: ${data.error}`);
            } else {
                currentChatId = data.chat_id;
                appendMessageCard("assistant", data.assistant_message.content);
                loadHistory(); // Refresh history
            }
        } catch (err) {
            stopProgress();
            appendMessageCard("assistant", `⚠️ **Network Error**: Unable to reach backend server (${err.message}).`);
        } finally {
            sendBtn.disabled = false;
            queryInput.focus();
        }
    }

    sendBtn.addEventListener("click", sendMessage);

    // --- History Sidebar Controller ---
    async function loadHistory() {
        try {
            const res = await fetch("/get_history");
            const data = await res.json();
            cachedHistory = data || [];
            renderHistoryList(cachedHistory);
        } catch (err) {
            console.error("Error loading chat history:", err);
        }
    }

    function renderHistoryList(items) {
        historyList.innerHTML = "";
        historyCountBadge.textContent = items.length;

        if (!items || items.length === 0) {
            const emptyItem = document.createElement("li");
            emptyItem.className = "history-item";
            emptyItem.style.color = "var(--sidebar-muted)";
            emptyItem.style.cursor = "default";
            emptyItem.textContent = "No research history yet";
            historyList.appendChild(emptyItem);
            return;
        }

        items.forEach(chat => {
            const li = document.createElement("li");
            li.className = "history-item";
            if (chat.id === currentChatId) {
                li.classList.add("active");
            }

            const titleSpan = document.createElement("span");
            titleSpan.className = "history-title";
            titleSpan.textContent = chat.title || `Research #${chat.id}`;
            li.appendChild(titleSpan);

            const delBtn = document.createElement("button");
            delBtn.className = "history-del-btn";
            delBtn.innerHTML = "🗑️";
            delBtn.title = "Delete this session";
            delBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                deleteSession(chat.id);
            });
            li.appendChild(delBtn);

            li.addEventListener("click", () => fetchChat(chat.id, chat.title));
            historyList.appendChild(li);
        });
    }

    // Filter history on search input
    historySearchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderHistoryList(cachedHistory);
            return;
        }
        const filtered = cachedHistory.filter(h => (h.title || "").toLowerCase().includes(query));
        renderHistoryList(filtered);
    });

    async function fetchChat(chatId, title = "Research Studio") {
        try {
            startProgress(false);
            const res = await fetch(`/get_chat/${chatId}`);
            const messages = await res.json();
            
            messagesList.innerHTML = "";
            heroState.classList.add("hidden");
            currentChatId = chatId;
            sessionTitle.textContent = title;

            messages.forEach(msg => {
                if (msg.role !== 'context') {
                    appendMessageCard(msg.role, msg.content);
                }
            });

            loadHistory();
        } catch (err) {
            showToast("Failed to load chat session.");
        } finally {
            stopProgress();
        }
    }

    async function deleteSession(chatId) {
        if (!confirm("Are you sure you want to delete this research session?")) return;

        try {
            const res = await fetch(`/delete_chat/${chatId}`, { method: "POST" });
            if (res.ok) {
                showToast("Research session deleted.");
                if (currentChatId === chatId) {
                    resetToNewChat();
                }
                loadHistory();
            }
        } catch (err) {
            showToast("Error deleting session.");
        }
    }

    clearHistoryBtn.addEventListener("click", async () => {
        if (!confirm("Delete all research history? This action is permanent.")) return;

        try {
            const res = await fetch("/clear_history", { method: "POST" });
            if (res.ok) {
                showToast("All research history cleared.");
                resetToNewChat();
                loadHistory();
            }
        } catch (err) {
            showToast("Failed to clear history.");
        }
    });

    function resetToNewChat() {
        currentChatId = null;
        messagesList.innerHTML = "";
        heroState.classList.remove("hidden");
        sessionTitle.textContent = "Research Studio";
        selectedFiles = [];
        renderFileChips();
        queryInput.value = "";
        adjustTextareaHeight();
        loadHistory();
    }

    newChatBtn.addEventListener("click", resetToNewChat);

    // --- Export Full Session ---
    exportBtn.addEventListener("click", () => {
        if (currentChatId === null) {
            showToast("No active research session to export.");
            return;
        }
        window.open(`/export_chat/${currentChatId}`, '_blank');
    });

    // --- Settings Modal & API Key Visibility ---
    settingsBtn.addEventListener("click", async () => {
        settingsModal.classList.remove("hidden");
        apiStatusMessage.className = "status-msg";
        apiStatusMessage.style.display = "none";
        
        try {
            const res = await fetch("/api/config");
            const data = await res.json();
            if (data.api_key_configured) {
                apiStatusMessage.textContent = `Active Key Configured: ${data.masked_key}`;
                apiStatusMessage.className = "status-msg success";
                apiStatusMessage.style.display = "block";
            }
        } catch (e) {}
    });

    closeModalBtn.addEventListener("click", () => {
        settingsModal.classList.add("hidden");
    });

    toggleKeyVisibility.addEventListener("click", () => {
        if (apiKeyInput.type === "password") {
            apiKeyInput.type = "text";
            toggleKeyVisibility.textContent = "🙈";
        } else {
            apiKeyInput.type = "password";
            toggleKeyVisibility.textContent = "👁️";
        }
    });

    saveKeyBtn.addEventListener("click", async () => {
        const key = apiKeyInput.value.trim();
        if (!key) {
            apiStatusMessage.textContent = "Please enter an API key.";
            apiStatusMessage.className = "status-msg error";
            apiStatusMessage.style.display = "block";
            return;
        }

        saveKeyBtn.disabled = true;
        try {
            const res = await fetch("/api/set_key", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ api_key: key })
            });
            const data = await res.json();
            if (data.status === "success") {
                apiStatusMessage.textContent = "API Key saved successfully! Live Gemini models active.";
                apiStatusMessage.className = "status-msg success";
                apiStatusMessage.style.display = "block";
                apiKeyInput.value = "";
                setTimeout(() => {
                    settingsModal.classList.add("hidden");
                    showToast("Gemini API Key updated successfully!");
                }, 1200);
            } else {
                apiStatusMessage.textContent = data.error || "Failed to update key.";
                apiStatusMessage.className = "status-msg error";
                apiStatusMessage.style.display = "block";
            }
        } catch (err) {
            apiStatusMessage.textContent = "Network error updating key.";
            apiStatusMessage.className = "status-msg error";
            apiStatusMessage.style.display = "block";
        } finally {
            saveKeyBtn.disabled = false;
        }
    });

    // Close modal on outer overlay click
    settingsModal.addEventListener("click", (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.add("hidden");
        }
    });

    // Initial Load
    loadHistory();
});
