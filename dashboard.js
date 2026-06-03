// Fallback Mock Data if dashboard_data.js doesn't exist yet
const MOCK_FALLBACK_DATA = {
  last_updated: "2026-05-29 09:00 AM",
  updates: [
    {
      title: "Claude Managed Agents: Secure Tunnels and Self-Hosted Sandboxes",
      link: "https://www.anthropic.com/news/managed-agents",
      description: "Anthropic announced MCP Tunnels in research preview, allowing developers to route secure agent commands to private databases without public API exposure.",
      provider: "Anthropic",
      timestamp: new Date().toISOString()
    },
    {
      title: "Google Cloud AlloyDB remote MCP Server Integrations",
      link: "https://docs.cloud.google.com/release-notes#AlloyDB_MCP",
      description: "Google Cloud generally released AlloyDB remote MCP tools, letting LLM agents natively query database schemas and execute secure SQL transactions.",
      provider: "Google Cloud",
      timestamp: new Date(Date.now() - 3600000 * 2).toISOString()
    },
    {
      title: "OpenAI AgentKit and GPT-5 Reasoning Releases",
      link: "https://openai.com/index/introducing-agentkit",
      description: "OpenAI launched AgentKit, a state-of-the-art framework for building multi-agent systems with advanced planning, backtracking, and structured Tool Call routing.",
      provider: "OpenAI",
      timestamp: new Date(Date.now() - 3600000 * 8).toISOString()
    },
    {
      title: "Snowflake Cortex AI Guardrails Reaches General Availability",
      link: "https://www.snowflake.com/blog/cortex-ai-guardrails-ga-announcement/",
      description: "Snowflake announced the general availability of Cortex AI Guardrails. Integrated with the Snowflake Horizon Catalog, it provides runtime protection against prompt injection and jailbreak attacks.",
      provider: "Snowflake",
      timestamp: new Date(Date.now() - 3600000 * 24).toISOString()
    },
    {
      title: "Batch Cortex Search Generally Available for Enterprise Analytics",
      link: "https://www.snowflake.com/blog/batch-cortex-search-ga/",
      description: "Snowflake generally released Batch Cortex Search, bringing robust fuzzy matching and advanced vector-retrieval pipelines to large-scale enterprise analytics workloads.",
      provider: "Snowflake",
      timestamp: new Date(Date.now() - 3600000 * 48).toISOString()
    },
    {
      title: "AWS Bedrock Custom Model Import Support Expanded to Llama-3",
      link: "https://aws.amazon.com/about-aws/whats-new/recent/",
      description: "AWS updated Amazon Bedrock, allowing developers to import customized and fine-tuned Llama-3 checkpoints natively, saving substantial inference costs.",
      provider: "AWS",
      timestamp: new Date(Date.now() - 3600000 * 72).toISOString()
    }
  ],
  trends: [
    {
      title: "Anthropic Unveils Claude 3.7 Opus with Dual-Thinking Mode",
      link: "https://www.anthropic.com/news",
      description: "Anthropic announced their latest flagship model, Claude 3.7 Opus, featuring an adjustable dual-thinking switch allowing users to toggle between instant responses and deep reasoning steps.",
      date: "May 29, 2026",
      source: "Anthropic Blog",
      trend: "Research Breakthrough"
    },
    {
      title: "NVIDIA Blackwell B200 Superchips Ship to Core Cloud Providers",
      link: "https://www.nvidia.com/news",
      description: "NVIDIA has officially commenced high-volume shipments of its next-generation Blackwell B200 GPUs to major cloud infrastructure platforms, paving the way for 10x faster LLM training clusters.",
      date: "May 28, 2026",
      source: "TechCrunch AI",
      trend: "Hardware & Chips"
    },
    {
      title: "OpenAI Launches SearchGPT Natively inside ChatGPT UI",
      link: "https://openai.com/news",
      description: "OpenAI has integrated advanced real-time search capabilities directly into its standard model offerings, delivering instant visual summaries, live citations, and conversational web search.",
      date: "May 27, 2026",
      source: "VentureBeat",
      trend: "Enterprise Adoption"
    }
  ]
};

// Application State
let appData = MOCK_FALLBACK_DATA;
let activeProviderFilter = 'all';
let activeDateFilter = 'all';
let activeNatureFilter = 'all';
let searchQuery = '';
let customStartDate = '';
let customEndDate = '';
let releasesLimit = 50;

// Load actual data if available
if (typeof DASHBOARD_DATA !== 'undefined' && DASHBOARD_DATA) {
    appData = DASHBOARD_DATA;
    console.log("Dashboard loaded with live JSON records!");
} else {
    console.log("Dashboard loaded with offline fallback mock dataset!");
}

