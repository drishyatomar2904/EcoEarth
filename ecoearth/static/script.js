// Reddit-specific dashboard functionality
class EcoEarthDashboard {
    constructor() {
        this.data = null;
        this.lastUpdate = null;
        this.init();
    }

    async init() {
        await this.loadData();
        this.startAutoRefresh();
        this.updateApiStatus();
    }

    async loadData() {
        try {
            const response = await fetch('/api/dashboard-data');
            const result = await response.json();
            
            if (result.success) {
                this.data = result.data;
                this.lastUpdate = new Date();
                this.updateDashboard();
            } else {
                console.error('Failed to load data:', result.error);
                this.showError('Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Network error loading data');
        }
    }

    updateDashboard() {
        this.updateOverview();
        this.updateTrendingTopics();
        this.updateTopInfluencers();
        this.updateGroundImpact();
        this.updateAIAnalysis();
        this.updatePlatformBreakdown();
        this.updateSamplePosts();
    }

    updateOverview() {
        const overview = this.data.overview;
        document.getElementById('totalPosts').textContent = overview.total_posts.toLocaleString();
        document.getElementById('totalNews').textContent = overview.total_news.toLocaleString();
        document.getElementById('effectivenessScore').textContent = overview.effectiveness_score + '%';
        document.getElementById('positiveSentiment').textContent = overview.positive_sentiment + '%';
        document.getElementById('lastUpdated').textContent = 'Updated: ' + overview.last_updated;
        document.getElementById('dataSource').textContent = overview.data_source.toUpperCase();
    }

    updateTrendingTopics() {
        const container = document.getElementById('trendingTopics');
        const topics = this.data.trending_topics;
        
        container.innerHTML = topics.map(topic => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                <span>${topic}</span>
                <span class="badge bg-primary">r/${topic.toLowerCase().replace(' ', '')}</span>
            </div>
        `).join('');
    }

    updateTopInfluencers() {
        const container = document.getElementById('topInfluencers');
        const influencers = this.data.top_influencers;
        
        container.innerHTML = influencers.map(influencer => `
            <div class="mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong class="text-primary">${influencer.username}</strong>
                        <div class="small text-muted">${influencer.posts_count} posts</div>
                    </div>
                    <span class="badge bg-success">${influencer.impact_score}% impact</span>
                </div>
                <div class="mt-2 small">
                    <span class="text-muted">🏅 ${influencer.total_engagement.toLocaleString()} engagement</span>
                </div>
            </div>
        `).join('');
    }

    updateGroundImpact() {
        const container = document.getElementById('groundImpact');
        const impact = this.data.ground_impact;
        
        container.innerHTML = `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="text-success">
                        <strong>${impact.cleanups_triggered}</strong>
                        <div class="small">Cleanups</div>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="text-info">
                        <strong>${impact.plastic_reduced_kg}kg</strong>
                        <div class="small">Plastic Reduced</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-warning">
                        <strong>${impact.trees_planted}</strong>
                        <div class="small">Trees Planted</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-primary">
                        <strong>${impact.people_engaged}</strong>
                        <div class="small">People Engaged</div>
                    </div>
                </div>
            </div>
        `;
    }

    updateAIAnalysis() {
        const container = document.getElementById('aiAnalysis');
        const analysis = this.data.ai_analysis;
        
        container.innerHTML = `
            <div class="mb-3">
                <p class="small">${analysis.summary}</p>
            </div>
            <div class="row text-center mb-3">
                <div class="col-4">
                    <small class="text-success">${analysis.sentiment_breakdown.positive}% Positive</small>
                </div>
                <div class="col-4">
                    <small class="text-danger">${analysis.sentiment_breakdown.negative}% Negative</small>
                </div>
                <div class="col-4">
                    <small class="text-warning">${analysis.sentiment_breakdown.neutral}% Neutral</small>
                </div>
            </div>
            ${analysis.recommendations ? `
                <div class="mt-3">
                    <strong>Recommendations:</strong>
                    <ul class="small mt-2">
                        ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    updatePlatformBreakdown() {
        const container = document.getElementById('platformBreakdown');
        const breakdown = this.data.platform_breakdown;
        
        container.innerHTML = Object.entries(breakdown).map(([platform, data]) => `
            <div class="mb-3">
                <div class="d-flex justify-content-between">
                    <strong class="text-capitalize">${platform}</strong>
                    <span class="badge bg-secondary">${data.count} posts</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                    <div class="progress-bar" style="width: ${Math.min(100, data.avg_engagement / 10)}%"></div>
                </div>
                <div class="small text-muted mt-1">
                    ${data.avg_engagement} avg engagement per post
                </div>
            </div>
        `).join('');
    }

    updateSamplePosts() {
        const container = document.getElementById('samplePosts');
        const posts = this.data.sample_posts;
        
        container.innerHTML = posts.map(post => `
            <div class="mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <small class="text-muted">${post.subreddit || 'r/environment'}</small>
                    <small class="text-muted">${this.formatTime(post.timestamp)}</small>
                </div>
                <h6 class="mb-2">${post.title || post.text.substring(0, 100)}...</h6>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">by ${post.author}</small>
                    <div>
                        <span class="badge bg-success me-1">▲ ${post.upvotes}</span>
                        <span class="badge bg-secondary">💬 ${post.comments}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    async updateApiStatus() {
        try {
            const response = await fetch('/api/system/status');
            const status = await response.json();
            
            const statusElement = document.getElementById('apiStatus');
            if (status.reddit_api && status.groq_ai) {
                statusElement.className = 'badge bg-success';
                statusElement.textContent = 'All Systems Operational';
            } else if (status.reddit_api) {
                statusElement.className = 'badge bg-warning';
                statusElement.textContent = 'Limited Functionality';
            } else {
                statusElement.className = 'badge bg-danger';
                statusElement.textContent = 'Using Sample Data';
            }
        } catch (error) {
            console.error('Error checking API status:', error);
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadData();
        }, 30000); // Refresh every 30 seconds
    }

    showError(message) {
        // Simple error display - you can enhance this with a proper notification system
        console.error('Dashboard Error:', message);
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new EcoEarthDashboard();
});
