// 📊 CLASE PRINCIPAL PARA JACCARD
class JaccardAnalyzer {
    constructor() {
        this.users = {};
        this.similarities = {};
    }
    
    // Calcular similaridad de Jaccard entre dos conjuntos
    jaccardSimilarity(set1, set2) {
        if (set1.size === 0 && set2.size === 0) return 0;
        
        const intersection = new Set([...set1].filter(x => set2.has(x)));
        const union = new Set([...set1, ...set2]);
        
        return union.size === 0 ? 0 : intersection.size / union.size;
    }
    
    // Preparar datos del CSV
    prepareData(csvData) {
        this.users = {};
        
        csvData.forEach(row => {
            const userId = parseInt(row.user_id);
            const items = row.original_title;
            
            if (items && items !== 'NaN') {
                const itemList = typeof items === 'string' ? 
                    items.split(',').map(item => item.trim()).filter(item => item && item !== 'NaN') : 
                    [];
                this.users[userId] = new Set(itemList);
            }
        });
        
        return this.users;
    }
    
    // Calcular todas las similaridades
    calculateAllSimilarities(minSimilarity = 0) {
        const userIds = Object.keys(this.users).map(id => parseInt(id));
        this.similarities = {};
        
        userIds.forEach(userId => {
            this.similarities[userId] = {};
        });
        
        for (let i = 0; i < userIds.length; i++) {
            for (let j = i + 1; j < userIds.length; j++) {
                const user1 = userIds[i];
                const user2 = userIds[j];
                
                const similarity = this.jaccardSimilarity(
                    this.users[user1], 
                    this.users[user2]
                );
                
                if (similarity >= minSimilarity) {
                    this.similarities[user1][user2] = similarity;
                    this.similarities[user2][user1] = similarity;
                }
            }
        }
        
        return this.similarities;
    }
    
    // Obtener usuarios más similares
    getSimilarUsers(userId, topK = 10) {
        const userSimilarities = this.similarities[userId] || {};
        
        return Object.entries(userSimilarities)
            .map(([otherUser, similarity]) => ({
                userId: parseInt(otherUser),
                similarity: similarity
            }))
            .sort((a, b) => b.similarity - a.similarity)
            .slice(0, topK);
    }
    
    // Estadísticas generales
    getStats() {
        const allSimilarities = [];
        Object.values(this.similarities).forEach(userSims => {
            allSimilarities.push(...Object.values(userSims));
        });
        
        if (allSimilarities.length === 0) return null;
        
        const allItems = new Set();
        Object.values(this.users).forEach(userSet => {
            [...userSet].forEach(item => allItems.add(item));
        });
        
        return {
            totalUsers: Object.keys(this.users).length,
            totalItems: allItems.size,
            avgSimilarity: _.mean(allSimilarities),
            maxSimilarity: _.max(allSimilarities),
            minSimilarity: _.min(allSimilarities),
            medianSimilarity: _.median(allSimilarities)
        };
    }
}