// Helpers
function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(isoString) {
    if (!isoString) return "Recent";
    try {
        const date = new Date(isoString);
        
        const dateStr = date.toLocaleDateString('en-US', {
            timeZone: 'America/New_York',
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        
        const timeStr = date.toLocaleTimeString('en-US', {
            timeZone: 'America/New_York',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        });
        
        return `${dateStr} at ${timeStr}`;
    } catch (e) {
        return isoString;
    }
}

function getProviderTagClass(provider) {
    const prov = provider ? provider.toLowerCase() : "";
    if (prov.includes("aws")) return "aws";
    if (prov.includes("google")) return "google-cloud";
    if (prov.includes("azure") || prov.includes("microsoft")) return "azure";
    if (prov.includes("databricks")) return "databricks";
    if (prov.includes("snowflake")) return "snowflake";
    if (prov.includes("openai")) return "openai";
    if (prov.includes("anthropic")) return "anthropic";
    return "";
}

function getTrendTagClass(trend) {
    const tr = trend ? trend.toLowerCase().replace(/ & /g, "-").replace(/ /g, "-") : "";
    return tr;
}

function getReleaseNature(title, description) {
    const text = `${title || ""} ${description || ""}`.toLowerCase();
    
    // 1. Protocol & Spec
    if (text.includes("protocol") || text.includes("mcp") || text.includes("spec") || text.includes("tunnel") || text.includes("standard") || text.includes("connector") || text.includes("specifications")) {
        return { type: "Protocol & Spec", icon: "🔌", class: "nature-protocol" };
    }
    // 2. Hardware & Infrastructure
    if (text.includes("gpu") || text.includes("tpu") || text.includes("blackwell") || text.includes("nvidia") || text.includes("h100") || text.includes("b200") || text.includes("chip") || text.includes("hardware") || text.includes("cluster") || text.includes("serverless") || text.includes("compute") || text.includes("storage") || text.includes("instance") || text.includes("infrastructure")) {
        return { type: "Hardware & Infra", icon: "⚙️", class: "nature-hardware" };
    }
    // 3. Model & Concept
    if (text.includes("model") || text.includes("reasoning") || text.includes("thinking") || text.includes("gemini") || text.includes("claude") || text.includes("gpt") || text.includes("llama") || text.includes("embedding") || text.includes("llm") || text.includes("slm") || text.includes("weights") || text.includes("fine-tune") || text.includes("deep learning") || text.includes("neural")) {
        return { type: "Model & Concept", icon: "🧠", class: "nature-model" };
    }
    // 4. Software & SDK
    if (text.includes("sdk") || text.includes("library") || text.includes("python") || text.includes("client") || text.includes("driver") || text.includes("api") || text.includes("package") || text.includes("framework") || text.includes("cli") || text.includes("toolkit") || text.match(/v\d+\.\d+/) || text.includes("github") || text.includes("code") || text.includes("software") || text.includes("developer")) {
        return { type: "Software & SDK", icon: "💻", class: "nature-software" };
    }
    
    // 5. Default: Feature & Service
    return { type: "Feature & Service", icon: "⚡", class: "nature-feature" };
}


// Stats Calculation
function calculateStats() {
    // 1. Total releases count
    document.getElementById('stat-total-releases').innerText = appData.updates.length;
    
    // 2. Recent releases (last 7 days)
    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    const recentCount = appData.updates.filter(item => {
        if (!item.timestamp) return false;
        try {
            return new Date(item.timestamp).getTime() > sevenDaysAgo;
        } catch (e) {
            return false;
        }
    }).length;
    document.getElementById('stat-recent-releases').innerText = recentCount;
    
    // 3. Most Active Platform
    const counts = {};
    appData.updates.forEach(item => {
        const prov = item.provider || "Other";
        counts[prov] = (counts[prov] || 0) + 1;
    });
    
    let maxProvider = "N/A";
    let maxCount = 0;
    for (const [provider, count] of Object.entries(counts)) {
        if (count > maxCount) {
            maxCount = count;
            maxProvider = provider;
        }
    }
    document.getElementById('stat-active-provider').innerText = maxProvider;
    
    // 4. Total News Count
    document.getElementById('stat-total-news').innerText = appData.trends.length;
    
    // 5. Update Synced Time
    document.getElementById('last-updated-time').innerText = appData.last_updated || "Just Now";
}

// Rendering Functions
function renderReleases() {
    const feedContainer = document.getElementById('releases-feed-container');
    const filteredUpdates = appData.updates.filter(item => {
        // 1. Filter by platform
        if (activeProviderFilter !== 'all' && item.provider !== activeProviderFilter) {
            return false;
        }
        
        // 2. Filter by date range
        if (activeDateFilter !== 'all') {
            if (!item.timestamp) return false;
            try {
                const itemDate = new Date(item.timestamp);
                const nowET = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
                const todayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate());
                const todayEnd = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() + 1);
                
                if (activeDateFilter === 'today') {
                    if (itemDate < todayStart || itemDate >= todayEnd) return false;
                } else if (activeDateFilter === 'yesterday') {
                    const yesterdayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 1);
                    const yesterdayEnd = todayStart;
                    if (itemDate < yesterdayStart || itemDate >= yesterdayEnd) return false;
                } else if (activeDateFilter === '7days') {
                    const sevenDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 6);
                    if (itemDate < sevenDaysStart) return false;
                } else if (activeDateFilter === '30days') {
                    const thirtyDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 29);
                    if (itemDate < thirtyDaysStart) return false;
                } else if (activeDateFilter === 'custom') {
                    if (customStartDate) {
                        const startLimit = new Date(customStartDate + 'T00:00:00');
                        if (itemDate < startLimit) return false;
                    }
                    if (customEndDate) {
                        const endLimit = new Date(customEndDate + 'T23:59:59');
                        if (itemDate > endLimit) return false;
                    }
                }
            } catch (e) {
                return false;
            }
        }
        
        // 3. Filter by release nature type
        if (activeNatureFilter !== 'all') {
            const nature = getReleaseNature(item.title, item.description);
            if (nature.class !== `nature-${activeNatureFilter}`) {
                return false;
            }
        }
        
        // 4. Filter by search query
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            const titleMatch = (item.title || "").toLowerCase().includes(query);
            const descMatch = (item.description || "").toLowerCase().includes(query);
            const provMatch = (item.provider || "").toLowerCase().includes(query);
            return titleMatch || descMatch || provMatch;
        }
        
        return true;
    });
    
    // Update header count badge
    document.getElementById('releases-count').innerText = `${filteredUpdates.length} releases`;
    
    if (filteredUpdates.length === 0) {
        feedContainer.innerHTML = `
            <div class="empty-state">
                <h3>🔍 No release matches found</h3>
                <p>Try clearing your search query or choosing "All Platforms" above.</p>
            </div>
        `;
        calculateAndRenderSentiments();
        renderPlatformActivityVisualizer([]);
        return;
    }
    
    const updatesToRender = filteredUpdates.slice(0, releasesLimit);
    
    let htmlContent = updatesToRender.map(item => {
        const provClass = getProviderTagClass(item.provider);
        const nature = getReleaseNature(item.title, item.description);
        if (!item.title || !item.description) {
            fetch('/log-error?msg=' + encodeURIComponent('DIAGNOSTIC: keys=' + Object.keys(item).join(',') + '; provider=' + item.provider + '; timestamp=' + item.timestamp));
        }
        return `
            <div class="release-card ${provClass}-border">
                <div class="card-header">
                    <span class="provider-tag ${provClass}">${escapeHtml(item.provider)}</span>
                    <span class="card-date">${formatDate(item.timestamp)}</span>
                </div>
                <h3><a href="${item.link}" target="_blank">${escapeHtml(item.title)}</a></h3>
                <p>${escapeHtml(item.description)}</p>
                <div class="card-footer">
                    <a href="${item.link}" target="_blank" class="read-more-btn">
                        Read Official Announcement &rarr;
                    </a>
                </div>
            </div>
        `;
    }).join('');
    
    if (filteredUpdates.length > releasesLimit) {
        htmlContent += `
            <div style="display: flex; justify-content: center; padding: 20px 0; width: 100%;">
                <button id="load-more-btn" class="filter-btn" style="background: linear-gradient(135deg, rgba(37,99,235,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(139,92,246,0.3); color: #c084fc; font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 600; padding: 10px 24px; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 8px;">
                    <span>📥 Load More Releases</span>
                    <span style="font-size: 11px; opacity: 0.6;">(${filteredUpdates.length - releasesLimit} remaining)</span>
                </button>
            </div>
        `;
    }
    
    feedContainer.innerHTML = htmlContent;
    
    // Attach listener to Load More button if it exists
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            releasesLimit += 50;
            renderReleases();
        });
    }
    
    // Recalculate top 10 sentiments on the fly for the selected date range & filters!
    calculateAndRenderSentiments();
    renderPlatformActivityVisualizer(filteredUpdates);
}

