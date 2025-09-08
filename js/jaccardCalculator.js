export let jaccardSimilarity = [];

export function calculateJaccardSimilarity(userData) {
    // Inicializar matriz de similitud
    jaccardSimilarity = Array(userData.length).fill().map(() => Array(userData.length).fill(0));
    
    // Calcular similitud para cada par de usuarios
    for (let i = 0; i < userData.length; i++) {
        for (let j = i; j < userData.length; j++) {
            if (i === j) {
                jaccardSimilarity[i][j] = 1; // Máxima similitud consigo mismo
            } else {
                const setA = new Set(userData[i].titles);
                const setB = new Set(userData[j].titles);
                
                // Calcular intersección y unión
                const intersection = new Set([...setA].filter(x => setB.has(x)));
                const union = new Set([...setA, ...setB]);
                
                // Calcular similitud de Jaccard
                jaccardSimilarity[i][j] = intersection.size / union.size;
                jaccardSimilarity[j][i] = jaccardSimilarity[i][j]; // Matriz simétrica
            }
        }
    }
    
    console.log('Matriz de similitud:', jaccardSimilarity);
    return jaccardSimilarity;
}