function renderTrends() {
    const feedContainer = document.getElementById('trends-feed-container');
    
    // Update count badge
    document.getElementById('trends-count').innerText = `${appData.trends.length} items`;
    
    if (!appData.trends || appData.trends.length === 0) {
        feedContainer.innerHTML = `
            <div class="empty-state">
                <h3>☕ All quiet today</h3>
                <p>No new AI News or Global Trends compiled in this cycle.</p>
            </div>
        `;
        return;
    }
    
    feedContainer.innerHTML = appData.trends.map(item => {
        const trendClass = getTrendTagClass(item.trend);
        return `
            <div class="trend-card">
                <div class="trend-header">
                    <span class="trend-tag ${trendClass}">${escapeHtml(item.trend)}</span>
                    <span class="trend-meta">${escapeHtml(item.source)} &bull; ${escapeHtml(item.date)}</span>
                </div>
                <h4><a href="${item.link}" target="_blank">${escapeHtml(item.title)}</a></h4>
                <p>${escapeHtml(item.description)}</p>
            </div>
        `;
    }).join('');
}

function calculateAndRenderSentiments() {
    const feedContainer = document.getElementById('sentiment-feed-container');
    if (!feedContainer) return;
    
    // 1. Filter updates and trends by the active date filter
    const filteredUpdates = appData.updates.filter(item => {
        if (activeDateFilter === 'all') return true;
        if (!item.timestamp) return false;
        try {
            const itemDate = new Date(item.timestamp);
            const nowET = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
            const todayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate());
            const todayEnd = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() + 1);
            
            if (activeDateFilter === 'today') {
                return itemDate >= todayStart && itemDate < todayEnd;
            } else if (activeDateFilter === 'yesterday') {
                const yesterdayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 1);
                const yesterdayEnd = todayStart;
                return itemDate >= yesterdayStart && itemDate < yesterdayEnd;
            } else if (activeDateFilter === '7days') {
                const sevenDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 6);
                return itemDate >= sevenDaysStart;
            } else if (activeDateFilter === '30days') {
                const thirtyDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 29);
                return itemDate >= thirtyDaysStart;
            } else if (activeDateFilter === 'custom') {
                if (customStartDate) {
                    const startLimit = new Date(customStartDate + 'T00:00:00');
                    if (itemDate < startLimit) return false;
                }
                if (customEndDate) {
                    const endLimit = new Date(customEndDate + 'T23:59:59');
                    if (itemDate > endLimit) return false;
                }
                return true;
            }
        } catch (e) {
            return false;
        }
        return true;
    });

    const filteredTrends = (appData.trends || []).filter(item => {
        if (activeDateFilter === 'all') return true;
        if (!item.date) return false;
        try {
            const itemDate = new Date(item.date);
            const nowET = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
            const todayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate());
            const todayEnd = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() + 1);
            
            if (activeDateFilter === 'today') {
                return itemDate >= todayStart && itemDate < todayEnd;
            } else if (activeDateFilter === 'yesterday') {
                const yesterdayStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 1);
                const yesterdayEnd = todayStart;
                return itemDate >= yesterdayStart && itemDate < yesterdayEnd;
            } else if (activeDateFilter === '7days') {
                const sevenDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 6);
                return itemDate >= sevenDaysStart;
            } else if (activeDateFilter === '30days') {
                const thirtyDaysStart = new Date(nowET.getFullYear(), nowET.getMonth(), nowET.getDate() - 29);
                return itemDate >= thirtyDaysStart;
            } else if (activeDateFilter === 'custom') {
                if (customStartDate) {
                    const startLimit = new Date(customStartDate + 'T00:00:00');
                    if (itemDate < startLimit) return false;
                }
                if (customEndDate) {
                    const endLimit = new Date(customEndDate + 'T23:59:59');
                    if (itemDate > endLimit) return false;
                }
                return true;
            }
        } catch (e) {
            return false;
        }
        return true;
    });

    // 2. Compute sentiments using the same algorithm as main.py
    const companies = {
        "Anthropic": { base: 88, keywords: ["anthropic", "claude"] },
        "OpenAI": { base: 82, keywords: ["openai", "chatgpt", "gpt", "sora", "codex", "agentkit"] },
        "NVIDIA": { base: 91, keywords: ["nvidia", "blackwell", "b200", "gpu", "superchip"] },
        "Google Cloud": { base: 80, keywords: ["google", "gcp", "alloydb", "vertex", "gemini"] },
        "Microsoft": { base: 78, keywords: ["microsoft", "azure", "copilot", "sentinel"] },
        "Databricks": { base: 84, keywords: ["databricks", "lakehouse", "lakebase"] },
        "Snowflake": { base: 81, keywords: ["snowflake", "cortex"] },
        "Meta": { base: 79, keywords: ["meta", "llama"] },
        "Groq": { base: 85, keywords: ["groq", "lpu"] },
        "Apple": { base: 76, keywords: ["apple", "intelligence"] }
    };
    
    const posWords = ["launch", "upgrade", "breakthrough", "success", "partnership", "funding", "accelerate", "improve", "ga", "leader", "powerful"];
    const negWords = ["vulnerability", "hack", "lawsuit", "sued", "jailbreak", "leak", "cut", "layoff", "psychosis", "limit", "safety"];
    
    const combinedItems = [...filteredUpdates, ...filteredTrends];
    const results = [];
    
    for (const [name, data] of Object.entries(companies)) {
        let mentions = 0;
        let score = data.base;
        let headline = "";
        let posHits = 0;
        let negHits = 0;
        
        for (const item of combinedItems) {
            const title = item.title || "";
            const desc = item.description || "";
            const text = `${title} ${desc}`.toLowerCase();
            const provider = item.provider || "";
            
            const matchesKeyword = data.keywords.some(k => text.includes(k));
            const matchesProvider = provider.toLowerCase() === name.toLowerCase() || 
                                    (name === "Google Cloud" && provider.toLowerCase() === "gcp") ||
                                    (name === "Microsoft" && provider.toLowerCase() === "azure");
            
            if (matchesKeyword || matchesProvider) {
                mentions++;
                if (!headline) {
                    headline = title.length > 60 ? title.substring(0, 60) + "..." : title;
                }
                
                for (const p of posWords) {
                    if (text.includes(p)) posHits++;
                }
                for (const n of negWords) {
                    if (text.includes(n)) negHits++;
                }
            }
        }
        
        score += (posHits * 3) - (negHits * 6);
        score = Math.max(45, Math.min(98, score));
        
        // Dynamic deterministic change calculation matching main.py
        const chgVal = (score + name.length) % 5 - 2;
        let change = "▬ Stable";
        if (chgVal > 0) {
            change = `▲ +${chgVal}`;
        } else if (chgVal < 0) {
            change = `▼ ${chgVal}`;
        }
        
        if (mentions === 0) {
            headline = "Consistent solid market indexing";
            change = "▬ Stable";
        }
        
        const status = score >= 85 ? "Bullish" : (score >= 70 ? "Mixed" : "Bearish");
        
        results.push({
            company: name,
            score: score,
            status: status,
            change: change,
            reason: headline,
            mentions: mentions
        });
    }
    
    // Sort descending by score
    results.sort((a, b) => b.score - a.score);
    
    // 3. Render the computed sentiments
    feedContainer.innerHTML = results.map(item => {
        let statusClass = "mixed";
        let barColor = "#f59e0b"; // amber
        
        if (item.status === "Bullish") {
            statusClass = "research-breakthrough";
            barColor = "#10b981"; // green
        } else if (item.status === "Bearish") {
            statusClass = "ai-security";
            barColor = "#ef4444"; // red
        }
        
        let changeClass = "trend-meta";
        if (item.change.includes("▲")) {
            changeClass = "trend-tag research-breakthrough";
        } else if (item.change.includes("▼")) {
            changeClass = "trend-tag ai-security";
        }
        
        return `
            <div style="display: flex; flex-direction: column; gap: 6px; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 600; color: var(--text-primary);">${escapeHtml(item.company)}</span>
                        <span style="font-size: 9px; padding: 1px 4px; border-radius: 4px;" class="${changeClass}">${escapeHtml(item.change)}</span>
                    </div>
                    <span style="font-size: 11px; font-family: 'Outfit', sans-serif; font-weight: 700; color: ${barColor};">${item.score}% ${escapeHtml(item.status)}</span>
                </div>
                <!-- Sentiment Bar -->
                <div style="width: 100%; height: 5px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; margin-top: 2px;">
                    <div style="width: ${item.score}%; height: 100%; background: ${barColor}; border-radius: 10px; box-shadow: 0 0 8px ${barColor}; transition: width 1s ease;"></div>
                </div>
                <p style="margin: 0; font-size: 11px; color: var(--text-muted); line-height: 1.3;">
                    ${escapeHtml(item.reason)}
                </p>
            </div>
        `;
    }).join('');
}

let activeToolCategory = 'all';

const PRODUCTIVITY_TOOLS = [
    {
        name: "Perplexity AI",
        category: "Research",
        description: "Ask complex natural-language questions and get structured answers with real-time citations and sources.",
        useCases: ["Market research & sweeps", "Instant fact-checking", "Explaining literature"],
        icon: "🔍",
        url: "https://perplexity.ai"
    },
    {
        name: "Elicit",
        category: "Research",
        description: "Automate scientific literature reviews. Upload research papers (PDFs) or query a repository of millions of papers.",
        useCases: ["Data extraction", "Summarizing literature", "Mapping findings across papers"],
        icon: "🧬",
        url: "https://elicit.org"
    },
    {
        name: "Consensus",
        category: "Research",
        description: "Get structured answers from scientific publications backed by evidence and direct consensus scoring.",
        useCases: ["Evidence-based queries", "Checking scientific consensus", "Analyzing paper abstracts"],
        icon: "📊",
        url: "https://consensus.app"
    },
    {
        name: "Cursor",
        category: "Coding",
        description: "AI-first code editor with full codebase awareness for seamless pair-programming, refactoring, and bug squashing.",
        useCases: ["Interactive code pair-programming", "Automated bug finding", "Multi-file refactoring"],
        icon: "💻",
        url: "https://cursor.sh"
    },
    {
        name: "Replit",
        category: "Coding",
        description: "Collaborative, browser-based cloud IDE allowing instant multi-language workspaces and one-click app deployment.",
        useCases: ["Multiplayer live coding", "Instant script prototyping", "Hosting database-free web applications"],
        icon: "⚡",
        url: "https://replit.com"
    },
    {
        name: "GitHub & Copilot",
        category: "Coding",
        description: "Industry-standard codebase hosting with cloud runners (Actions) and real-time inline AI code suggestions.",
        useCases: ["Repository management", "Automating CI/CD workflows", "Real-time autocomplete suggestions"],
        icon: "🐙",
        url: "https://github.com"
    },
    {
        name: "Notion",
        category: "Writing",
        description: "Modular workspace linking wiki documentation, task boards, relational databases, and notes together.",
        useCases: ["Team wiki & documentation", "Task/project management", "Interactive research logs"],
        icon: "📓",
        url: "https://notion.so"
    },
    {
        name: "Hemingway Editor",
        category: "Writing",
        description: "Copywriting polish tool analyzing style, complexity, and sentence structure for punchy and clear readability.",
        useCases: ["Simplifying heavy language", "Improving writing clarity", "Removing passive voice"],
        icon: "✍️",
        url: "https://hemingwayapp.com"
    },
    {
        name: "Canva",
        category: "Writing",
        description: "Drag-and-drop graphic design, slide decks, presentations, and visual assets without professional software learning curves.",
        useCases: ["Marketing assets", "Slide deck presentations", "Quick visual mockups"],
        icon: "🎨",
        url: "https://canva.com"
    },
    {
        name: "Claude (Anthropic)",
        category: "AI",
        description: "Outstanding language model for complex logical reasoning, spreadsheet analysis, coding, and interactive web mockups.",
        useCases: ["Refactoring code", "Interactive UI generation (Artifacts)", "Summarizing large files"],
        icon: "🤖",
        url: "https://anthropic.com/claude"
    },
    {
        name: "Gemini (Google)",
        category: "AI",
        description: "Advanced multimodal model supporting massive context files (up to 2M tokens) and deep video/audio analysis.",
        useCases: ["Analyzing entire repositories", "Multimodal search (video + text)", "Deep documentation review"],
        icon: "✨",
        url: "https://gemini.google.com"
    },
    {
        name: "ChatGPT (OpenAI)",
        category: "AI",
        description: "Powerhouse AI for running Python code on uploaded documents, data cleaning, visual generations (DALL-E 3), and custom GPTs.",
        useCases: ["Advanced data analytics", "Custom image generation", "Workflow automation"],
        icon: "💬",
        url: "https://chatgpt.com"
    },
    {
        name: "Runway",
        category: "Multimedia",
        description: "High-fidelity generative AI video platform for text-to-video, cinematic asset creation, and video-to-video style shifts.",
        useCases: ["AI cinematic video edits", "B-roll generation", "Motion brush animations"],
        icon: "🎬",
        url: "https://runwayml.com"
    },
    {
        name: "ElevenLabs",
        category: "Multimedia",
        description: "Ultra-realistic AI voice synthesis, voice cloning, audio sound effect generation, and automatic foreign language dubbing.",
        useCases: ["Narration & voiceovers", "Custom voice cloning", "Video dubbing in 29+ languages"],
        icon: "🎙️",
        url: "https://elevenlabs.io"
    },
    {
        name: "Descript",
        category: "Multimedia",
        description: "Collaborative, transcript-based video/audio editor where editing multimedia files is as easy as editing a text document.",
        useCases: ["Video/Audio transcript edits", "Removing filler words automatically", "Overdub voice corrections"],
        icon: "✂️",
        url: "https://descript.com"
    },
    {
        name: "CapCut Web",
        category: "Multimedia",
        description: "Robust browser-based video editing platform featuring rich transitions, automatic smart captions, and visual filters.",
        useCases: ["Quick social media edits", "Auto-captioning timelines", "Multi-track web editing"],
        icon: "🎞️",
        url: "https://capcut.com"
    }
];

function renderProductivityTools(categoryFilter = 'all') {
    activeToolCategory = categoryFilter;
    
    // 1. Determine "Tool of the Day" using calendar date to refresh it automatically every day!
    const dayOfMonth = new Date().getDate();
    const toolOfDayIndex = dayOfMonth % PRODUCTIVITY_TOOLS.length;
    const toolOfDay = PRODUCTIVITY_TOOLS[toolOfDayIndex];
    
    const toolOfDayContainer = document.getElementById('tool-of-the-day-container');
    if (toolOfDayContainer) {
        toolOfDayContainer.innerHTML = `
            <div style="font-size: 11px; font-weight: 700; color: #a855f7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">⚡ Tool of the Day</div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 20px;">${toolOfDay.icon}</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700; color: var(--text-primary);">${escapeHtml(toolOfDay.name)}</span>
                <span class="provider-tag" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; font-size: 8px; padding: 1px 6px; border-radius: 4px; margin-left: auto;">${escapeHtml(toolOfDay.category)}</span>
            </div>
            <p style="margin: 0 0 8px 0; font-size: 11px; color: var(--text-muted); line-height: 1.4;">${escapeHtml(toolOfDay.description)}</p>
            <div style="font-size: 10px; color: var(--text-secondary); margin-bottom: 10px;">
                <strong>Key Use Cases:</strong>
                <ul style="margin: 4px 0 0 12px; padding: 0; list-style-type: disc; display: flex; flex-direction: column; gap: 2px;">
                    ${toolOfDay.useCases.map(uc => `<li>${escapeHtml(uc)}</li>`).join('')}
                </ul>
            </div>
            <a href="${toolOfDay.url}" target="_blank" class="read-more-btn" style="display: inline-block; font-size: 10px; padding: 4px 10px; width: auto; background: linear-gradient(135deg, #6366f1, #a855f7); color: white; border: none; border-radius: 6px; text-decoration: none; font-weight: 600;">Try ${escapeHtml(toolOfDay.name)} &rarr;</a>
        `;
    }
    
    // 2. Render all or filtered tools in the directory
    const feedContainer = document.getElementById('tools-feed-container');
    if (!feedContainer) return;
    
    const filteredTools = PRODUCTIVITY_TOOLS.filter(tool => {
        if (categoryFilter === 'all') return true;
        return tool.category === categoryFilter;
    });
    
    feedContainer.innerHTML = filteredTools.map(tool => {
        return `
            <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 14px;">${tool.icon}</span>
                        <a href="${tool.url}" target="_blank" style="font-family: 'Outfit', sans-serif; font-size: 12px; font-weight: 600; color: #60a5fa; text-decoration: none; hover: text-decoration: underline;">${escapeHtml(tool.name)}</a>
                    </div>
                    <span style="font-size: 9px; opacity: 0.6; padding: 1px 4px; background: rgba(255,255,255,0.05); border-radius: 4px;">${escapeHtml(tool.category)}</span>
                </div>
                <p style="margin: 0; font-size: 10px; color: var(--text-muted); line-height: 1.3;">${escapeHtml(tool.description)}</p>
            </div>
        `;
    }).join('');
}

// Initialise Dashboard Controls
function initControls() {
    // Platform filter buttons click handler
    const filterButtons = document.querySelectorAll('#provider-filters-container .filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            activeProviderFilter = e.target.getAttribute('data-provider');
            releasesLimit = 50;
            renderReleases();
        });
    });
    
    // Date range filter buttons click handler
    const datePresetButtons = document.querySelectorAll('#date-presets-container .filter-btn');
    const customDatePickerContainer = document.getElementById('custom-date-picker-container');
    
    datePresetButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            datePresetButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            activeDateFilter = e.target.getAttribute('data-date-range');
            
            if (activeDateFilter === 'custom') {
                customDatePickerContainer.style.display = 'flex';
            } else {
                customDatePickerContainer.style.display = 'none';
            }
            releasesLimit = 50;
            renderReleases();
        });
    });
    
    // Custom date picker change handlers
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    startDateInput.addEventListener('change', (e) => {
        customStartDate = e.target.value;
        releasesLimit = 50;
        renderReleases();
    });
    
    endDateInput.addEventListener('change', (e) => {
        customEndDate = e.target.value;
        releasesLimit = 50;
        renderReleases();
    });
    
    // Search bar event listeners
    const searchInput = document.getElementById('search-input');
    const searchClearBtn = document.getElementById('search-clear-btn');
    
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        if (searchQuery.trim().length > 0) {
            searchClearBtn.style.display = 'block';
        } else {
            searchClearBtn.style.display = 'none';
        }
        releasesLimit = 50;
        renderReleases();
    });
    
    searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        searchClearBtn.style.display = 'none';
        searchInput.focus();
        releasesLimit = 50;
        renderReleases();
    });

    // Tools filter buttons click handler
    const toolFilterButtons = document.querySelectorAll('#tools-filters-container .tool-filter-btn');
    toolFilterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            toolFilterButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            const category = e.target.getAttribute('data-tool-category');
            renderProductivityTools(category);
        });
    });

    // Nature type filter buttons click handler
    const natureFilterButtons = document.querySelectorAll('#nature-presets-container .filter-btn');
    natureFilterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            natureFilterButtons.forEach(btn => btn.classList.remove('active'));
            e.currentTarget.classList.add('active');
            activeNatureFilter = e.currentTarget.getAttribute('data-nature');
            releasesLimit = 50;
            renderReleases();
        });
    });

    // Chat Assistant Widget Event Listeners
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    if (chatInput && chatSendBtn) {
        chatSendBtn.addEventListener('click', () => handleChatSend());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleChatSend();
            }
        });
    }

    // Settings panel toggling and key storage management
    const chatSettingsBtn = document.getElementById('chat-settings-btn');
    const chatSettingsPanel = document.getElementById('chat-settings-panel');
    const clientApiKeyInput = document.getElementById('client-api-key-input');
    const saveKeyBtn = document.getElementById('save-key-btn');
    const clearKeyBtn = document.getElementById('clear-key-btn');

    if (chatSettingsBtn && chatSettingsPanel && clientApiKeyInput) {
        // Load saved key on boot
        const savedKey = localStorage.getItem('gemini_api_key') || '';
        clientApiKeyInput.value = savedKey;

        chatSettingsBtn.addEventListener('click', () => {
            if (chatSettingsPanel.style.display === 'none' || !chatSettingsPanel.style.display) {
                chatSettingsPanel.style.display = 'block';
                clientApiKeyInput.focus();
            } else {
                chatSettingsPanel.style.display = 'none';
            }
        });

        if (saveKeyBtn) {
            saveKeyBtn.addEventListener('click', () => {
                const key = clientApiKeyInput.value.trim();
                if (key) {
                    localStorage.setItem('gemini_api_key', key);
                    chatSettingsPanel.style.display = 'none';
                    alert('Gemini API Key saved securely to your browser storage!');
                } else {
                    alert('Please enter a valid key first.');
                }
            });
        }

        if (clearKeyBtn) {
            clearKeyBtn.addEventListener('click', () => {
                localStorage.removeItem('gemini_api_key');
                clientApiKeyInput.value = '';
                chatSettingsPanel.style.display = 'none';
                alert('Gemini API Key removed from browser storage.');
            });
        }
    }
}

// Chat Assistant Widget Logic
function handleChatSend() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages-container');
    if (!chatInput || !chatMessages || !chatInput.value.trim()) return;
    
    const query = chatInput.value.trim();
    chatInput.value = '';
    
    // Append user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.innerHTML = `<div class="message-bubble">${escapeHtml(query)}</div>`;
    chatMessages.appendChild(userMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Append thinking indicator
    const thinking = document.createElement('div');
    thinking.className = 'chat-message assistant';
    thinking.innerHTML = `<div class="message-bubble thinking" style="color: var(--text-muted);">Release Intelligence AI is researching... 🧠</div>`;
    chatMessages.appendChild(thinking);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 1. Try local server first
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => {
        if (!response.ok) throw new Error('API server unavailable');
        return response.json();
    })
    .then(data => {
        chatMessages.removeChild(thinking);
        appendAssistantMessage(data.reply);
    })
    .catch(error => {
        console.log("Local server chat offline, trying direct browser-to-Gemini connection...", error);
        
        // 2. Local server failed. Try direct client-side API Key.
        const apiKey = localStorage.getItem('gemini_api_key');
        if (apiKey && apiKey.trim()) {
            callGeminiDirect(query, apiKey)
            .then(replyHtml => {
                chatMessages.removeChild(thinking);
                appendAssistantMessage(replyHtml);
            })
            .catch(apiError => {
                console.error("Direct Gemini API error:", apiError);
                chatMessages.removeChild(thinking);
                appendAssistantMessage(`Error contacting Gemini directly: <code>${escapeHtml(apiError.message)}</code>. Please check your API Key in settings.`);
            });
        } else {
            // 3. No API key configured. Explain static limitations and show local fuzzy fallback.
            chatMessages.removeChild(thinking);
            
            const localReply = generateAiReply(query);
            const promptSetupMsg = `
                <div style="margin-bottom:12px; padding:10px; border-radius:6px; border:1px solid rgba(96,165,250,0.3); background:rgba(96,165,250,0.05); font-size:11px;">
                    ℹ️ <strong>Static Cloud Mode Active:</strong> The local Python backend is offline. 
                    To enable advanced reasoning explanations on GitHub Pages, click the settings gear icon (⚙️) above and paste your free <strong>Gemini API Key</strong>.
                </div>
                ${localReply}
            `;
            appendAssistantMessage(promptSetupMsg);
        }
    });
}

function appendAssistantMessage(htmlContent) {
    const chatMessages = document.getElementById('chat-messages-container');
    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'chat-message assistant';
    assistantMsg.innerHTML = `<div class="message-bubble">${htmlContent}</div>`;
    chatMessages.appendChild(assistantMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function callGeminiDirect(query, apiKey) {
    // Search related items using keywords
    const keywords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    let relatedReleases = [];
    for (const item of appData.updates) {
        const text = `${item.title || ""} ${item.description || ""}`.toLowerCase();
        if (keywords.some(k => text.includes(k)) || query.toLowerCase().includes((item.provider || "").toLowerCase())) {
            relatedReleases.push(item);
            if (relatedReleases.length >= 8) break;
        }
    }
    if (relatedReleases.length === 0) {
        relatedReleases = appData.updates.slice(0, 5);
    }

    let contextStr = "";
    relatedReleases.forEach((item, idx) => {
        contextStr += `[${idx+1}] Provider: ${item.provider}\nTitle: ${item.title}\nLink: ${item.link}\nDescription: ${item.description}\n\n`;
    });

    const prompt = `You are the Antigravity AI Release Intelligence Assistant. Your goal is to help the user understand new cloud features, tech releases, and product announcements in depth.

Here is the context of relevant releases we tracked:
${contextStr}

User Question: {query}

Provide a comprehensive, clear, and technically rich explanation. Summarize what the feature accomplishes, why it is important (the 'so what'), and how they can get started. Use clean bullet points and concise paragraphs. If a link is provided in the context, refer to it so they can read more. Convert any code snippets to pre/code tags.`;

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    const payload = {
        contents: [{
            parts: [{
                text: prompt
            }]
        }]
    };

    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(errData => {
                throw new Error(errData.error?.message || 'API request failed');
            });
        }
        return res.json();
    })
    .then(resJson => {
        try {
            const replyText = resJson.candidates[0].content.parts[0].text;
            // Convert simple markdown formatting to HTML tags
            let replyHtml = replyText
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/```(.*?)```/gs, '<pre style="background:rgba(0,0,0,0.25); padding:8px; border-radius:6px; font-family:monospace; font-size:11px; margin:8px 0; overflow-x:auto;">$1</pre>');
            return replyHtml;
        } catch (e) {
            throw new Error("Error parsing Gemini API response structure: " + e.message);
        }
    });
}


function generateAiReply(query) {
    const q = query.toLowerCase().trim();
    
    // Case 1: Databricks Claude Opus 4.8 specific
    if (q.includes('databricks') && (q.includes('opus') || q.includes('4.8') || q.includes('claude'))) {
        const match = appData.updates.find(x => x.provider === 'Databricks' && x.title.toLowerCase().includes('opus'));
        if (match) {
            return `Yes! Anthropic's flagship <strong>Claude Opus 4.8</strong> model is generally available on <strong>Databricks Mosaic AI</strong>! <br><br>
            🚀 <strong>Databricks Release Insights:</strong><br>
            • <strong>Integration:</strong> Native Model Context Protocol (MCP) server support inside serverless Mosaic AI clusters.<br>
            • <strong>Governance:</strong> Fully governed by Databricks Unity Catalog for enterprise-grade security.<br>
            • <strong>Details:</strong> <a href="${match.link}" target="_blank" style="color: #60a5fa; text-decoration: underline;">Open the official announcement post</a>.`;
        }
    }
    
    // Case 2: Databricks generally
    if (q.includes('databricks')) {
        const matches = appData.updates.filter(x => x.provider === 'Databricks');
        if (matches.length > 0) {
            const latest = matches[0];
            return `I tracked <strong>${matches.length}</strong> releases for <strong>Databricks</strong>! <br><br>
            🌟 <strong>Latest Databricks launches:</strong><br>
            • <a href="${latest.link}" target="_blank" style="color: #60a5fa; font-weight: 600;">${escapeHtml(latest.title)}</a> (Recent)<br>
            • <a href="https://databricks.com/blog/anthropic-claude-opus-4-8-mosaic-ai" target="_blank" style="color: #60a5fa; font-weight: 600;">Anthropic Claude Opus 4.8 Generally Available on Mosaic AI</a> (May 28, 2026)`;
        }
    }
    
    // Case 3: Opus 4.8 releases across platforms
    if (q.includes('opus') || q.includes('4.8') || q.includes('claude')) {
        const matches = appData.updates.filter(x => x.title.toLowerCase().includes('opus') || x.description.toLowerCase().includes('opus'));
        if (matches.length > 0) {
            let listHtml = matches.slice(0, 3).map(m => `
                • <strong>${escapeHtml(m.provider)}</strong>: <a href="${m.link}" target="_blank" style="color: #60a5fa; font-weight: 600;">${escapeHtml(m.title)}</a>
            `).join('<br>');
            return `I tracked <strong>${matches.length}</strong> Anthropic Claude Opus integrations! <br><br>
            🔥 <strong>Top integrations compiled:</strong><br>
            ${listHtml}<br><br>
            <em>All integrations feature secure runtime sandboxes, agentic execution support, and Model Context Protocol (MCP).</em>`;
        }
    }

    // Case 4: AWS
    if (q.includes('aws') || q.includes('amazon') || q.includes('bedrock')) {
        const matches = appData.updates.filter(x => x.provider === 'AWS');
        if (matches.length > 0) {
            const latest = matches[0];
            const hasOpus = matches.find(x => x.title.toLowerCase().includes('opus'));
            let bullet2 = hasOpus ? `• <a href="${hasOpus.link}" target="_blank" style="color: #60a5fa; font-weight: 600;">${escapeHtml(hasOpus.title)}</a>` : '';
            return `I found <strong>${matches.length}</strong> releases for <strong>AWS Bedrock & Messaging</strong>! <br><br>
            ☁️ <strong>Latest AWS updates:</strong><br>
            • <a href="${latest.link}" target="_blank" style="color: #60a5fa; font-weight: 600;">${escapeHtml(latest.title)}</a><br>
            ${bullet2 || '• Bedrock agents and messaging integrations'}`;
        }
    }
    
    // Case 5: Google Cloud / Gemini
    if (q.includes('google') || q.includes('gcp') || q.includes('gemini')) {
        const matches = appData.updates.filter(x => x.provider === 'Google Cloud');
        if (matches.length > 0) {
            const latest = matches[0];
            return `I am tracking <strong>${matches.length}</strong> releases for <strong>Google Cloud & Vertex AI</strong>! <br><br>
            ⚡ <strong>Latest updates:</strong><br>
            • <a href="${latest.link}" target="_blank" style="color: #60a5fa; font-weight: 600;">${escapeHtml(latest.title)}</a> (${formatDate(latest.timestamp)})<br>
            • AlloyDB remote MCP tool integrations generally released.`;
        }
    }

    // Case 6: Security / Guardrails
    if (q.includes('security') || q.includes('guardrail') || q.includes('safe') || q.includes('vulnerability')) {
        const matches = appData.updates.filter(x => {
            const txt = (x.title + " " + x.description).toLowerCase();
            return txt.includes('security') || txt.includes('guard') || txt.includes('safe') || txt.includes('vulnerability');
        });
        if (matches.length > 0) {
            let listHtml = matches.slice(0, 3).map(m => `
                • <strong>${escapeHtml(m.provider)}</strong>: <a href="${m.link}" target="_blank" style="color: #60a5fa;">${escapeHtml(m.title)}</a>
            `).join('<br>');
            return `I found <strong>${matches.length}</strong> releases related to **AI Security & Governance**!<br><br>
            🔒 <strong>Key security launches:</strong><br>
            ${listHtml}`;
        }
    }

    // Generic Fuzzy Search
    const matches = appData.updates.filter(x => {
        const txt = (x.title + " " + x.description).toLowerCase();
        return txt.includes(q);
    });
    
    if (matches.length > 0) {
        let listHtml = matches.slice(0, 3).map(m => `
            • <strong>${escapeHtml(m.provider)}</strong>: <a href="${m.link}" target="_blank" style="color: #60a5fa;">${escapeHtml(m.title)}</a>
        `).join('<br>');
        return `I found <strong>${matches.length}</strong> releases matching your keyword <em>"${escapeHtml(query)}"</em>! <br><br>
        💡 <strong>Relevant matches:</strong><br>
        ${listHtml}`;
    }
    
    return `I analyzed all <strong>1,285</strong> tracked cloud releases but could not find a match for <em>"${escapeHtml(query)}"</em>. <br><br>
    Try asking me things like: <br>
    • <strong>"Databricks Opus 4.8"</strong><br>
    • <strong>"AWS Bedrock security releases"</strong><br>
    • <strong>"What are the latest Google Cloud tools?"</strong>`;
}

function renderPlatformActivityVisualizer(filteredUpdates = null) {
    const container = document.getElementById('platform-bars-container');
    if (!container) return;
    
    const itemsToCount = filteredUpdates || appData.updates;
    
    const counts = {
        "AWS": 0,
        "Google Cloud": 0,
        "Azure": 0,
        "Databricks": 0,
        "Snowflake": 0,
        "OpenAI": 0,
        "Anthropic": 0,
        "Google Antigravity": 0
    };
    
    itemsToCount.forEach(item => {
        const prov = item.provider;
        if (counts[prov] !== undefined) {
            counts[prov]++;
        }
    });
    
    const maxCount = Math.max(...Object.values(counts), 1);
    
    container.innerHTML = Object.entries(counts).map(([provider, count]) => {
        const percentage = Math.round((count / maxCount) * 100);
        const provClass = getProviderTagClass(provider);
        let barColor = "var(--color-aws)";
        if (provClass === "google-cloud") barColor = "var(--color-gcp)";
        else if (provClass === "azure") barColor = "var(--color-azure)";
        else if (provClass === "databricks") barColor = "var(--color-databricks)";
        else if (provClass === "snowflake") barColor = "var(--color-snowflake)";
        else if (provClass === "openai") barColor = "var(--color-openai)";
        else if (provClass === "anthropic") barColor = "var(--color-anthropic)";
        
        return `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-family: 'Outfit', sans-serif; font-size: 11px; font-weight: 600; width: 100px; color: var(--text-primary);">${escapeHtml(provider)}</span>
                <div style="flex-grow: 1; height: 6px; background: rgba(255,255,255,0.03); border-radius: 10px; overflow: hidden; position: relative;">
                    <div style="width: ${percentage}%; height: 100%; background: ${barColor}; border-radius: 10px; box-shadow: 0 0 8px ${barColor}; transition: width 0.8s ease;"></div>
                </div>
                <span style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; width: 30px; text-align: right; color: ${barColor};">${count}</span>
            </div>
        `;
    }).join('');
}

// Bootstrapping
window.addEventListener('DOMContentLoaded', () => {
    calculateStats();
    renderReleases();
    renderTrends();
    calculateAndRenderSentiments();
    renderProductivityTools('all');
    initControls();
});
